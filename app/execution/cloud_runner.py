import time
from typing import Dict, Any, Optional, List
import httpx
from app.execution.base import BaseAgentRunner
from app.models.schemas import ExecutionResult
from app.core.config import settings

class CloudLLMRunner(BaseAgentRunner):
    """Cloud API & Local OpenAI-compatible LLM runner supporting OmniRoute, OpenAI, and Anthropic."""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        super().__init__(name=f"cloud_{provider}")
        self.provider = provider.lower()
        if self.provider == "anthropic":
            self.api_key = api_key or settings.anthropic_api_key
            self.model = model or settings.anthropic_model
            self.base_url = "https://api.anthropic.com/v1"
        else:
            self.api_key = api_key or settings.openai_api_key
            self.model = model or settings.openai_model
            self.base_url = base_url or settings.openai_base_url
            self.fallback_url = settings.openai_fallback_url

    async def _test_endpoint(self, url: str) -> bool:
        """Probe OpenAI-compatible /v1/models or health check endpoint with quick 0.8s timeout."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            async with httpx.AsyncClient(timeout=0.8) as client:
                resp = await client.get(f"{url.rstrip('/')}/models", headers=headers)
                if resp.status_code in (200, 401):  # Server responded
                    return True
        except Exception:
            pass
        return False

    async def is_available(self) -> bool:
        if self.provider == "anthropic":
            return bool(self.api_key and len(self.api_key.strip()) > 0)
        
        # OpenAI or OmniRoute gateway
        if self.base_url.startswith("http://") or self.base_url.startswith("https://"):
            # Check primary URL
            if await self._test_endpoint(self.base_url):
                return True
            # Check fallback URL if configured
            if hasattr(self, "fallback_url") and self.fallback_url and await self._test_endpoint(self.fallback_url):
                return True
            # Or if API key is provided and points to official OpenAI
            if "openai.com" in self.base_url and bool(self.api_key and len(self.api_key.strip()) > 0):
                return True
        return False

    async def run(self, agent_id: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        start_time = time.time()

        try:
            if self.provider == "anthropic":
                if not self.api_key:
                    return ExecutionResult(
                        source=self.provider,
                        model=self.model,
                        response=f"Error: API key for Anthropic not configured.",
                        latency_ms=0.0,
                        status="error"
                    )
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
                async with httpx.AsyncClient(timeout=10.0) as client:
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
                # OpenAI / OmniRoute Gateway Execution
                target_urls = [self.base_url]
                if hasattr(self, "fallback_url") and self.fallback_url and self.fallback_url != self.base_url:
                    target_urls.append(self.fallback_url)

                headers = {
                    "Content-Type": "application/json"
                }
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                model_to_use = (context or {}).get("model") or self.model
                payload = {
                    "model": model_to_use,
                    "messages": [
                        {"role": "system", "content": f"You are {agent_id}, a specialized CortxOS autonomous agent."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }

                last_error = None
                for url in target_urls:
                    endpoint = f"{url.rstrip('/')}/chat/completions"
                    try:
                        async with httpx.AsyncClient(timeout=3.5) as client:
                            resp = await client.post(endpoint, json=payload, headers=headers)
                            if resp.status_code == 200:
                                data = resp.json()
                                text = data["choices"][0]["message"]["content"]
                                elapsed = round((time.time() - start_time) * 1000, 2)
                                usage = data.get("usage", {})
                                total_tokens = usage.get("total_tokens", len(prompt.split()) + len(text.split()))
                                return ExecutionResult(
                                    source="openai_gateway",
                                    model=model_to_use,
                                    response=text,
                                    latency_ms=elapsed,
                                    status="success",
                                    metadata={"endpoint": url, "tokens": total_tokens}
                                )
                            elif resp.status_code == 401:
                                raise RuntimeError(f"OmniRoute/OpenAI 401 Unauthorized at {url}: Check API key")
                            else:
                                last_error = f"HTTP {resp.status_code}: {resp.text}"
                    except Exception as e:
                        last_error = str(e)
                        continue

                raise RuntimeError(f"All OpenAI/OmniRoute endpoints failed. Last error: {last_error}")

        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 2)
            return ExecutionResult(
                source=self.provider,
                model=self.model,
                response=f"Cloud/Gateway LLM call failed: {str(e)}",
                latency_ms=elapsed,
                status="error",
                metadata={"error": str(e)}
            )
