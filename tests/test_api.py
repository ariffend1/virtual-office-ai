"""
CortxOS Multi-Agent Studio Test Suite
Async HTTP & WebSocket runner supporting both standard Python asyncio execution and pytest.
"""
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import asyncio
import json
from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_health_check_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
        data = resp.json()
        assert data["status"] == "healthy"
        assert "Arch-01" in data["agents"]
        assert data["modules_count"] == 10
        print("[PASS] Test Health Check Endpoint")

async def test_modules_list_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["modules"]) == 10
        module_ids = [m["id"] for m in data["modules"]]
        assert "studio" in module_ids
        assert "mission" in module_ids
        print("[PASS] Test Modules List Endpoint (10 Modules)")

async def test_module_html_views():
    modules = [
        "cortxos_multi_agent_studio_neural_simulation_environment/code.html",
        "mission_dispatcher/code.html",
        "telemetry_gateway/code.html",
        "3d_workspace/code.html",
        "knowledge_graph/code.html"
    ]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for mod in modules:
            resp = await client.get(f"/view/{mod}")
            assert resp.status_code == 200, f"Module view failed: {mod}"
            assert len(resp.text) > 100
        print("[PASS] Test Standalone Module HTML Views")

async def test_http_dispatch_mock():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "agent": "Audit-02",
            "prompt": "Verify zero-trust consensus on Raft Cluster",
            "runner": "mock"
        }
        resp = await client.post("/api/dispatch", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "dispatched"
        assert data["agent"] == "Audit-02"
        assert data["result"]["status"] == "success"
        assert "QUORUM_APPROVED" in data["result"]["metadata"]["consensus"]
        print("[PASS] Test HTTP Task Dispatch & Execution Engine")

async def test_index_shell_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "CortxOS" in resp.text
        assert "Live Stream Log" in resp.text
        print("[PASS] Test Unified Shell Index Page")

async def run_suite():
    print("=== STARTING CORTXOS MODULAR BACKEND TESTS ===")
    await test_health_check_endpoint()
    await test_modules_list_endpoint()
    await test_module_html_views()
    await test_http_dispatch_mock()
    await test_index_shell_page()
    print("=== ALL TESTS PASSED CLEANLY ===")

if __name__ == "__main__":
    asyncio.run(run_suite())
