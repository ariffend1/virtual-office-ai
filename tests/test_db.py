"""
Unit & Integration Tests for SQLite Database Models & CRUD Endpoints
"""
import pytest
import asyncio
from sqlmodel import Session, select
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.db import engine, init_db
from app.models.db_models import AgentDB, TaskDB, DAGExecutionLogDB, TokenUsageHistoryDB

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

@pytest.mark.asyncio
async def test_db_agent_seeding_and_crud():
    with Session(engine) as session:
        agents = session.exec(select(AgentDB)).all()
        assert len(agents) >= 4
        agent_ids = [a.id for a in agents]
        assert "Arch-01" in agent_ids

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get list of agents
        res = await client.get("/api/agents")
        assert res.status_code == 200
        data = res.json()
        assert "Arch-01" in data["agents"]

        # Get specific agent
        res = await client.get("/api/agents/Arch-01")
        assert res.status_code == 200
        assert res.json()["id"] == "Arch-01"

        # Create/Update agent
        new_agent = {
            "id": "TestAgent-99",
            "name": "TestAgent 99",
            "role": "Testing",
            "color": "#123456",
            "capabilities": ["unit_testing"],
            "status": "ready"
        }
        res = await client.post("/api/agents", json=new_agent)
        assert res.status_code == 200
        assert res.json()["id"] == "TestAgent-99"

@pytest.mark.asyncio
async def test_db_task_persistence_and_tokens():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Dispatch task
        dispatch_payload = {
            "agent": "Audit-02",
            "prompt": "Verify Byzantine consensus",
            "runner": "mock"
        }
        res = await client.post("/api/dispatch", json=dispatch_payload)
        assert res.status_code == 200

        # Verify task recorded in DB via GET /api/tasks
        res = await client.get("/api/tasks")
        assert res.status_code == 200
        tasks = res.json()["tasks"]
        assert len(tasks) > 0
        assert tasks[0]["agent_id"] == "Audit-02"

        # Verify token history recorded in DB via GET /api/tokens/history
        res = await client.get("/api/tokens/history")
        assert res.status_code == 200
        tokens_data = res.json()
        assert tokens_data["total_tokens"] > 0

@pytest.mark.asyncio
async def test_db_dag_logs():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        log_payload = {
            "mission_id": "helios-01",
            "phase_id": "PHASE_01",
            "phase_name": "AST Codebase Index",
            "agent_id": "Arch-01",
            "status": "completed",
            "payload_diff": "+ const x = 1;",
            "duration_s": 1.25
        }
        res = await client.post("/api/dag/logs", json=log_payload)
        assert res.status_code == 200
        assert res.json()["mission_id"] == "helios-01"

        # List DAG logs
        res = await client.get("/api/dag/logs?mission_id=helios-01")
        assert res.status_code == 200
        logs = res.json()["logs"]
        assert len(logs) > 0
        assert logs[0]["phase_id"] == "PHASE_01"
