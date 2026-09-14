import asyncio
from typing import Dict, Any, Optional
from app.execution.base import BaseAgentRunner
from app.execution.mock_runner import MockNeuralRunner
from app.execution.ollama_runner import OllamaRunner
from app.execution.cloud_runner import CloudLLMRunner
from app.models.schemas import ExecutionResult

class EngineDispatcher:
    """Intelligent dispatcher resolving runner strategy (Ollama -> Cloud -> Mock Neural Simulation)."""

    def __init__(self):
        self.mock_runner = MockNeuralRunner()
        self.ollama_runner = OllamaRunner()
        self.openai_runner = CloudLLMRunner(provider="openai")
        self.anthropic_runner = CloudLLMRunner(provider="anthropic")

    async def execute(
        self,
        agent_id: str,
        prompt: str,
        runner_choice: str = "auto",
        context: Optional[Dict[str, Any]] = None
    ) -> ExecutionResult:
        runner_choice = runner_choice.lower()
        
        # Explicit runner overrides
        if runner_choice == "ollama":
            return await self.ollama_runner.run(agent_id, prompt, context)
        elif runner_choice == "openai":
            return await self.openai_runner.run(agent_id, prompt, context)
        elif runner_choice == "anthropic":
            return await self.anthropic_runner.run(agent_id, prompt, context)
        elif runner_choice == "mock":
            return await self.mock_runner.run(agent_id, prompt, context)

        # 'auto' strategy: 1. Try Ollama -> 2. Try OpenAI/Anthropic (if keys set) -> 3. High-speed Mock Neural Sim
        if await self.ollama_runner.is_available():
            res = await self.ollama_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        if await self.openai_runner.is_available():
            res = await self.openai_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        if await self.anthropic_runner.is_available():
            res = await self.anthropic_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        # Deterministic simulation fallback
        return await self.mock_runner.run(agent_id, prompt, context)

engine_dispatcher = EngineDispatcher()
