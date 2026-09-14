import time
from typing import Dict, Any, Optional
import httpx
from app.execution.base import BaseAgentRunner
from app.models.schemas import ExecutionResult
from app.core.config import settings

class CloudLLMRunner(BaseAgentRunner):
    """Cloud API LLM runner supporting OpenAI compatible endpoints & Anthropic Claude."""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None):
        super().__init__(name=f"cloud_{provider}")
        self.provider = provider.lower()
        if self.provider == "anthropic":
            self.api_key = api_key or settings.anthropic_api_key
            self.model = model or settings.anthropic_model
        else:
            self.api_key = api_key or settings.openai_api_key
            self.model = model or settings.openai_model

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 0)

    async def run(self, agent_id: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        start_time = time.time()
        
        if not await self.is_available():
            return ExecutionResult(
                source=self.provider,
                model=self.model,
                response=f"Error: API key for {self.provider} not configured.",
                latency_ms=0.0,
                status="error"
            )

        try:
            if self.provider == "anthropic":
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": f"Agent: {agent_id}\nDirective: {prompt}"}]
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data.get("content", [{}])[0].get("text", "")
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        return ExecutionResult(
                            source="anthropic",
                            model=self.model,
                            response=text,
                            latency_ms=elapsed,
                            status="success"
                        )
                    else:
                        raise RuntimeError(f"Anthropic returned {resp.status_code}: {resp.text}")
            else:
                # Default OpenAI Compatible
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": f"You are {agent_id}, a specialized CortxOS agent."},
                        {"role": "user", "content": prompt}
                    ]
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"]
                        elapsed = round((time.time() - start_time) * 1000, 2)
                        return ExecutionResult(
                            source="openai",
                            model=self.model,
                            response=text,
                            latency_ms=elapsed,
                            status="success"
                        )
                    else:
                        raise RuntimeError(f"OpenAI returned {resp.status_code}: {resp.text}")
        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return ExecutionResult(
                source=self.provider,
                model=self.model,
                response=f"Cloud LLM call failed: {str(e)}",
                latency_ms=elapsed,
                status="error",
                metadata={"error": str(e)}
            )
