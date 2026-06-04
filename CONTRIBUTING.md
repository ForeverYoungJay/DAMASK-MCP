# Contributing

Thanks for helping improve DAMASK MCP.

## Development Setup

Use Python 3.10 or newer in an environment where the `damask` Python package can be installed:

```bash
python -m pip install -e ".[dev]"
```

Before submitting changes, run:

```bash
python -m pytest tests
fastmcp inspect fastmcp.json
```

## Pull Request Guidelines

- Keep tool changes scoped to one workflow area when possible.
- Add or update tests for new MCP tool behavior.
- Keep file writes restricted to `workspaces/`.
- Avoid returning large arrays directly from tools; return summaries or exported files.
- Document new user-facing tools in `README.md` and `src/damask_mcp/adapter/api_registry.py`.

## Compatibility

The public server/helper namespace is `damask_mcp`. The adapter package is `damask_mcp.adapter`.

If a change depends on a specific DAMASK version or solver binary behavior, note that in the pull request.
