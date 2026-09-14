import json
from typing import Dict, Any, Optional, List
from app.execution.tools.base import BaseTool, ToolResult
from app.execution.tools.terminal import TerminalTool
from app.execution.tools.file_manager import FileManagerTool
from app.execution.tools.web_search import WebSearchTool

class ToolRegistry:
    """Central registry and executor for sandboxed agent tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self.register(TerminalTool())
        self.register(FileManagerTool())
        self.register(WebSearchTool())

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self._tools.values()]

    async def execute_tool(self, name: str, kwargs: Dict[str, Any]) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(
                tool_name=name,
                success=False,
                output="",
                error=f"Tool '{name}' is not registered. Available: {list(self._tools.keys())}",
                execution_time_ms=0.0
            )
        return await tool.execute(**kwargs)

    async def parse_and_execute_directive(self, prompt: str) -> Optional[ToolResult]:
        """Detects tool invocation triggers in prompt directives (e.g. tool:terminal_runner cmd=ls)."""
        prompt_lower = prompt.lower()

        # Terminal command trigger
        if "run command:" in prompt_lower or "exec:" in prompt_lower or "cmd:" in prompt_lower:
            cmd = ""
            for tag in ["run command:", "exec:", "cmd:"]:
                if tag in prompt_lower:
                    idx = prompt_lower.find(tag) + len(tag)
                    cmd = prompt[idx:].strip().split("\n")[0]
                    break
            if cmd:
                return await self.execute_tool("terminal_runner", {"command": cmd})

        # File read trigger
        if "read file:" in prompt_lower or "cat file:" in prompt_lower:
            path = ""
            for tag in ["read file:", "cat file:"]:
                if tag in prompt_lower:
                    idx = prompt_lower.find(tag) + len(tag)
                    path = prompt[idx:].strip().split()[0]
                    break
            if path:
                return await self.execute_tool("file_manager", {"action": "read", "path": path})

        # File list trigger
        if "list files" in prompt_lower or "ls dir:" in prompt_lower:
            path = "."
            if "ls dir:" in prompt_lower:
                idx = prompt_lower.find("ls dir:") + len("ls dir:")
                path = prompt[idx:].strip().split()[0]
            return await self.execute_tool("file_manager", {"action": "list", "path": path})

        # Web search trigger
        if "search web:" in prompt_lower or "search:" in prompt_lower or "lookup:" in prompt_lower:
            query = ""
            for tag in ["search web:", "search:", "lookup:"]:
                if tag in prompt_lower:
                    idx = prompt_lower.find(tag) + len(tag)
                    query = prompt[idx:].strip().split("\n")[0]
                    break
            if query:
                return await self.execute_tool("web_search", {"query": query})

        return None

tool_registry = ToolRegistry()
