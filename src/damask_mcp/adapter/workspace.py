"""Workspace and DAMASK source discovery helpers."""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def project_root() -> Path:
    """Return the DAMASK MCP project root."""
    return Path(__file__).resolve().parents[3]


def workspaces_root() -> Path:
    """Return the workspace root and create it if needed."""
    configured = os.environ.get("DAMASK_MCP_WORKSPACES")
    candidates = [Path(configured).expanduser()] if configured else []
    candidates.extend([project_root() / "workspaces", Path(tempfile.gettempdir()) / "damask-mcp-workspaces"])

    errors: list[str] = []
    for root in candidates:
        try:
            root.mkdir(parents=True, exist_ok=True)
            return root
        except OSError as exc:
            errors.append(f"{root}: {exc}")

    raise RuntimeError("Could not create a DAMASK MCP workspace root. Tried: " + "; ".join(errors))


def damask_python_root() -> Path:
    """Return the local DAMASK Python source root."""
    return project_root() / "damask-3.0.2" / "python"


def ensure_damask_python_on_path() -> Path:
    """Ensure the local DAMASK Python source is importable."""
    path = damask_python_root()
    path_str = str(path)
    if path.exists() and path_str not in sys.path:
        sys.path.insert(0, path_str)
    return path


def import_damask() -> Any:
    """Import the DAMASK Python package from an installed package or local source tree."""
    try:
        return importlib.import_module("damask")
    except ModuleNotFoundError:
        ensure_damask_python_on_path()
        return importlib.import_module("damask")
