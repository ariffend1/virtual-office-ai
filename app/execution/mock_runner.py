import time
from typing import Dict, Any, Optional
from app.execution.base import BaseAgentRunner
from app.models.schemas import ExecutionResult
from app.core.config import DEFAULT_AGENT_PROFILES

class MockNeuralRunner(BaseAgentRunner):
    """Deterministic, simulated neural engine runner for high-speed offline sandbox testing & preview."""

    def __init__(self):
        super().__init__(name="mock_neural_engine")

    async def is_available(self) -> bool:
        return True

    async def run(self, agent_id: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        start_time = time.time()
        profile = DEFAULT_AGENT_PROFILES.get(agent_id, DEFAULT_AGENT_PROFILES["Arch-01"])
        
        fallback_plans = [
            f"1. Validating execution envelope for '{prompt}' under sandbox isolation.",
            f"2. Interfacing with {profile['name']} ({profile['role']}).",
            f"3. Running multi-agent consensus validation across Raft Quorum [Audit-02 + Search-03 + Astra-04].",
            f"4. Generating pipeline state change: Task parsed, memory synced, state: VERIFIED_READY.",
            f"5. Result: Autonomous task completed with zero-latency telemetry stream."
        ]
        
        elapsed = round((time.time() - start_time) * 1000 + 42.0, 2)
        
        return ExecutionResult(
            source="simulated_neural_engine",
            model=f"{agent_id}-NeuralSim-v2.4",
            response="\n".join(fallback_plans),
            latency_ms=elapsed,
            status="success",
            metadata={"agent_role": profile["role"], "consensus": "QUORUM_APPROVED"}
        )
