"""Unified FastMCP server exposing the DAMASK workflow toolchain."""

from __future__ import annotations

from typing import Any

from damask_mcp.adapter.api_registry import SERVER_REGISTRY, list_registered_servers
from damask_mcp.mcp_servers._fastmcp import FastMCP
from damask_mcp.mcp_servers.auth import auth_provider_from_environment
from damask_mcp.mcp_servers import (
    damask_core_server,
    damask_misc_server,
    damask_postprocess_server,
    damask_preprocess_server,
    damask_runner_server,
    damask_validation_server,
)

mcp = FastMCP("damask", auth=auth_provider_from_environment())

_SERVER_MODULES = {
    "core": damask_core_server,
    "preprocess": damask_preprocess_server,
    "validation": damask_validation_server,
    "runner": damask_runner_server,
    "postprocess": damask_postprocess_server,
    "misc": damask_misc_server,
}


def _register_group_tools() -> None:
    """Register split-server tool callables on the unified FastMCP server."""
    for group_name, module in _SERVER_MODULES.items():
        for tool_name in SERVER_REGISTRY[group_name]["tools"]:
            mcp.add_tool(getattr(module, tool_name))


_register_group_tools()


@mcp.tool()
def describe_damask_mcp() -> dict[str, Any]:
    """Describe the registered DAMASK MCP server groups and their tools."""
    return list_registered_servers()


def create_server() -> FastMCP:
    """Create the unified DAMASK FastMCP server."""
    return mcp


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
