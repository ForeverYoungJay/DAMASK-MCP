from pathlib import Path

from damask_mcp import runtime


def test_configure_runtime_environment_uses_runtime_dir(monkeypatch, tmp_path):
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setenv("DAMASK_MCP_RUNTIME_DIR", str(runtime_dir))
    for name in ["TMPDIR", "TEMP", "TMP", "XDG_CACHE_HOME", "MPLCONFIGDIR", "PYTHONPYCACHEPREFIX", "DAMASK_MCP_DB_DIR"]:
        monkeypatch.delenv(name, raising=False)

    applied = runtime.configure_runtime_environment()

    assert applied["TMPDIR"] == str(runtime_dir / "tmp")
    assert applied["XDG_CACHE_HOME"] == str(runtime_dir / "cache")
    assert applied["MPLCONFIGDIR"] == str(runtime_dir / "matplotlib")
    assert applied["PYTHONPYCACHEPREFIX"] == str(runtime_dir / "pycache")
    assert applied["DAMASK_MCP_DB_DIR"] == str(runtime_dir / "db")
    assert all(Path(path).exists() for path in applied.values())


def test_configure_runtime_environment_overrides_existing_temp_dirs(monkeypatch, tmp_path):
    runtime_dir = tmp_path / "runtime"
    monkeypatch.setenv("DAMASK_MCP_RUNTIME_DIR", str(runtime_dir))
    monkeypatch.setenv("TMPDIR", "/not-used")

    applied = runtime.configure_runtime_environment()

    assert applied["TMPDIR"] == str(runtime_dir / "tmp")
