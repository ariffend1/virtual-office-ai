import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from app.execution.tools.base import BaseTool, ToolResult
from app.core.config import settings

class FileManagerTool(BaseTool):
    """Sandboxed file manager tool supporting read, write, list, and stat operations."""

    def __init__(self):
        super().__init__(
            name="file_manager",
            description="Reads, writes, lists, and inspects files safely within the project root sandbox."
        )

    def _resolve_safe_path(self, relative_path: str) -> Path:
        target = (settings.base_dir / relative_path).resolve()
        # Path traversal guard
        if not str(target).startswith(str(settings.base_dir.resolve())):
            raise PermissionError(f"Access denied: path '{relative_path}' escapes sandbox root.")
        return target

    async def execute(self, action: str, path: str = ".", content: Optional[str] = None, max_depth: int = 2) -> ToolResult:
        start_time = time.time()
        action = action.lower()

        try:
            target_path = self._resolve_safe_path(path)
        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=str(e),
                execution_time_ms=0.0
            )

        try:
            if action in ("read", "cat"):
                if not target_path.exists() or not target_path.is_file():
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        output="",
                        error=f"File not found: {path}",
                        execution_time_ms=round((time.time() - start_time) * 1000, 2)
                    )
                text = target_path.read_text(encoding="utf-8", errors="ignore")
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output=text,
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )

            elif action in ("write", "create"):
                if content is None:
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        output="",
                        error="Content argument is required for write action.",
                        execution_time_ms=0.0
                    )
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(content, encoding="utf-8")
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output=f"Successfully wrote {len(content)} bytes to {path}",
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )

            elif action in ("list", "ls", "readdir"):
                if not target_path.exists() or not target_path.is_dir():
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        output="",
                        error=f"Directory not found: {path}",
                        execution_time_ms=round((time.time() - start_time) * 1000, 2)
                    )
                items = [p.relative_to(settings.base_dir).as_posix() for p in target_path.glob("*")]
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output="\n".join(items) if items else "(empty directory)",
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )

            elif action in ("stat", "info"):
                if not target_path.exists():
                    return ToolResult(
                        tool_name=self.name,
                        success=False,
                        output="",
                        error=f"Path not found: {path}",
                        execution_time_ms=round((time.time() - start_time) * 1000, 2)
                    )
                st = target_path.stat()
                info = (
                    f"Path: {path}\n"
                    f"Type: {'Directory' if target_path.is_dir() else 'File'}\n"
                    f"Size: {st.st_size} bytes\n"
                    f"Modified: {int(st.st_mtime)}"
                )
                return ToolResult(
                    tool_name=self.name,
                    success=True,
                    output=info,
                    execution_time_ms=round((time.time() - start_time) * 1000, 2)
                )

            else:
                return ToolResult(
                    tool_name=self.name,
                    success=False,
                    output="",
                    error=f"Unknown file action '{action}'. Supported: read, write, list, stat",
                    execution_time_ms=0.0
                )

        except Exception as e:
            return ToolResult(
                tool_name=self.name,
                success=False,
                output="",
                error=f"File operation failed: {str(e)}",
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
