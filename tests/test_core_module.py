from damask_mcp.adapter.modules import core


class FakeRotation:
    """Fake Rotation."""

    def from_random(self):
        return None


class FakeDamask:
    __version__ = "3.0.2"
    __file__ = "/tmp/damask/__init__.py"
    Rotation = FakeRotation


def test_check_damask_installation(monkeypatch):
    monkeypatch.setattr(core, "import_damask", lambda: FakeDamask)
    result = core.check_damask_installation()
    assert result["ok"] is True
    assert result["version"] == "3.0.2"
    assert result["import_location"] == "installed_package"
    assert result["using_local_source"] is False
    assert result["module_file"].endswith("/damask/__init__.py")


def test_diagnose_damask_runtime(monkeypatch, tmp_path):
    monkeypatch.setattr(core, "check_damask_installation", lambda: {"ok": True})
    monkeypatch.setattr(core, "find_damask_executables", lambda: {"selected": None})
    monkeypatch.setattr(core, "workspaces_root", lambda: tmp_path / "workspaces")
    monkeypatch.setattr(core, "preferred_workspaces_root", lambda: tmp_path / "workspaces")

    result = core.diagnose_damask_runtime()

    assert result["ok"] is False
    assert result["python"]["ok"] is True
    assert result["solver"]["selected"] is None
    assert result["workspace"]["ok"] is True
    assert result["recommendations"]


def test_inspect_damask_class(monkeypatch):
    monkeypatch.setattr(core, "import_damask", lambda: FakeDamask)
    result = core.inspect_damask_class("Rotation")
    assert result["ok"] is True
    assert result["class_name"] == "Rotation"
