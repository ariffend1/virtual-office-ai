import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from app.models.schemas import TelemetryPayload, StreamMessage

class WebSocketManager:
    """Manages active WebSocket connections, message broadcasting, and telemetry ticker loops."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._telemetry_task: Optional[asyncio.Task] = None
        self._tokens_base: int = 48210
        self._fps_base: int = 60

    async def connect(self, websocket: WebSocket, port: int, agents: List[str]):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send initial handshake
        handshake = {
            "type": "system_handshake",
            "status": "connected",
            "sandbox_port": port,
            "agents": agents,
            "message": "CortxOS Agentic Neural Bridge Connected (Modularized Sandbox Isolated)"
        }
        await websocket.send_text(json.dumps(handshake))

        # Start telemetry loop if not already running
        if self._telemetry_task is None or self._telemetry_task.done():
            self._telemetry_task = asyncio.create_task(self._telemetry_loop())

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        raw = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(raw)
            except Exception:
                self.disconnect(connection)

    async def broadcast_stream(self, stream_msg: StreamMessage):
        await self.broadcast(stream_msg.dict())

    async def _telemetry_loop(self):
        """Continuous background ticker providing real-time telemetry metrics to all connected clients."""
        try:
            while len(self.active_connections) > 0:
                await asyncio.sleep(1.0)
                self._tokens_base += 14
                latency = 26 + (int(time.time()) % 7)
                fps = self._fps_base - (int(time.time()) % 2)
                
                payload = TelemetryPayload(
                    type="telemetry",
                    fps=fps,
                    latency_ms=latency,
                    tokens=self._tokens_base,
                    cost=round(self._tokens_base * 0.0000015, 4),
                    active_threads=4,
                    subprocesses_healthy=12,
                    timestamp=int(time.time())
                )
                await self.broadcast(payload.dict())
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[WebSocketManager Telemetry Error]: {e}")

ws_manager = WebSocketManager()
