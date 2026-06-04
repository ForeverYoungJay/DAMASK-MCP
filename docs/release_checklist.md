# Release Checklist

Use this checklist before tagging or publishing DAMASK MCP.

## Local Verification

- `python -m pip install -e ".[dev]"`
- `python -m pytest tests`
- `python -c "import asyncio; from server import mcp; print(mcp.name, len(asyncio.run(mcp.list_tools())))"`
- `python -c "import damask; print(damask.__version__)"`

## Repository Readiness

- README installation and client examples are current.
- `LICENSE`, `CONTRIBUTING.md`, and `SECURITY.md` are present.
- New tools are listed in `README.md` and `src/damask_mcp/adapter/api_registry.py`.
- No generated files, caches, local workspaces, or secrets are tracked.
- Dependency and DAMASK license notes are still accurate.

## Deployment Readiness

- Hosted runtime can import `damask`.
- Hosted runtime has `DAMASK_grid` if runner tools are enabled.
- Runner timeout and workspace storage limits are appropriate.
- Public MCP surface has been reviewed for tools that mutate files or execute solver binaries.
