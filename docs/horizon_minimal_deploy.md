# Horizon Minimal Deploy Checklist

Use this checklist when you want to publish `DAMASK-MCP` to a public or team-accessible FastMCP URL through Prefect Horizon.

## Minimum Inputs

- A GitHub repository containing this project.
- A FastMCP entrypoint that Horizon can load.
- A dependency file such as `pyproject.toml` or `requirements.txt`.

This repo already has:

- Entrypoint: `server.py:mcp`
- FastMCP config: `fastmcp.json`
- Dependencies: `pyproject.toml`

## Minimal Steps

1. Push the repository to GitHub.
2. Confirm the server loads locally:
   ```bash
   conda run -n <DAMASK_CONDA_ENV> python -c "import asyncio; from server import mcp; print(mcp.name, len(asyncio.run(mcp.list_tools())))"
   ```
3. Sign in to Prefect Horizon with GitHub.
4. Create a new Horizon project from the `DAMASK-MCP` repository.
5. Set the entrypoint to `server.py:mcp`.
6. Let Horizon detect and install dependencies from `pyproject.toml`.
7. Deploy and verify the generated `/mcp` endpoint.

## Recommended Before Public Release

- Confirm whether the hosted runtime will have a working `damask` Python package.
- Confirm whether the hosted runtime will have access to a `DAMASK_grid` executable if you want runner tools enabled.
- Set `DAMASK_MCP_WORKSPACES` to a writable mounted directory if generated inputs must be inspected or reused outside the MCP process.
- Set `DAMASK_GRID_EXECUTABLE` to the absolute solver path when `DAMASK_grid` is not discoverable on `PATH`.
- Set `MCP_BEARER_TOKEN` when the public HTTP endpoint should require `Authorization: Bearer <token>`.
- Decide whether to expose all tools or trim the public surface later.
- Add any required secrets as Horizon environment variables rather than hardcoding them.

## Public Release Caveat

Preprocess and validation tools will generally work wherever the `damask` Python package is installed. Runner tools may still require solver binaries and filesystem/runtime constraints that are different from local desktop usage.
