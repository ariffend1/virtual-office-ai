"""
Unit & Integration Tests for WebSocket Lifecycle & Streaming Gateway
"""
import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

def test_websocket_stream_lifecycle():
    client = TestClient(app)
    with client.websocket_connect("/ws/stream") as websocket:
        # Check initial handshake message
        handshake = websocket.receive_json()
        assert handshake["type"] == "system_handshake"
        assert "Arch-01" in handshake["agents"]

        # Send ping and verify pong
        websocket.send_json({"type": "ping"})
        pong = websocket.receive_json()
        assert pong["type"] == "pong"

        # Send task dispatch directive
        websocket.send_json({
            "type": "dispatch_task",
            "agent": "Audit-02",
            "prompt": "Verify zero-trust WebSocket pipeline",
            "runner": "mock"
        })

        # Receive thinking event
        msg_think = websocket.receive_json()
        assert msg_think["type"] == "agent_stream"
        assert msg_think["status"] == "thinking"
        assert msg_think["agent"] == "Audit-02"

        # Receive working event
        msg_work = websocket.receive_json()
        assert msg_work["type"] == "agent_stream"
        assert msg_work["status"] == "working"

        # Receive completed event
        msg_done = websocket.receive_json()
        assert msg_done["type"] == "agent_stream"
        assert msg_done["status"] == "completed"
        assert "EXECUTION STREAM" in msg_done["output"]
