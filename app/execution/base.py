import abc
import time
from typing import Dict, Any, Optional
from app.models.schemas import ExecutionResult

class BaseAgentRunner(abc.ABC):
    """Abstract base class for all CortxOS Agent execution runners (Local, Ollama, Cloud, Mock)."""

    def __init__(self, name: str):
        self.name = name

    @abc.abstractmethod
    async def run(self, agent_id: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """Executes a prompt for a given agent and returns a typed ExecutionResult."""
        pass

    @abc.abstractmethod
    async def is_available(self) -> bool:
        """Returns True if the backend runtime/endpoint is available and healthy."""
        pass
