import asyncio
import json
import httpx
import websockets

BASE_HTTP = "http://127.0.0.1:8899"
BASE_WS = "ws://127.0.0.1:8899/ws/stream"

async def test_health_check():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_HTTP}/api/health")
        assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["port"] == 8899
        assert "Arch-01" in data["agents"]
        assert data["modules_count"] == 10
        print("[PASS] Health Check Endpoint verified.")

async def test_modules_list():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_HTTP}/api/modules")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["modules"]) == 10
        print("[PASS] Modules API verified with 10 design modules.")

async def test_module_views():
    modules = [
        "cortxos_multi_agent_studio_neural_simulation_environment/code.html",
        "mission_dispatcher/code.html",
        "telemetry_gateway/code.html",
        "3d_workspace/code.html",
        "knowledge_graph/code.html"
    ]
    async with httpx.AsyncClient() as client:
        for mod in modules:
            resp = await client.get(f"{BASE_HTTP}/view/{mod}")
            assert resp.status_code == 200, f"Failed to load module view: {mod}"
            assert len(resp.text) > 100
        print("[PASS] Module HTML views verified.")

async def test_http_dispatch():
    async with httpx.AsyncClient() as client:
        payload = {
            "agent": "Audit-02",
            "prompt": "Verify zero-trust consensus on Raft Cluster"
        }
        resp = await client.post(f"{BASE_HTTP}/api/dispatch", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "dispatched"
        assert data["agent"] == "Audit-02"
        assert "result" in data
        assert data["result"]["status"] == "success"
        print("[PASS] HTTP Task Dispatch & Fallback LLM engine verified.")

async def test_websocket_stream_and_heartbeat():
    async with websockets.connect(BASE_WS) as ws:
        # 1. Check handshake
        handshake_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        handshake = json.loads(handshake_raw)
        assert handshake["type"] == "system_handshake"
        assert handshake["sandbox_port"] == 8899
        print("[PASS] WS System Handshake verified:", handshake["message"])

        # 2. Check telemetry heartbeat
        telemetry_raw = await asyncio.wait_for(ws.recv(), timeout=5.0)
        telemetry = json.loads(telemetry_raw)
        assert telemetry["type"] == "telemetry"
        assert "fps" in telemetry
        assert "latency_ms" in telemetry
        assert "tokens" in telemetry
        print(f"[PASS] WS Telemetry Heartbeat received: FPS={telemetry['fps']}, Latency={telemetry['latency_ms']}ms, Tokens={telemetry['tokens']}")

        # 3. Test bidirectional dispatch task
        dispatch_cmd = {
            "type": "dispatch_task",
            "agent": "Arch-01",
            "prompt": "Initialize ISO-3D shader coordinate grid and PBR lighting"
        }
        await ws.send(json.dumps(dispatch_cmd))
        
        # Expect stream updates (thinking -> working -> completed or interleaved telemetry)
        events_received = []
        for _ in range(5):
            msg_raw = await asyncio.wait_for(ws.recv(), timeout=6.0)
            msg = json.loads(msg_raw)
            if msg.type if hasattr(msg, 'type') else msg.get("type") == "agent_stream":
                events_received.append(msg)
                if msg.get("status") == "completed":
                    break
        
        statuses = [e.get("status") for e in events_received]
        assert "completed" in statuses or len(events_received) >= 1
        print("[PASS] WS Bidirectional Agent Dispatch & Streaming trace verified.")

async def run_all():
    print("=== STARTING CORTXOS RUNTIME SUITE TESTS ===")
    await test_health_check()
    await test_modules_list()
    await test_module_views()
    await test_http_dispatch()
    await test_websocket_stream_and_heartbeat()
    print("=== ALL 5 TEST SUITES PASSED CLEANLY ===")

if __name__ == "__main__":
    asyncio.run(run_all())
