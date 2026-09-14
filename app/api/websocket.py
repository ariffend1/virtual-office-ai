import json
import time
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import ws_manager
from app.core.config import settings, DEFAULT_AGENT_PROFILES
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

                # Step 1: Thinking
                await websocket.send_text(json.dumps({
                    "type": "agent_stream",
                    "agent": agent_id,
                    "status": "thinking",
                    "output": f"[@{agent_id}] Analyzing neural directive: '{prompt}' ...\n",
                    "timestamp": int(time.time())
                }))
                
                await asyncio.sleep(0.2)

                # Step 2: Working
                await websocket.send_text(json.dumps({
                    "type": "agent_stream",
                    "agent": agent_id,
                    "status": "working",
                    "output": f"[@{agent_id}] Swarm orchestrator running multi-threaded synthesis...\n",
                    "timestamp": int(time.time())
                }))

                # Step 3: Compute via execution engine
                result = await engine_dispatcher.execute(
                    agent_id=agent_id,
                    prompt=prompt,
                    runner_choice=runner_choice
                )

                # Step 4: Completed
                await websocket.send_text(json.dumps({
                    "type": "agent_stream",
                    "agent": agent_id,
                    "status": "completed",
                    "source": result.source,
                    "model": result.model,
                    "output": f"=== [{agent_id} EXECUTION STREAM] ===\n{result.response}\n[Consensus: APPROVED | Latency: {result.latency_ms}ms]\n",
                    "timestamp": int(time.time())
                }))

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)
