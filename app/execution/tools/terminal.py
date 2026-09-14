import asyncio
import time
import shlex
from typing import List, Optional
from app.execution.tools.base import BaseTool, ToolResult
from app.core.config import settings

class TerminalTool(BaseTool):
    """Sandboxed terminal command execution tool with allowed command whitelist & timeout."""

    ALLOWED_COMMANDS = {
        "ls", "cat", "pwd", "echo", "git", "python", "python3", "pip", "pytest", "head", "tail", "grep", "find", "wc"
    }

    BLOCKED_PATTERNS = [
        "rm -rf", "sudo", "chmod 777", "mkfs", "dd ", "> /dev/", ":(){ :|:& };:"
    ]

    def __init__(self):
        super().__init__(
            name="terminal_runner",
            description="Executes safe CLI terminal commands within the sandboxed project environment."
        )

    async def execute(self, command: str, timeout: float = 10.0) -> ToolResult:
        start_time = time.time()

        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in command:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output="",
                    error=f"Command rejected: contains blocked pattern '{pattern}'",
                    execution_time_ms=0.0
                )

        # Parse command binary name
        try:
            tokens = shlex.split(command)
            binary = tokens[0] if tokens else ""
            if binary.startswith("./") or binary.startswith("../"):
                binary = binary.split("/")[-1]
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Command parsing error: {str(e)}",
                execution_time_ms=0.0
            )

        if binary not in self.ALLOWED_COMMANDS:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Unauthorized command binary '{binary}'. Allowed: {sorted(list(self.ALLOWED_COMMANDS))}",
                execution_time_ms=0.0
            )

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(settings.base_dir)
            )

            stdout_data, stderr_data = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            elapsed = round((time.time() - start_time) * 1000, 2)

            stdout_str = stdout_data.decode("utf-8", errors="ignore")
            stderr_str = stderr_data.decode("utf-8", errors="ignore")

            if proc.returncode == 0:
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output=stdout_str if stdout_str else "(command executed with no output)",
                    error=stderr_str if stderr_str else None,
                    execution_time_ms=elapsed
                )
            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output=stdout_str,
                    error=f"Exit code {proc.returncode}: {stderr_str}",
                    execution_time_ms=elapsed
                )

        except asyncio.TimeoutError:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Execution timed out after {timeout} seconds.",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"Terminal execution error: {str(e)}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
