from pathlib import Path

import yaml
import pytest

from damask_mcp.tools.damask_yaml import build_load_yaml, build_material_yaml, build_numerics_yaml
from damask_mcp.tools.validation import validate_material_yaml


def test_build_material_yaml_falls_back_when_mcp_output_is_not_structured_yaml(monkeypatch, tmp_path):
    material_path = tmp_path / "material.yaml"

    def fake_create_material_yaml(self, *, path, **kwargs):
        Path(path).write_text("material", encoding="utf-8")
        return {"ok": True, "path": path}

    monkeypatch.setattr(
        "damask_mcp.mcp_clients.damask_preprocess_client.DAMASKPreprocessClient.create_material_yaml",
        fake_create_material_yaml,
    )

    build_material_yaml(
        {
            "phase_name": "phase_a",
            "lattice": "cF",
            "elastic": {"type": "Hooke", "C_11": 1.0, "C_12": 0.5, "C_44": 0.25},
        },
        str(material_path),
    )
    payload = yaml.safe_load(material_path.read_text(encoding="utf-8"))

    assert isinstance(payload, dict)
    assert "material" in payload
    assert payload["phase"]["phase_a"]["mechanical"]["elastic"]["C_11"] == 1.0
    assert "plastic" not in payload["phase"]["phase_a"]["mechanical"]


def test_build_material_yaml_requires_explicit_material_parameters(tmp_path):
    with pytest.raises(ValueError, match="elastic"):
        build_material_yaml({"phase_name": "phase_a", "lattice": "cF"}, str(tmp_path / "material.yaml"))


def test_build_material_yaml_rejects_incomplete_cubic_hooke(tmp_path):
    with pytest.raises(ValueError, match="C_11, C_12, and C_44"):
        build_material_yaml(
            {"phase_name": "Cu", "lattice": "cF", "elastic": {"type": "Hooke", "C_11": 198.0e9}},
            str(tmp_path / "material.yaml"),
        )


def test_build_load_yaml_can_use_mcp_preprocess_client(monkeypatch, tmp_path):
    load_path = tmp_path / "load.yaml"

    def fake_create_simple_tension_load_yaml(self, *, path, strain_rate, final_strain, steps):
        Path(path).write_text(
            yaml.safe_dump({"loadstep": [{"discretization": {"N": steps, "t": final_strain / strain_rate}}]}, sort_keys=False),
            encoding="utf-8",
        )
        return {"ok": True, "path": path}

    monkeypatch.setattr(
        "damask_mcp.mcp_clients.damask_preprocess_client.DAMASKPreprocessClient.create_simple_tension_load_yaml",
        fake_create_simple_tension_load_yaml,
    )

    build_load_yaml(
        {"loading_mode": "uniaxial_tension", "strain_rate": 1.0e-3, "final_strain": 0.02, "steps": 5},
        str(load_path),
    )
    payload = yaml.safe_load(load_path.read_text(encoding="utf-8"))

    assert isinstance(payload, dict)
    assert "loadstep" in payload


def test_build_load_yaml_accepts_explicit_loadcase_without_default_deformation(tmp_path):
    load_path = tmp_path / "load.yaml"
    build_load_yaml(
        {
            "loadcase": {
                "solver": {"mechanical": "spectral_basic"},
                "loadstep": [
                    {
                        "boundary_conditions": {"mechanical": {"P": [[0, "x", "x"], ["x", 0, "x"], ["x", "x", 0]]}},
                        "discretization": {"t": 2.0, "N": 4},
                    }
                ],
            }
        },
        str(load_path),
    )

    payload = yaml.safe_load(load_path.read_text(encoding="utf-8"))

    assert "loadstep" in payload
    assert "F" not in payload["loadstep"][0]["boundary_conditions"]["mechanical"]


def test_build_load_yaml_requires_explicit_load_definition(tmp_path):
    with pytest.raises(ValueError, match="explicit"):
        build_load_yaml({}, str(tmp_path / "load.yaml"))


def test_build_numerics_yaml_falls_back_when_mcp_writer_is_unavailable(monkeypatch, tmp_path):
    numerics_path = tmp_path / "numerics.yaml"

    monkeypatch.setattr(
        "damask_mcp.mcp_clients.damask_preprocess_client.DAMASKPreprocessClient.write_yaml_file",
        lambda self, *, path, data: (_ for _ in ()).throw(RuntimeError("mcp unavailable")),
    )

    build_numerics_yaml({"numerics": {"solver": {"grid": {"N_staggered_iter_max": 12}}}}, str(numerics_path))
    payload = yaml.safe_load(numerics_path.read_text(encoding="utf-8"))

    assert payload["solver"]["grid"]["N_staggered_iter_max"] == 12


def test_build_numerics_yaml_requires_explicit_numerics(tmp_path):
    with pytest.raises(ValueError, match="numerics"):
        build_numerics_yaml({}, str(tmp_path / "numerics.yaml"))


def test_validate_material_yaml_includes_optional_mcp_validation(monkeypatch, tmp_path):
    material_path = tmp_path / "material.yaml"
    material_path.write_text(
        yaml.safe_dump(
            {
                "homogenization": {"SX": {"N_constituents": 1, "mechanical": {"type": "pass"}}},
                "phase": {"alpha": {"lattice": "cF", "mechanical": {"elastic": {"type": "Hooke"}}}},
                "material": [{"homogenization": "SX", "constituents": [{"phase": "alpha", "O": [1.0, 0.0, 0.0, 0.0], "v": 1.0}]}],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "damask_mcp.mcp_clients.damask_preprocess_client.DAMASKPreprocessClient.validate_material_yaml",
        lambda self, *, path: {"ok": True, "source": "mcp"},
    )

    result = validate_material_yaml(str(material_path))

    assert result["ok"] is True
    assert result["mcp_validation"]["source"] == "mcp"
