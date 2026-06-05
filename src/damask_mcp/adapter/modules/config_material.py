"""Higher-level ConfigMaterial wrappers."""

from __future__ import annotations

from typing import Any

from damask_mcp.adapter.modules.material_tools import inspect_material_yaml, validate_material_yaml
from damask_mcp.adapter.validators import ensure_workspace_write_path
from damask_mcp.adapter.workspace import import_damask


def validate_elastic_parameters(lattice: str, elastic: dict[str, Any]) -> None:
    """Reserved hook for elastic parameter validation without material-specific defaults."""
    del lattice, elastic


def create_material_yaml(
    path: str,
    material_name: str,
    phase_name: str,
    lattice: str,
    elastic: dict[str, Any],
    plastic: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a basic DAMASK material.yaml file with one phase and one constituent."""
    if not lattice:
        raise ValueError("lattice is required; DAMASK MCP does not assume a material lattice.")
    if not isinstance(elastic, dict) or not elastic:
        raise ValueError("elastic must be a non-empty DAMASK elastic parameter mapping.")
    validate_elastic_parameters(lattice, elastic)
    output_path = ensure_workspace_write_path(path)
    damask = import_damask()
    phase_data: dict[str, Any] = {
        "lattice": lattice,
        "mechanical": {"elastic": elastic},
    }
    if plastic is not None:
        phase_data["mechanical"]["plastic"] = plastic
    config = damask.ConfigMaterial(
        {
            "homogenization": {material_name: {"N_constituents": 1}},
            "phase": {phase_name: phase_data},
            "material": [
                {
                    "homogenization": material_name,
                    "constituents": [{"phase": phase_name, "O": [1.0, 0.0, 0.0, 0.0], "v": 1.0}],
                }
            ],
        }
    )
    config.save(output_path)
    inspected = inspect_material_yaml(str(output_path))
    inspected["created_from"] = {
        "material_name": material_name,
        "phase_name": phase_name,
        "lattice": lattice,
        "has_plastic": plastic is not None,
    }
    return inspected


def create_material_yaml_from_template(
    path: str,
    homogenization: dict[str, Any],
    phase: dict[str, Any],
    material: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a DAMASK material.yaml from an explicit template."""
    output_path = ensure_workspace_write_path(path)
    damask = import_damask()
    config = damask.ConfigMaterial(
        {
            "homogenization": homogenization,
            "phase": phase,
            "material": material,
        }
    )
    config.save(output_path)
    inspected = inspect_material_yaml(str(output_path))
    inspected["created_from"] = {
        "mode": "template",
        "homogenization_count": len(homogenization),
        "phase_count": len(phase),
        "material_count": len(material),
    }
    return inspected


__all__ = [
    "create_material_yaml",
    "create_material_yaml_from_template",
    "inspect_material_yaml",
    "validate_elastic_parameters",
    "validate_material_yaml",
]
