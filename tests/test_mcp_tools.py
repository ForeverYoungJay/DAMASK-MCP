from damask_mcp.mcp_servers import (
    damask_server,
    damask_core_server,
    damask_misc_server,
    damask_postprocess_server,
    damask_preprocess_server,
    damask_runner_server,
    damask_validation_server,
)
from damask_mcp.adapter.api_registry import list_registered_servers
import asyncio


def test_server_tool_docstrings_exist():
    assert damask_core_server.check_damask_installation.__doc__
    assert damask_server.describe_damask_mcp.__doc__
    assert damask_preprocess_server.create_empty_material_yaml.__doc__
    assert damask_preprocess_server.create_material_yaml_from_template.__doc__
    assert damask_validation_server.validate_simulation_setup.__doc__
    assert damask_postprocess_server.inspect_result_file.__doc__
    assert damask_misc_server.inspect_table.__doc__
    assert damask_runner_server.run_damask_grid.__doc__


def test_server_registry_lists_validation_and_unified_servers():
    result = list_registered_servers()

    assert result["ok"] is True
    assert "validation" in result["servers"]
    assert "unified" in result["servers"]


def test_unified_server_lists_registered_tools_with_fastmcp():
    tools = asyncio.run(damask_server.mcp.list_tools())

    assert damask_server.mcp.name == "damask"
    assert len(tools) == 69
    assert {tool.name for tool in tools} >= {"describe_damask_mcp", "create_load_yaml_from_template"}


def test_runner_server_forwards_run_damask_grid_keyword_arguments(monkeypatch):
    captured = {}

    def fake_run_damask_grid_impl(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(damask_runner_server, "run_damask_grid_impl", fake_run_damask_grid_impl)

    result = damask_runner_server.run_damask_grid(
        workspace="demo",
        geometry="geometry.vti",
        load="load.yaml",
        material="material.yaml",
        numerics="numerics.yaml",
        timeout_seconds=123,
    )

    assert result == {"ok": True}
    assert captured == {
        "workspace": "demo",
        "geometry": "geometry.vti",
        "load": "load.yaml",
        "material": "material.yaml",
        "numerics": "numerics.yaml",
        "timeout_seconds": 123,
    }


def test_create_workspace_returns_structured_error(monkeypatch):
    def fake_resolve_workspace_dir(name):
        raise RuntimeError("workspace root is read-only")

    monkeypatch.setattr(damask_preprocess_server, "resolve_workspace_dir", fake_resolve_workspace_dir)

    result = damask_preprocess_server.create_workspace("demo")

    assert result["ok"] is False
    assert result["name"] == "demo"
    assert "DAMASK_MCP_WORKSPACES" in result["hint"]
