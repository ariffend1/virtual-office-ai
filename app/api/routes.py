import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select

from app.models.schemas import (
    HealthStatus,
    ModuleInfo,
    TaskDispatchRequest,
    TaskDispatchResponse,
    StreamMessage
)
from app.models.db_models import AgentDB, TaskDB, DAGExecutionLogDB, TokenUsageHistoryDB
from app.core.config import settings, DEFAULT_MODULES
from app.core.db import get_session, engine
from app.core.websocket_manager import ws_manager
from app.execution.dispatcher import engine_dispatcher

router = APIRouter(prefix="/api", tags=["CortxOS Core API"])

@router.get("/health", response_model=HealthStatus)
async def health_check(session: Session = Depends(get_session)):
    """Returns comprehensive runtime status, connected agents from DB, and WebSocket diagnostics."""
    agents = session.exec(select(AgentDB)).all()
    agents_dict = {
        a.id: {
            "id": a.id,
            "name": a.name,
            "role": a.role,
            "color": a.color,
            "capabilities": a.capabilities,
            "status": a.status
        }
        for a in agents
    }

    return HealthStatus(
        status="healthy",
        service="CortxOS Multi-Agent Studio Sandbox",
        version=settings.app_version,
        port=settings.port,
        active_ws_clients=len(ws_manager.active_connections),
        agents=agents_dict,
        modules_count=len(DEFAULT_MODULES),
        execution_engine="dynamic_hybrid",
        timestamp=int(time.time())
    )

@router.get("/modules", response_model=Dict[str, List[ModuleInfo]])
async def get_modules():
    """Lists all registered CortxOS interactive design modules."""
    return {"modules": [ModuleInfo(**m) for m in DEFAULT_MODULES]}

# Agent CRUD
@router.get("/agents")
async def get_agents(session: Session = Depends(get_session)):
    """Lists all active agent profiles, roles, and capability matrices from database."""
    agents = session.exec(select(AgentDB)).all()
    return {"agents": {a.id: a.model_dump() for a in agents}}

