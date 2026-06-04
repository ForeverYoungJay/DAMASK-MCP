# Local User Setup

This guide is for users running DAMASK MCP on their own computer.

## Core Rule

Run the MCP server inside the same environment that can use DAMASK.

That environment must provide both:

- the `damask` Python package
- the `DAMASK_grid` solver executable

The system `python` or `python3` is not enough unless it satisfies both checks.

## Find the Working DAMASK Environment

If DAMASK is installed in Conda, first find the environment:

```bash
conda env list
```

Then check the candidate environment. Replace `<DAMASK_CONDA_ENV>` with the actual environment name from `conda env list`:

```bash
conda run -n <DAMASK_CONDA_ENV> python -c "import damask; print(damask.__version__)"
conda run -n <DAMASK_CONDA_ENV> which DAMASK_grid
```

If these commands work, use that same environment to run DAMASK MCP.

## Install DAMASK MCP Into That Environment

From the repository root:

```bash
conda run -n <DAMASK_CONDA_ENV> python -m pip install -e ".[dev]"
```

Do not install into a different Python environment and then run MCP from another one.

## Use a Local Workspace

By default, DAMASK MCP writes generated files under:

```text
<DAMASK-MCP>/workspaces/
```

For a local desktop setup, this is usually the best choice because the MCP process and the user's shell can both inspect the same files.

If a client or deployment uses a read-only application directory such as `/app`, configure a writable local path:

```bash
export DAMASK_MCP_WORKSPACES=/absolute/path/to/DAMASK-MCP/workspaces
```

DAMASK MCP does not fall back to `/tmp`. If the workspace root cannot be created, it reports an error and asks for `DAMASK_MCP_WORKSPACES`.

## Configure the Solver Path

If `DAMASK_grid` is not visible on `PATH` inside the MCP process, set it explicitly:

```bash
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

For a Conda environment, it often looks like:

```bash
export DAMASK_GRID_EXECUTABLE=/path/to/miniconda3/envs/<DAMASK_CONDA_ENV>/bin/DAMASK_grid
```

Use the user's actual Conda path and environment name.

## MCP Client Pattern

The client should start MCP through Conda, not through the system Python:

```text
command = "conda"
args = [
  "run",
  "--no-capture-output",
  "-n",
  "<DAMASK_CONDA_ENV>",
  "python",
  "-m",
  "damask_mcp.mcp_servers.damask_server"
]
```

The environment should include:

```text
PYTHONPATH=/absolute/path/to/DAMASK-MCP/src
DAMASK_MCP_WORKSPACES=/absolute/path/to/DAMASK-MCP/workspaces
DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

See the files under `examples/` for complete client snippets.

## Custom MCP Install UI

If the client shows a "Connect to a custom MCP" form, use the STDIO tab for a local desktop setup.

Name:

```text
damask
```

Command to launch:

```text
conda
```

Arguments, one item per row:

```text
run
--no-capture-output
-n
<DAMASK_CONDA_ENV>
python
-m
damask_mcp.mcp_servers.damask_server
```

Environment variables:

```text
PYTHONPATH=/absolute/path/to/DAMASK-MCP/src
DAMASK_MCP_WORKSPACES=/absolute/path/to/DAMASK-MCP/workspaces
DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

Working directory:

```text
/absolute/path/to/DAMASK-MCP
```

Environment variable passthrough is optional. Use it only for variables that already exist in the user's shell and should be forwarded into the MCP process. For reproducible installs, prefer explicit environment variables in the form.

If the user prefers not to depend on `conda` being discoverable, they can launch the environment Python directly:

Command to launch:

```text
/path/to/miniconda3/envs/<DAMASK_CONDA_ENV>/bin/python
```

Arguments:

```text
-m
damask_mcp.mcp_servers.damask_server
```

## Verify From MCP

After connecting the MCP client, run these MCP tools:

```text
check_damask_installation
find_damask_executables
create_workspace
```

`find_damask_executables` should report a non-null `selected` path.

## Common Problems

`/app/workspaces` is read-only:

Set `DAMASK_MCP_WORKSPACES` to a writable local directory. Local users should normally use `<DAMASK-MCP>/workspaces`.

MCP can import `damask` but cannot find `DAMASK_grid`:

Set `DAMASK_GRID_EXECUTABLE` to the absolute solver path, or start MCP with `conda run -n <env>` where `<env>` contains `DAMASK_grid`.

The shell can run `DAMASK_grid`, but MCP cannot:

The shell and MCP are running in different environments. Put the solver path in `DAMASK_GRID_EXECUTABLE` inside the MCP client config.

`python` is missing or cannot import `damask`:

Use `conda run -n <env> python ...` instead of the system `python`.
