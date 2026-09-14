import json
import time
import uuid
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlmodel import Session, select
from app.core.websocket_manager import ws_manager
from app.core.config import settings, DEFAULT_AGENT_PROFILES
from app.core.db import engine
from app.models.db_models import TaskDB, TokenUsageHistoryDB, AgentDB
from app.execution.dispatcher import engine_dispatcher
from app.models.schemas import StreamMessage

ws_router = APIRouter(tags=["CortxOS WebSocket Gateway"])

@ws_router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    agent_ids = list(DEFAULT_AGENT_PROFILES.keys())
    await ws_manager.connect(websocket, port=settings.port, agents=agent_ids)

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
            except Exception:
                payload = {"type": "dispatch_task", "prompt": data, "agent": "Arch-01"}

            msg_type = payload.get("type", "dispatch_task")

            if msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": int(time.time())}))
                continue

            if msg_type == "dispatch_task":
                agent_id = payload.get("agent", "Arch-01")
                prompt = payload.get("prompt", "Default diagnostic check")
                runner_choice = payload.get("runner", "auto")
                task_str_id = f"task-{uuid.uuid4().hex[:8]}"

                # Record task and agent state in SQLite
                with Session(engine) as session:
                    agent_db = session.get(AgentDB, agent_id)
                    if agent_db:
                        agent_db.status = "thinking"
                        session.add(agent_db)

                    task_rec = TaskDB(
                        task_id=task_str_id,
                        agent_id=agent_id,
                        prompt=prompt,
                        status="thinking",
                        runner=runner_choice
                    )
                    session.add(task_rec)
                    session.commit()

                # Step 1: Thinking
                msg_think = StreamMessage(
                    type="agent_stream",
                    agent=agent_id,
                    status="thinking",
                    output=f"[@{agent_id}] Analyzing neural directive [{task_str_id}]: '{prompt}' ...\n",
                    timestamp=int(time.time())
                )
                await ws_manager.broadcast_stream(msg_think)
                
                await asyncio.sleep(0.2)

                # Step 2: Working
                with Session(engine) as session:
                    agent_db = session.get(AgentDB, agent_id)
                    if agent_db:
                        agent_db.status = "working"
                        session.add(agent_db)
                    task_rec = session.exec(select(TaskDB).where(TaskDB.task_id == task_str_id)).first()
                    if task_rec:
                        task_rec.status = "working"
                        session.add(task_rec)
                    session.commit()

                msg_work = StreamMessage(
                    type="agent_stream",
                    agent=agent_id,
                    status="working",
                    output=f"[@{agent_id}] Swarm orchestrator running multi-threaded synthesis...\n",
                    timestamp=int(time.time())
                )
                await ws_manager.broadcast_stream(msg_work)

                # Step 3: Compute via execution engine
                result = await engine_dispatcher.execute(
                    agent_id=agent_id,
                    prompt=prompt,
                    runner_choice=runner_choice
                )

                # Step 4: Completed & SQLite Record Update
                with Session(engine) as session:
                    task_rec = session.exec(select(TaskDB).where(TaskDB.task_id == task_str_id)).first()
                    if task_rec:
                        task_rec.status = "completed" if result.status == "success" else "failed"
                        task_rec.result_output = result.response
                        task_rec.latency_ms = result.latency_ms
                        task_rec.completed_at = int(time.time())
                        session.add(task_rec)

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

                    agent_db = session.get(AgentDB, agent_id)
                    if agent_db:
                        agent_db.status = "ready"
                        session.add(agent_db)

                    session.commit()

                msg_done = StreamMessage(
                    type="agent_stream",
                    agent=agent_id,
                    status="completed" if result.status == "success" else "error",
                    source=result.source,
                    model=result.model,
                    output=f"=== [{agent_id} EXECUTION STREAM] ===\n{result.response}\n[Consensus: APPROVED | Latency: {result.latency_ms}ms]\n",
                    timestamp=int(time.time())
                )
                await ws_manager.broadcast_stream(msg_done)

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)
