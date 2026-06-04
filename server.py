"""Stable top-level FastMCP entrypoint for local tools and hosted deployment."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from damask_mcp.mcp_servers.damask_server import create_server, mcp  # noqa: E402

__all__ = ["create_server", "mcp"]
