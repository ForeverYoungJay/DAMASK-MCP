# DAMASK MCP

Standalone FastMCP servers for DAMASK preprocessing, validation, execution, and post-processing workflows.

DAMASK MCP exposes a curated DAMASK workflow surface to MCP clients. It wraps common operations such as YAML generation, geometry preparation, simulation setup validation, controlled `DAMASK_grid` execution, result inspection, and lightweight post-processing.

## Status

This project is ready for local MCP use and public release-candidate testing. The runner tools depend on a working DAMASK solver installation, so hosted deployments should verify solver availability before exposing execution tools.

## Features

- DAMASK installation and API inspection
- Preprocessing and YAML generation
- Simulation input validation
- Workspace-restricted `DAMASK_grid` execution
- Result inspection, VTK export, and stress-strain extraction
- Miscellaneous table, utility, and regular-grid helpers

The unified server registers 69 MCP tools.

## Install

Create or activate a Python environment with DAMASK support, then install this project. Do not rely on the system `python` or `python3` unless that interpreter can import `damask` and can see the `DAMASK_grid` executable.

```bash
python -m pip install -e ".[dev]"
```

The adapter prefers an installed `damask` Python package. If this repository also contains a local `damask-3.0.2/python` source tree, it will fall back to that automatically.

If you already have a Conda environment for DAMASK, install from the repository root. Replace `<DAMASK_CONDA_ENV>` with the user's actual environment name:

```bash
conda activate <DAMASK_CONDA_ENV>
python -m pip install -e ".[dev]"
```

Verify that Python imports this checkout, not another editable install:

```bash
python -c "import damask_mcp, damask_mcp.adapter; print(damask_mcp.__file__); print(damask_mcp.adapter.__file__)"
```

Both paths should point inside this repository.

For a complete local setup guide, see:

- [docs/local_user_setup.md](./docs/local_user_setup.md)

That guide includes the exact values to enter in a "Connect to a custom MCP" STDIO install form.

## Run

Unified server:

```bash
damask-mcp
```

Equivalent module entrypoint:

```bash
python -m damask_mcp.mcp_servers.damask_server
```

FastMCP direct entrypoint:

```bash
fastmcp run server.py:mcp
```

FastMCP deployment config:

```bash
fastmcp inspect fastmcp.json
fastmcp run fastmcp.json --skip-env
```

The root-level `fastmcp.json` uses `streamable-http` on `127.0.0.1:8081/mcp`, matching hosted FastMCP proxy runners that wait for a local HTTP MCP endpoint.

By default, generated inputs and outputs are written under `workspaces/` in the MCP process current working directory. In local STDIO installs, this is the "Working directory" field. In hosted runtimes, if that directory is read-only, DAMASK MCP falls back to `/tmp/damask-mcp/workspaces`. Set `DAMASK_MCP_WORKSPACES` to a writable mounted directory when persistent storage is available.

Runner tools require a `DAMASK_grid` executable in the MCP runtime, not only the `damask` Python package. Put `DAMASK_grid` on `PATH` or set `DAMASK_GRID_EXECUTABLE` to its absolute path. The `find_damask_executables` tool reports every probe it tried, the selected executable, environment hints, and setup guidance; ask users to run it first when solver execution is unavailable.

For local desktop users, the recommended pattern is to start the MCP with `conda run -n <env> ...`, where `<env>` is the same Conda environment that contains both the `damask` Python package and `DAMASK_grid`.

Recommended runtime environment:

```bash
export DAMASK_MCP_WORKSPACES=/absolute/path/to/DAMASK-MCP/workspaces
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

Hosted runtimes that only provide `/tmp` as writable storage can use:

```bash
export DAMASK_MCP_RUNTIME_DIR=/tmp/damask-mcp
export DAMASK_MCP_WORKSPACES=/tmp/damask-mcp/workspaces
```

## Remote Conda Deployment

Yes, this MCP can be deployed inside a Conda environment. The important rule is that the Conda environment must live on the remote server or container that runs the MCP process. A user's local Conda environment is not visible to a remote HTTP MCP deployment.

One typical remote setup is:

```bash
conda create -n damask-mcp python=3.11
conda activate damask-mcp
python -m pip install -e ".[dev]"
python -c "import damask; print(damask.__version__)"
which DAMASK_grid || echo "Set DAMASK_GRID_EXECUTABLE"
```

Then run the STDIO server from that environment:

```bash
conda run --no-capture-output -n damask-mcp python -m damask_mcp.mcp_servers.damask_server
```

For an HTTP FastMCP deployment, run the repository entrypoint from the same Conda environment:

```bash
export DAMASK_MCP_RUNTIME_DIR=/tmp/damask-mcp
export DAMASK_MCP_WORKSPACES=/tmp/damask-mcp/workspaces
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
export MCP_BEARER_TOKEN=<shared-secret-token>
conda run --no-capture-output -n damask-mcp fastmcp run fastmcp.json --skip-env
```

If the platform provides persistent storage, prefer a mounted path such as `/data/workspaces` for `DAMASK_MCP_WORKSPACES`.

## Client Config Examples

Example client configs are included here:

- [examples/codex.mcp.toml](./examples/codex.mcp.toml)
- [examples/claude_desktop_config.json](./examples/claude_desktop_config.json)

Update the placeholder absolute paths before using them. The examples set `PYTHONPATH` to this repository's `src/` directory to avoid accidentally loading another editable install. They also show `DAMASK_MCP_WORKSPACES` and `DAMASK_GRID_EXECUTABLE`, which are the two important settings for reproducible solver runs.

For hosted HTTP installation with `https://DAMASK-MCP.fastmcp.app/mcp`, bearer token, and optional headers, see:

