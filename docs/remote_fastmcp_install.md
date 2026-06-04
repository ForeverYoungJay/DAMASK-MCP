# Remote FastMCP Install

Use this guide when installing a hosted DAMASK MCP endpoint such as:

```text
https://DAMASK-MCP.fastmcp.app/mcp
```

## FastMCP Install Fields

Use the Streamable HTTP tab for a hosted DAMASK MCP server.

This form is for connector users. It only tells the client how to reach an already-running remote MCP server. It does not install DAMASK, set `DAMASK_grid`, or choose a workspace on that remote server.

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

## Who Configures DAMASK?

There are two separate roles:

- Connector users enter the URL and token in the install form.
- MCP deployers configure the remote runtime that serves that URL.

For a URL like:

```text
https://DAMASK-MCP.fastmcp.app/mcp
```

all tool calls execute on the server behind that URL. They do not execute on the connector user's laptop. The remote server cannot see the user's local Conda environment or local `DAMASK_grid`.

The deployer must ensure the hosted runtime has:

```bash
python -c "import damask; print(damask.__version__)"
which DAMASK_grid
```

If `which DAMASK_grid` does not work in the hosted runtime, set:

```bash
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

The deployer should verify from the MCP client by running:

```text
check_damask_installation
find_damask_executables
```

`find_damask_executables` should return a non-null `selected` path before runner tools are advertised as fully working.

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
export DAMASK_MCP_WORKSPACES=/writable/path/workspaces
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

Do not point `DAMASK_MCP_WORKSPACES` at `/app/workspaces` unless `/app` is writable in the hosting environment. On many hosted platforms, `/app` is the read-only application directory.

For local desktop users, run the MCP inside the Conda environment that can import `damask` and see `DAMASK_grid`.
