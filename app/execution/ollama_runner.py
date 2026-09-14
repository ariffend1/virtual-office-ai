import time
from typing import Dict, Any, Optional
import httpx
from app.execution.base import BaseAgentRunner
from app.models.schemas import ExecutionResult
from app.core.config import settings

class OllamaRunner(BaseAgentRunner):
    """Local LLM runner connecting to Ollama instance (qwen2.5-coder, llama3, deepseek, etc.)."""

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name="ollama")
        self.base_url = base_url or settings.ollama_url
        self.model = model or settings.ollama_model

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def run(self, agent_id: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                system_prompt = f"You are {agent_id}, an autonomous AI specialist in CortxOS. Execute the following directive with high precision."
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": f"{system_prompt}\n\nTask: {prompt}",
                        "stream": False
                    }
                )
                if resp.status_code == 200:
                    raw_response = resp.json().get("response", "")
                    elapsed = round((time.time() - start_time) * 1000, 2)
                    return ExecutionResult(
                        source="ollama",
                        model=self.model,
                        response=raw_response,
                        latency_ms=elapsed,
                        status="success",
                        metadata={"endpoint": self.base_url}
                    )
                else:
                    raise RuntimeError(f"Ollama returned HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return ExecutionResult(
                source="ollama",
                model=self.model,
                response=f"Ollama execution failed: {str(e)}",
                latency_ms=elapsed,
                status="error",
                metadata={"error": str(e)}
            )
