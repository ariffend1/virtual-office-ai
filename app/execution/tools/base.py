import abc
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ToolResult(BaseModel):
    tool_name: str
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: float = 0.0

class BaseTool(abc.ABC):
    """Abstract base class for CortxOS sandboxed execution tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Executes the tool with given arguments safely."""
        pass
