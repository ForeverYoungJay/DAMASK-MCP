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
