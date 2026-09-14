import pytest
from app.execution.dispatcher import engine_dispatcher
from app.execution.cloud_runner import CloudLLMRunner
from app.core.websocket_manager import ws_manager

@pytest.mark.asyncio
async def test_cloud_runner_offline_fallback():
    # Cloud runner with non-existent local gateway should fail or return False for availability
    runner = CloudLLMRunner(provider="openai", base_url="http://127.0.0.1:99999/v1")
    is_avail = await runner.is_available()
    assert is_avail is False

@pytest.mark.asyncio
async def test_dispatcher_gateway_graceful_fallback():
    # Calling with gateway/openai runner should gracefully fallback to mock simulation when offline
    res = await engine_dispatcher.execute(
        agent_id="Arch-01",
        prompt="Synthesize cluster telemetry",
        runner_choice="gateway"
    )
    assert res.status == "success"
    assert "Arch-01" in res.model or "NeuralEngine" in res.model
    assert len(res.response) > 0

@pytest.mark.asyncio
async def test_hardware_telemetry_collector():
    hw = ws_manager._get_hardware_metrics()
    assert "cpu_percent" in hw
    assert "ram_percent" in hw
    assert "ram_used_mb" in hw
    assert "disk_percent" in hw
    assert "active_threads" in hw
    assert hw["active_threads"] >= 1

    db_stats = ws_manager._get_db_metrics()
    assert "total_tasks" in db_stats
    assert "tokens" in db_stats
    assert "cost" in db_stats
