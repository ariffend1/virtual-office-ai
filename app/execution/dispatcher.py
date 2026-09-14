import asyncio
from typing import Dict, Any, Optional
from app.execution.base import BaseAgentRunner
from app.execution.mock_runner import MockNeuralRunner
from app.execution.ollama_runner import OllamaRunner
from app.execution.cloud_runner import CloudLLMRunner
from app.execution.tools.registry import tool_registry
from app.models.schemas import ExecutionResult

class EngineDispatcher:
    """Intelligent dispatcher resolving runner strategy and real tool execution with graceful neural fallback."""

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

        # Check if directive contains a real sandboxed tool invocation
        tool_result = await tool_registry.parse_and_execute_directive(prompt)
        if tool_result:
            status_str = "success" if tool_result.success else "error"
            output_body = tool_result.output if tool_result.success else (tool_result.error or "Tool execution failed")
            return ExecutionResult(
                source=f"tool:{tool_result.tool_name}",
                model=f"{agent_id}-SandboxedRunner",
                response=f"[TOOL EXECUTION TRACE - {tool_result.tool_name}]\n{output_body}",
                latency_ms=tool_result.execution_time_ms,
                status=status_str,
                metadata={"tool": tool_result.tool_name, "success": tool_result.success}
            )

        # Explicit runner overrides
        if runner_choice == "ollama":
            res = await self.ollama_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res
            # If explicit ollama fails, return result or fallback
            return res
        elif runner_choice in ("openai", "gateway", "omniroute"):
            res = await self.openai_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res
            # Fallback to mock if requested gateway is offline
            mock_res = await self.mock_runner.run(agent_id, prompt, context)
            mock_res.metadata["fallback_from"] = runner_choice
            mock_res.metadata["gateway_error"] = res.response
            return mock_res
        elif runner_choice == "anthropic":
            res = await self.anthropic_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res
            mock_res = await self.mock_runner.run(agent_id, prompt, context)
            mock_res.metadata["fallback_from"] = runner_choice
            return mock_res
        elif runner_choice == "mock":
            return await self.mock_runner.run(agent_id, prompt, context)

        # 'auto' strategy:
        # 1. Try OpenAI/OmniRoute gateway (if available)
        if await self.openai_runner.is_available():
            res = await self.openai_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        # 2. Try Ollama (if available)
        if await self.ollama_runner.is_available():
            res = await self.ollama_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        # 3. Try Anthropic (if available)
        if await self.anthropic_runner.is_available():
            res = await self.anthropic_runner.run(agent_id, prompt, context)
            if res.status == "success":
                return res

        # 4. High-speed deterministic neural simulation fallback
        return await self.mock_runner.run(agent_id, prompt, context)

engine_dispatcher = EngineDispatcher()