- [docs/remote_fastmcp_install.md](./docs/remote_fastmcp_install.md)

For remote deployments, the person deploying the MCP server must configure DAMASK on that remote runtime. Connector users only provide the URL and token; their local Conda environment is not visible to the remote server.

## Verification

Run these commands before opening a release or deployment:

```bash
python -m pytest tests
fastmcp inspect fastmcp.json
python -c "import damask; print(damask.__version__)"
```

Expected local baseline:

- `pytest`: all tests pass
- `fastmcp inspect`: server name `damask`, 69 tools
- `damask`: import succeeds

## Architecture

Main adapter package:

- `src/damask_mcp/adapter/`

Server and workflow helper package:

- `src/damask_mcp/`

Unified server:

- `src/damask_mcp/mcp_servers/damask_server.py`

Split servers remain available for finer-grained registration:

- `src/damask_mcp/mcp_servers/damask_core_server.py`
- `src/damask_mcp/mcp_servers/damask_preprocess_server.py`
- `src/damask_mcp/mcp_servers/damask_validation_server.py`
- `src/damask_mcp/mcp_servers/damask_runner_server.py`
- `src/damask_mcp/mcp_servers/damask_postprocess_server.py`
- `src/damask_mcp/mcp_servers/damask_misc_server.py`

Top-level hosted/local entrypoint:

```text
server.py:mcp
```

## Safety Rules

- MCP tools return JSON-serializable dictionaries.
- Material and generic load builders require explicit user-provided model parameters; they do not assume elastic constants, plasticity laws, lattices, or default deformation gradients.
- Cubic Hooke materials (`cP`, `cI`, `cF`) must provide `C_11`, `C_12`, and `C_44`; `C_11` alone is rejected.
- File reads and writes are restricted to `workspaces/`.
- Runner subprocess calls do not use `shell=True`.
- Large arrays are summarized instead of returned directly.
- Result-mutating post-processing tools are restricted to workspace-local files.

## DAMASK APIs Wrapped

The adapter uses confirmed DAMASK APIs including:

- `damask.ConfigMaterial`
- `damask.YAML`
- `damask.LoadcaseGrid`
- `damask.GeomGrid`
- `damask.Rotation`
- `damask.Result`
- `damask.seeds.from_random`
- `damask.mechanics`
- `damask.tensor`

## Tool Groups

Core:

- `check_damask_installation`
- `get_damask_version`
- `list_damask_modules`
- `inspect_damask_class`
- `inspect_damask_function`

Pre-processing:

- `create_simple_tension_load_yaml`
- `create_simple_compression_load_yaml`
- `create_load_yaml_from_template`
- `create_material_yaml`
- `create_material_yaml_from_template`
- `validate_yaml_file`
- `create_empty_material_yaml`
- `inspect_material_yaml`
- `validate_material_yaml`
- `add_material_entry`
- `create_random_orientations`
- `convert_euler_to_quaternion`
- `convert_quaternion_to_euler`
- `create_random_seeds`
- `create_voronoi_grid`
- `inspect_grid`
- `scale_grid`
- `renumber_grid`
- `clean_grid`

Validation:

- `validate_material_yaml_structure`
- `validate_load_yaml_structure`
- `inspect_geometry_material_indices`
- `check_phase_homogenization_consistency`
- `check_orientation_format`
- `check_required_plasticity_parameters`
- `check_material_indices`
- `validate_simulation_setup`

Runner:

- `find_damask_executables`
- `run_damask_grid`
- `list_workspace_files`
- `collect_result_files`

Post-processing:

- `inspect_result_file`
- `list_result_data`
- `list_result_increments`
- `list_result_fields`
- `add_strain`
- `add_equivalent_mises`
- `add_deviator`
- `add_spherical`
- `add_gradient`
- `add_divergence`
- `add_curl`
- `export_result_vtk`
- `extract_volume_average`
- `extract_stress_strain_curve`

Miscellaneous:

- `load_table`
- `inspect_table`
- `get_table_column`
- `rename_table_column`
- `sort_table_by`
- `inspect_dream3d_base_group`
- `inspect_dream3d_cell_data_group`
- `miller_to_bravais`
- `bravais_to_miller`
- `grid_point_to_node`
- `grid_node_to_point`
- `grid_ravel`
- `grid_unravel`
- `validate_regular_grid_coordinates`

## Hosted Deployment

If you want to publish this MCP over HTTP, use the included minimal Horizon deployment checklist:

- [docs/horizon_minimal_deploy.md](./docs/horizon_minimal_deploy.md)

Confirm whether the hosted runtime has a working `damask` Python package and a `DAMASK_grid` executable before enabling runner workflows.

For hosted deployments, the most reliable configuration is an absolute solver path:

```bash
export DAMASK_GRID_EXECUTABLE=/absolute/path/to/DAMASK_grid
```

The diagnostic tool checks `DAMASK_GRID_EXECUTABLE`, `PATH`, the active Python environment `bin/` directory, `CONDA_PREFIX/bin`, and common local DAMASK source-build paths.

## License

This project is distributed under the MIT License. DAMASK itself is a separate dependency distributed under its own license; check the installed DAMASK package and comply with its license terms when using or redistributing DAMASK-backed workflows.
