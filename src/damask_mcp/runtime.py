"""Runtime filesystem defaults for hosted and local MCP environments."""

from __future__ import annotations

import os
from pathlib import Path


def runtime_root() -> Path:
    """Return the writable runtime root used for cache, temp, and state files."""
    configured = os.environ.get("DAMASK_MCP_RUNTIME_DIR")
    return Path(configured).expanduser() if configured else Path("/tmp") / "damask-mcp"


def ensure_runtime_subdir(name: str) -> Path:
    """Create and return a subdirectory under the writable runtime root."""
    path = runtime_root() / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_runtime_environment() -> dict[str, str]:
    """Set safe writable defaults for libraries that otherwise write near the app."""
    defaults = {
        "TMPDIR": ensure_runtime_subdir("tmp"),
        "TEMP": ensure_runtime_subdir("tmp"),
        "TMP": ensure_runtime_subdir("tmp"),
        "XDG_CACHE_HOME": ensure_runtime_subdir("cache"),
        "MPLCONFIGDIR": ensure_runtime_subdir("matplotlib"),
        "PYTHONPYCACHEPREFIX": ensure_runtime_subdir("pycache"),
        "DAMASK_MCP_DB_DIR": ensure_runtime_subdir("db"),
    }
    applied: dict[str, str] = {}
    for name, path in defaults.items():
        value = str(path)
        os.environ[name] = value
        Path(value).expanduser().mkdir(parents=True, exist_ok=True)
        applied[name] = value
    return applied
