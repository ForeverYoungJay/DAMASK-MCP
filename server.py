"""Stable top-level FastMCP entrypoint for local tools and hosted deployment."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _configure_early_runtime_environment() -> None:
    runtime_root = Path(os.environ.get("DAMASK_MCP_RUNTIME_DIR", "/tmp/damask-mcp")).expanduser()
    defaults = {
        "TMPDIR": runtime_root / "tmp",
        "TEMP": runtime_root / "tmp",
        "TMP": runtime_root / "tmp",
        "XDG_CACHE_HOME": runtime_root / "cache",
        "MPLCONFIGDIR": runtime_root / "matplotlib",
        "PYTHONPYCACHEPREFIX": runtime_root / "pycache",
        "DAMASK_MCP_DB_DIR": runtime_root / "db",
    }
    for name, path in defaults.items():
        path.mkdir(parents=True, exist_ok=True)
        os.environ[name] = str(path)


_configure_early_runtime_environment()

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from damask_mcp.mcp_servers.damask_server import create_server, mcp  # noqa: E402

__all__ = ["create_server", "mcp"]
