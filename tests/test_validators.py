from pathlib import Path

import pytest

from damask_mcp.adapter import validators


def test_validate_workspace_name_accepts_safe_names():
    assert validators.validate_workspace_name("demo_tension") == "demo_tension"


def test_validate_workspace_name_rejects_unsafe_names():
    with pytest.raises(ValueError):
        validators.validate_workspace_name("../bad")


def test_workspace_write_path_stays_inside_workspaces():
    path = validators.ensure_workspace_write_path("demo_tension/test.yaml")
    assert "workspaces" in str(path)


def test_workspace_write_path_rejects_escape():
    with pytest.raises(ValueError):
        validators.ensure_workspace_write_path("/tmp/outside.txt")


def test_workspace_read_path_uses_same_relative_semantics(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspaces"
    monkeypatch.setenv("DAMASK_MCP_WORKSPACES", str(workspace_root))
    file_path = workspace_root / "demo_tension" / "test.yaml"
    file_path.parent.mkdir(parents=True)
    file_path.write_text("ok: true\n", encoding="utf-8")

    assert validators.ensure_existing_file("demo_tension/test.yaml") == file_path.resolve()
    assert validators.ensure_existing_file("workspaces/demo_tension/test.yaml") == file_path.resolve()


def test_workspace_read_path_rejects_escape(monkeypatch, tmp_path):
    workspace_root = tmp_path / "workspaces"
    outside = tmp_path / "outside.yaml"
    outside.write_text("ok: false\n", encoding="utf-8")
    monkeypatch.setenv("DAMASK_MCP_WORKSPACES", str(workspace_root))

    with pytest.raises(ValueError):
        validators.ensure_existing_file(outside)
