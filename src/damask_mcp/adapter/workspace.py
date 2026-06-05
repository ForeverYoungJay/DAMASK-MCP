"""Workspace and DAMASK source discovery helpers."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any

from damask_mcp.runtime import runtime_root


def project_root() -> Path:
    """Return the DAMASK MCP project root."""
    return Path(__file__).resolve().parents[3]


def workspaces_root() -> Path:
    """Return the workspace root and create it if needed."""
    configured = os.environ.get("DAMASK_MCP_WORKSPACES")
    roots = [Path(configured).expanduser()] if configured else [Path.cwd() / "workspaces", runtime_root() / "workspaces"]

    errors: list[str] = []
    for root in roots:
        try:
            root.mkdir(parents=True, exist_ok=True)
            return root
        except OSError as exc:
            errors.append(f"{root}: {exc}")

    configured_hint = "the configured DAMASK_MCP_WORKSPACES" if configured else "the current working directory or runtime workspaces"
    tried = "; ".join(errors)
    raise RuntimeError(
        f"Could not create {configured_hint}. Tried: {tried}. "
        "Set DAMASK_MCP_WORKSPACES to a writable directory shared with the MCP runtime."
    )


def preferred_workspaces_root() -> Path:
    """Return the preferred workspace path before writability fallback is applied."""
    configured = os.environ.get("DAMASK_MCP_WORKSPACES")
    return Path(configured).expanduser() if configured else Path.cwd() / "workspaces"


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
