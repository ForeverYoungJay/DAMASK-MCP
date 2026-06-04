from damask_mcp.adapter.modules import runner


def test_find_damask_executables_includes_configured_path(monkeypatch, tmp_path):
    executable = tmp_path / "DAMASK_grid"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o755)
    monkeypatch.setenv("DAMASK_GRID_EXECUTABLE", str(executable))
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    monkeypatch.setenv("PATH", "")

    result = runner.find_damask_executables()

    assert result["ok"] is True
    assert result["selected"] == str(executable)
    assert str(executable) in result["executables"]
    assert result["guidance"]
    assert any(probe["source"] == "DAMASK_GRID_EXECUTABLE" for probe in result["probes"])


def test_find_damask_executables_reports_non_executable_configured_path(monkeypatch, tmp_path):
    executable = tmp_path / "DAMASK_grid"
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    executable.chmod(0o644)
    monkeypatch.setenv("DAMASK_GRID_EXECUTABLE", str(executable))
    monkeypatch.setattr(runner.shutil, "which", lambda name: None)
    monkeypatch.setenv("PATH", "")

    result = runner.find_damask_executables()

    configured_probe = next(probe for probe in result["probes"] if probe["source"] == "DAMASK_GRID_EXECUTABLE")
    assert configured_probe["exists"] is True
    assert configured_probe["executable"] is False
    assert str(executable) not in result["executables"]