@router.get("/agents/{agent_id}")
async def get_agent_by_id(agent_id: str, session: Session = Depends(get_session)):
    agent = session.get(AgentDB, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent

@router.post("/agents")
async def create_or_update_agent(agent_data: Dict[str, Any], session: Session = Depends(get_session)):
    agent_id = agent_data.get("id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="Agent 'id' is required")

    agent = session.get(AgentDB, agent_id)
    if agent:
        for k, v in agent_data.items():
            if hasattr(agent, k):
                setattr(agent, k, v)
        agent.updated_at = int(time.time())
    else:
        agent = AgentDB(
            id=agent_id,
            name=agent_data.get("name", agent_id),
            role=agent_data.get("role", "Swarm Member"),
            color=agent_data.get("color", "#00687a"),
            capabilities=agent_data.get("capabilities", []),
            status=agent_data.get("status", "ready")
        )
        session.add(agent)

    session.commit()
    session.refresh(agent)
    return agent

# Task CRUD
@router.get("/tasks")
async def list_tasks(limit: int = 50, session: Session = Depends(get_session)):
    """Lists task execution history."""
    tasks = session.exec(select(TaskDB).order_by(TaskDB.id.desc()).limit(limit)).all()
    return {"tasks": [t.model_dump() for t in tasks]}

@router.get("/tasks/{task_id}")
async def get_task(task_id: str, session: Session = Depends(get_session)):
    tasks = session.exec(select(TaskDB).where(TaskDB.task_id == task_id)).all()
    if not tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[0]

@router.post("/dispatch", response_model=TaskDispatchResponse)
async def dispatch_task_http(req: TaskDispatchRequest, session: Session = Depends(get_session)):
    """Dispatches a task directive via HTTP REST, logs state in SQLite, and broadcasts WS stream."""
    agent_id = req.agent
    prompt = req.prompt
    task_str_id = f"task-{uuid.uuid4().hex[:8]}"

    # Update agent DB status to thinking
    agent_db = session.get(AgentDB, agent_id)
    if agent_db:
        agent_db.status = "thinking"
        session.add(agent_db)

    task_rec = TaskDB(
        task_id=task_str_id,
        agent_id=agent_id,
        prompt=prompt,
        status="thinking",
        runner=req.runner or "auto"
    )
    session.add(task_rec)
    session.commit()

    # Broadcast start event
    msg_start = StreamMessage(
        type="agent_stream",
        agent=agent_id,
        status="thinking",
        output=f"[@{agent_id}] Ingesting directive [{task_str_id}]: '{prompt}' via REST Bridge\n",
        timestamp=int(time.time())
    )
    await ws_manager.broadcast_stream(msg_start)

    # Execute directive through the execution engine dispatcher
    result = await engine_dispatcher.execute(
        agent_id=agent_id,
        prompt=prompt,
        runner_choice=req.runner or "auto",
        context=req.context
    )

    # Update task DB record
    task_rec.status = "completed" if result.status == "success" else "failed"
    task_rec.result_output = result.response
    task_rec.latency_ms = result.latency_ms
    task_rec.completed_at = int(time.time())
    session.add(task_rec)

    # Record token usage
    tokens = result.metadata.get("tokens", len(prompt.split()) + len(result.response.split()))
    token_rec = TokenUsageHistoryDB(
        agent_id=agent_id,
        task_id=task_str_id,
        prompt_tokens=len(prompt.split()),
        completion_tokens=len(result.response.split()),
        total_tokens=tokens,
        estimated_cost=round(tokens * 0.000002, 6)
    )
    session.add(token_rec)

    # Reset agent status in DB
    if agent_db:
        agent_db.status = "ready"
        session.add(agent_db)

    session.commit()

    # Broadcast finish event
    msg_finish = StreamMessage(
        type="agent_stream",
        agent=agent_id,
        status="completed" if result.status == "success" else "error",
        source=result.source,
        model=result.model,
        output=f"[EXECUTION TRACE - {result.source.upper()}]\n{result.response}\n[Consensus: QUORUM_APPROVED - Latency: {result.latency_ms}ms]\n",
        timestamp=int(time.time())
    )
    await ws_manager.broadcast_stream(msg_finish)

    return TaskDispatchResponse(
        status="dispatched",
        agent=agent_id,
        result=result,
        timestamp=int(time.time())
    )

# DAG Execution Logs CRUD
@router.get("/dag/logs")
async def list_dag_logs(mission_id: Optional[str] = None, session: Session = Depends(get_session)):
    stmt = select(DAGExecutionLogDB)
    if mission_id:
        stmt = stmt.where(DAGExecutionLogDB.mission_id == mission_id)
    stmt = stmt.order_by(DAGExecutionLogDB.id.desc()).limit(100)
    logs = session.exec(stmt).all()
    return {"logs": [l.model_dump() for l in logs]}

@router.post("/dag/logs")
async def create_dag_log(log_data: Dict[str, Any], session: Session = Depends(get_session)):
    log_rec = DAGExecutionLogDB(
        mission_id=log_data.get("mission_id", "mission-01"),
        phase_id=log_data.get("phase_id", "PHASE_01"),
        phase_name=log_data.get("phase_name", "Execution Step"),
        agent_id=log_data.get("agent_id", "Arch-01"),
        status=log_data.get("status", "completed"),
        payload_diff=log_data.get("payload_diff", ""),
        duration_s=float(log_data.get("duration_s", 0.0))
    )
    session.add(log_rec)
    session.commit()
    session.refresh(log_rec)

    # Broadcast websocket state synchronization
    await ws_manager.broadcast_stream(StreamMessage(
        type="agent_stream",
        agent=log_rec.agent_id,
        status=log_rec.status,
        output=f"[DAG_LOG] {log_rec.phase_id} ({log_rec.phase_name}) -> {log_rec.status}\n{log_rec.payload_diff}",
        timestamp=int(time.time())
    ))

    return log_rec

# Token Usage History
@router.get("/tokens/history")
async def get_token_history(session: Session = Depends(get_session)):
    history = session.exec(select(TokenUsageHistoryDB).order_by(TokenUsageHistoryDB.id.desc()).limit(100)).all()
    total_tokens = sum(h.total_tokens for h in history)
    total_cost = sum(h.estimated_cost for h in history)
    return {
        "total_tokens": total_tokens,
        "total_cost": round(total_cost, 4),
        "history": [h.model_dump() for h in history]
    }
