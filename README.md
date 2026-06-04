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

Create or activate a Python environment with DAMASK support, then install this project:

```bash
python -m pip install -e ".[dev]"
```

The adapter prefers an installed `damask` Python package. If this repository also contains a local `damask-3.0.2/python` source tree, it will fall back to that automatically.

If you already have a Conda environment such as `damaskcp`, install from the repository root:

```bash
conda activate damaskcp
python -m pip install -e ".[dev]"
```

Verify that Python imports this checkout, not another editable install:

```bash
python -c "import damask_mcp, damask_mcp.adapter; print(damask_mcp.__file__); print(damask_mcp.adapter.__file__)"
```

Both paths should point inside this repository.

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

## Client Config Examples

Example client configs are included here:

- [examples/codex.mcp.toml](./examples/codex.mcp.toml)
- [examples/claude_desktop_config.json](./examples/claude_desktop_config.json)

Update the placeholder absolute paths before using them. The examples set `PYTHONPATH` to this repository's `src/` directory to avoid accidentally loading another editable install.

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
- File writes are restricted to `workspaces/`.
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

## License

This project is distributed under the MIT License. DAMASK itself is a separate dependency distributed under its own license; check the installed DAMASK package and comply with its license terms when using or redistributing DAMASK-backed workflows.
