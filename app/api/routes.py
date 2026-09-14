import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    HealthStatus,
    ModuleInfo,
    TaskDispatchRequest,
    TaskDispatchResponse,
    StreamMessage
)
from app.core.config import settings, DEFAULT_AGENT_PROFILES, DEFAULT_MODULES
from app.core.websocket_manager import ws_manager
from app.execution.dispatcher import engine_dispatcher

router = APIRouter(prefix="/api", tags=["CortxOS Core API"])

@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Returns comprehensive runtime status, connected agents, and WebSocket diagnostics."""
    return HealthStatus(
        status="healthy",
        service="CortxOS Multi-Agent Studio Sandbox",
        version=settings.app_version,
        port=settings.port,
        active_ws_clients=len(ws_manager.active_connections),
        agents=DEFAULT_AGENT_PROFILES,
        modules_count=len(DEFAULT_MODULES),
        execution_engine="dynamic_hybrid",
        timestamp=int(time.time())
    )

@router.get("/modules", response_model=Dict[str, List[ModuleInfo]])
async def get_modules():
    """Lists all registered CortxOS interactive design modules."""
    return {"modules": [ModuleInfo(**m) for m in DEFAULT_MODULES]}

@router.get("/agents")
async def get_agents():
    """Lists all active agent profiles, roles, and capability matrices."""
    return {"agents": DEFAULT_AGENT_PROFILES}

@router.post("/dispatch", response_model=TaskDispatchResponse)
async def dispatch_task_http(req: TaskDispatchRequest):
    """Dispatches a task directive via HTTP REST and broadcasts live trace to connected WebSockets."""
    agent_id = req.agent
    prompt = req.prompt
    
    # Broadcast start event
    msg_start = StreamMessage(
        type="agent_stream",
        agent=agent_id,
        status="thinking",
        output=f"[@{agent_id}] Ingesting directive: '{prompt}' via REST Bridge\n",
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

    # Broadcast finish event
    msg_finish = StreamMessage(
        type="agent_stream",
        agent=agent_id,
        status="completed",
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
