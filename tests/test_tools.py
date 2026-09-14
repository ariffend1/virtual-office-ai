"""
Unit & Integration Tests for Sandboxed Tools & Tool Registry
"""
import pytest
from app.execution.tools.terminal import TerminalTool
from app.execution.tools.file_manager import FileManagerTool
from app.execution.tools.web_search import WebSearchTool
from app.execution.tools.registry import tool_registry
from app.execution.dispatcher import engine_dispatcher

@pytest.mark.asyncio
async def test_terminal_tool_allowed_and_blocked():
    tool = TerminalTool()

    # Allowed safe command
    res = await tool.execute(command="echo 'CortxOS Tools Test'")
    assert res.success is True
    assert "CortxOS Tools Test" in res.output

    # Blocked unauthorized command binary
    res = await tool.execute(command="unauthorized_binary_cmd")
    assert res.success is False
    assert "Unauthorized command" in res.error

    # Blocked dangerous pattern
    res = await tool.execute(command="rm -rf /")
    assert res.success is False
    assert "blocked pattern" in res.error

@pytest.mark.asyncio
async def test_file_manager_tool():
    tool = FileManagerTool()

    # Read existing file
    res = await tool.execute(action="read", path="requirements.txt")
    assert res.success is True
    assert "fastapi" in res.output.lower()

    # Stat existing file
    res = await tool.execute(action="stat", path="README.md")
    assert res.success is True
    assert "Size:" in res.output

    # List root dir
    res = await tool.execute(action="list", path=".")
    assert res.success is True
    assert "requirements.txt" in res.output

    # Path traversal block
    res = await tool.execute(action="read", path="../../../etc/passwd")
    assert res.success is False
    assert "escapes sandbox root" in res.error

@pytest.mark.asyncio
async def test_web_search_tool():
    tool = WebSearchTool()
    res = await tool.execute(query="Multi-Agent Architecture")
    assert res.success is True
    assert "Multi-Agent Architecture" in res.output

@pytest.mark.asyncio
async def test_tool_registry_and_dispatcher_integration():
    # Registry tool lookup
    assert tool_registry.get_tool("terminal_runner") is not None
    assert len(tool_registry.list_tools()) == 3

    # Dispatcher directive tool execution
    res = await engine_dispatcher.execute("Arch-01", "cmd: echo 'Hello Dispatcher Tools'")
    assert res.status == "success"
    assert "tool:terminal_runner" in res.source
    assert "Hello Dispatcher Tools" in res.response
