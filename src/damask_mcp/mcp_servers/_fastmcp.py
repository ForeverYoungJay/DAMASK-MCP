"""FastMCP compatibility helpers for DAMASK MCP servers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

try:
    from fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[no-redef]
    except ImportError:
        @dataclass(frozen=True)
        class _FallbackTool:
            name: str
            description: str | None = None


        class FastMCP:  # type: ignore[no-redef]
            """Minimal fallback used when FastMCP is not installed in the test environment."""

            def __init__(self, name: str, *args: Any, **kwargs: Any) -> None:
                self.name = name
                self._tools: list[Callable[..., Any]] = []
                self._mounted: list[tuple["FastMCP", str | None]] = []

            def tool(self, *args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
                def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
                    self.add_tool(fn)
                    return fn

                return decorator

            def add_tool(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Callable[..., Any]:
                del args, kwargs
                if fn not in self._tools:
                    self._tools.append(fn)
                return fn

            async def list_tools(self) -> list[_FallbackTool]:
                return [_FallbackTool(name=tool.__name__, description=tool.__doc__) for tool in self._tools]

            def mount(
                self,
                server: "FastMCP",
                namespace: str | None = None,
                as_proxy: bool | None = None,
                tool_names: dict[str, str] | None = None,
                prefix: str | None = None,
            ) -> None:
                del as_proxy, tool_names
                self._mounted.append((server, namespace or prefix))

            def run(self, *args: Any, **kwargs: Any) -> None:
                del args, kwargs
                raise RuntimeError(
                    "FastMCP is not installed. Install the MCP SDK dependencies to run the DAMASK MCP servers."
                )


__all__ = ["FastMCP"]
