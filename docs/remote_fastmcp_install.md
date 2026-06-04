# Remote FastMCP Install

Use this guide when installing a hosted DAMASK MCP endpoint such as:

```text
https://DAMASK-MCP.fastmcp.app/mcp
```

## FastMCP Install Fields

Use the Streamable HTTP tab for a hosted DAMASK MCP server.

Name:

```text
damask
```

URL:

```text
https://DAMASK-MCP.fastmcp.app/mcp
```

Bearer token env var:

```text
MCP_BEARER_TOKEN
```

Headers:

```text
Authorization: Bearer <token>
```

Headers from environment variables:

```text
Authorization: Bearer ${MCP_BEARER_TOKEN}
```

If the install UI has a dedicated "Bearer token env var" field, prefer that field and enter `MCP_BEARER_TOKEN`. Do not also hardcode the token in a static header.

Environment variables and working directory fields are only for STDIO/local launches. They do not configure a remote hosted server after it has already started. Configure hosted runtime variables in the hosting provider instead.

## Server Behavior

DAMASK MCP enables bearer authentication only when the server process has:

```bash
export MCP_BEARER_TOKEN=<token>
```

When this environment variable is absent, the server remains unauthenticated for local development.

When it is present, clients must send:

```text
Authorization: Bearer <same token>
```

## Local Runtime Variables Are Still Separate

`MCP_BEARER_TOKEN` only protects the HTTP MCP endpoint. It does not configure DAMASK itself.

For solver workflows, the server runtime also needs:

```bash
export DAMASK_MCP_WORKSPACES=/absolute/path/to/DAMASK-MCP/workspaces
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

For local desktop users, run the MCP inside the Conda environment that can import `damask` and see `DAMASK_grid`.
