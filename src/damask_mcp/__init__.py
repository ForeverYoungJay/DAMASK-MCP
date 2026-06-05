"""DAMASK MCP package."""

from damask_mcp.runtime import configure_runtime_environment

configure_runtime_environment()

__all__ = [
    "__version__",
]

__version__ = "0.1.0"
