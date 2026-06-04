"""Deterministic builders for DAMASK YAML-like inputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from damask_mcp.mcp_clients.damask_preprocess_client import DAMASKPreprocessClient


def build_material_yaml(spec: dict[str, Any], output_path: str) -> str:
    """Build a material.yaml from explicit material data.

    This helper intentionally avoids material-specific elastic or plastic defaults.
    Provide either full DAMASK ``homogenization``/``phase``/``material`` mappings or
    the minimal single-phase inputs ``phase_name``, ``lattice``, and ``elastic``.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    phase_name = spec.get("phase_name", spec.get("material_system", "phase_0"))
    homogenization_name = spec.get("homogenization_name", "homogenization_0")
    orientation = spec.get("orientation", [1.0, 0.0, 0.0, 0.0])
    volume_fraction = float(spec.get("volume_fraction", 1.0))

    material_entries = spec.get("material", spec.get("material_entries"))
    if not material_entries:
        material_entries = [
            {
                "homogenization": homogenization_name,
                "constituents": [
                    {
                        "phase": phase_name,
                        "O": orientation,
                        "v": volume_fraction,
                    }
                ],
            }
        ]

    phase = spec.get("phase")
    if phase is None:
        if "lattice" not in spec:
            raise ValueError("build_material_yaml requires 'lattice' when a full 'phase' mapping is not provided.")
        if "elastic" not in spec:
            raise ValueError("build_material_yaml requires 'elastic' when a full 'phase' mapping is not provided.")
        mechanical: dict[str, Any] = {"elastic": spec["elastic"]}
        if "plastic" in spec:
            mechanical["plastic"] = spec["plastic"]
        phase = {
            phase_name: {
                "lattice": spec["lattice"],
                "mechanical": mechanical,
            }
        }

    payload = {
        "homogenization": spec.get(
            "homogenization",
            {homogenization_name: {"N_constituents": 1, "mechanical": {"type": "pass"}}},
        ),
        "phase": phase,
        "material": material_entries,
    }

    if _try_build_material_with_mcp(spec=spec, path=path, payload=payload):
        return str(path)

    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return str(path)


def build_load_yaml(spec: dict[str, Any], output_path: str) -> str:
    """Build a load.yaml from explicit load data.

    Generic loads should be passed as ``loadcase`` or ``loadstep`` mappings. The
    named uniaxial convenience path is used only when ``loading_mode`` is given.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if _try_build_load_with_mcp(spec=spec, path=path) and _is_valid_yaml_mapping(path, "loadstep"):
        return str(path)

    payload = _explicit_load_payload(spec)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return str(path)


def build_numerics_yaml(spec: dict[str, Any], output_path: str) -> str:
    """Build a numerics.yaml file from explicit numerics data."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if "numerics" not in spec:
        raise ValueError("build_numerics_yaml requires an explicit 'numerics' mapping.")
    payload = spec["numerics"]
    try:
        client = DAMASKPreprocessClient()
        client.write_yaml_file(path=str(path), data=payload)
        if _is_valid_yaml_mapping(path):
            return str(path)
    except Exception:
        pass
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return str(path)


def _try_build_material_with_mcp(*, spec: dict[str, Any], path: Path, payload: dict[str, Any]) -> bool:
    try:
        client = DAMASKPreprocessClient()
        material_entries = spec.get("material_entries")
        if material_entries:
            client.create_material_yaml_from_template(
                path=str(path),
                homogenization=payload["homogenization"],
                phase=payload["phase"],
                material=payload["material"],
            )
        else:
            client.create_material_yaml(
                path=str(path),
                material_name=spec.get("material_system", spec.get("phase_name", "material")),
                phase_name=spec.get("phase_name", spec.get("material_system", "phase_0")),
                lattice=spec["lattice"],
                elastic=spec["elastic"],
                plastic=spec.get("plastic"),
            )
        return _is_valid_yaml_mapping(path, "material")
    except Exception:
        return False


def _try_build_load_with_mcp(*, spec: dict[str, Any], path: Path) -> bool:
    try:
        if "loading_mode" not in spec and "workflow_type" not in spec:
            return False
        client = DAMASKPreprocessClient()
        mode = str(spec.get("loading_mode", spec.get("workflow_type"))).lower()
        if not {"final_strain", "strain_rate", "steps"}.issubset(spec):
            raise ValueError("Named load helpers require 'strain_rate', 'final_strain', and 'steps'.")
        final_strain = float(spec["final_strain"])
        strain_rate = float(spec["strain_rate"])
        steps = int(spec["steps"])
        if "compression" in mode:
            client.create_simple_compression_load_yaml(
                path=str(path),
                strain_rate=strain_rate,
                final_strain=final_strain,
                steps=steps,
            )
            return True
        if any(token in mode for token in ("tension", "simulation_run", "calibration", "comparison", "discovery")):
            client.create_simple_tension_load_yaml(
                path=str(path),
                strain_rate=strain_rate,
                final_strain=final_strain,
                steps=steps,
            )
            return True
        return False
    except Exception:
        return False


def _explicit_load_payload(spec: dict[str, Any]) -> dict[str, Any]:
    if "loadcase" in spec:
        loadcase = spec["loadcase"]
        if not isinstance(loadcase, dict):
            raise TypeError("'loadcase' must be a mapping.")
        return loadcase

    if "loadstep" in spec:
        loadstep = spec["loadstep"]
        if not isinstance(loadstep, list):
            raise TypeError("'loadstep' must be a list of DAMASK loadstep mappings.")
        payload: dict[str, Any] = {"loadstep": loadstep}
        if "solver" in spec:
            payload["solver"] = spec["solver"]
        return payload

    if "boundary_conditions" in spec:
        if "time" not in spec or "steps" not in spec:
            raise ValueError("Explicit boundary_conditions require 'time' and 'steps'.")
        step: dict[str, Any] = {
            "boundary_conditions": spec["boundary_conditions"],
            "discretization": {"t": float(spec["time"]), "N": int(spec["steps"])},
        }
        if "f_out" in spec:
            step["f_out"] = int(spec["f_out"])
        payload = {"loadstep": [step]}
        if "solver" in spec:
            payload["solver"] = spec["solver"]
        return payload

    raise ValueError(
        "build_load_yaml requires explicit 'loadcase', 'loadstep', or 'boundary_conditions'. "
        "Use create_simple_tension_load_yaml/create_simple_compression_load_yaml only for those named workflows."
    )


def _is_valid_yaml_mapping(path: Path, required_key: str | None = None) -> bool:
    if not path.exists():
        return False
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return False
    if not isinstance(payload, dict):
        return False
    if required_key is not None and required_key not in payload:
        return False
    return True
