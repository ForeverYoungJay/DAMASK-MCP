from pathlib import Path

from damask_mcp.adapter import workspace


def test_project_root_contains_src():
    assert (workspace.project_root() / "src").exists()


def test_workspaces_root_exists():
    assert workspace.workspaces_root().exists()
    assert workspace.workspaces_root().name == "workspaces"


def test_workspaces_root_defaults_to_current_working_directory(monkeypatch, tmp_path):
    monkeypatch.delenv("DAMASK_MCP_WORKSPACES", raising=False)
    monkeypatch.chdir(tmp_path)

    assert workspace.workspaces_root() == tmp_path / "workspaces"


def test_workspaces_root_can_be_configured(monkeypatch, tmp_path):
    configured = tmp_path / "mcp-workspaces"
    monkeypatch.setenv("DAMASK_MCP_WORKSPACES", str(configured))

    assert workspace.workspaces_root() == configured
    assert configured.exists()
