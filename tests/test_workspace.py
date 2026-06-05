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


def test_workspaces_root_falls_back_to_runtime_dir_when_cwd_is_read_only(monkeypatch, tmp_path):
    runtime_dir = tmp_path / "runtime"
    read_only_root = Path("/app")
    original_mkdir = Path.mkdir

    def fake_mkdir(self, *args, **kwargs):
        if self == read_only_root / "workspaces":
            raise OSError("read-only")
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.delenv("DAMASK_MCP_WORKSPACES", raising=False)
    monkeypatch.setenv("DAMASK_MCP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setattr(workspace.Path, "cwd", staticmethod(lambda: read_only_root))
    monkeypatch.setattr(workspace.Path, "mkdir", fake_mkdir)

    assert workspace.workspaces_root() == runtime_dir / "workspaces"


def test_workspaces_root_can_be_configured(monkeypatch, tmp_path):
    configured = tmp_path / "mcp-workspaces"
    monkeypatch.setenv("DAMASK_MCP_WORKSPACES", str(configured))

    assert workspace.workspaces_root() == configured
    assert configured.exists()
