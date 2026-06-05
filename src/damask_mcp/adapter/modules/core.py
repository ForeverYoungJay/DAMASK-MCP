"""Core DAMASK inspection and environment helpers."""

from __future__ import annotations

import importlib
import inspect
import os
from pathlib import Path
from typing import Any

from damask_mcp.adapter.modules.runner import find_damask_executables
from damask_mcp.adapter.workspace import preferred_workspaces_root, workspaces_root
from damask_mcp.runtime import configure_runtime_environment, runtime_root
from damask_mcp.adapter.workspace import damask_python_root, import_damask


def _safe_signature(obj: Any) -> str | None:
    try:
        return str(inspect.signature(obj))
    except Exception:
        return None


def _safe_doc(obj: Any) -> str | None:
    doc = inspect.getdoc(obj)
    if doc is None:
        return None
    lines = [line.rstrip() for line in doc.splitlines()[:20]]
    return "\n".join(lines)


def check_damask_installation() -> dict[str, Any]:
    """Check whether the local DAMASK Python package can be imported."""
    try:
        damask = import_damask()
        local_source_root = damask_python_root().resolve()
        module_file = Path(damask.__file__).resolve()
        try:
            module_file.relative_to(local_source_root)
            using_local_source = True
        except ValueError:
            using_local_source = False
        return {
            "ok": True,
            "imported": True,
            "version": getattr(damask, "__version__", None),
            "source_root": str(local_source_root),
            "local_source_root": str(local_source_root),
            "local_source_exists": local_source_root.exists(),
            "using_local_source": using_local_source,
            "import_location": "local_source" if using_local_source else "installed_package",
            "module_file": str(module_file),
        }
    except Exception as exc:
        local_source_root = damask_python_root().resolve()
        return {
            "ok": False,
            "imported": False,
            "source_root": str(local_source_root),
            "local_source_root": str(local_source_root),
            "local_source_exists": local_source_root.exists(),
            "error": f"{type(exc).__name__}: {exc}",
        }


def diagnose_damask_runtime() -> dict[str, Any]:
    """Diagnose Python, workspace, cache, and solver readiness for this MCP runtime."""
    runtime_env = configure_runtime_environment()
    python_result = check_damask_installation()
    solver_result = find_damask_executables()
    workspace_result: dict[str, Any]
    try:
        workspace = workspaces_root()
        workspace_result = {
            "ok": True,
            "path": str(workspace.resolve()),
            "preferred_path": str(preferred_workspaces_root().resolve()),
        }
    except Exception as exc:
        workspace_result = {
            "ok": False,
            "preferred_path": str(preferred_workspaces_root().resolve()),
            "error": f"{type(exc).__name__}: {exc}",
        }

    recommendations: list[str] = []
    if not python_result.get("ok"):
        recommendations.append("Install the DAMASK Python package in the MCP runtime.")
    if not solver_result.get("selected"):
        recommendations.append(
            "Install the DAMASK metapackage or solver binary in the MCP runtime, then set DAMASK_GRID_EXECUTABLE."
        )
    if not workspace_result.get("ok"):
        recommendations.append("Set DAMASK_MCP_WORKSPACES to a writable directory such as /tmp/damask-mcp/workspaces.")

    return {
        "ok": bool(python_result.get("ok") and solver_result.get("selected") and workspace_result.get("ok")),
        "python": python_result,
        "solver": solver_result,
        "workspace": workspace_result,
        "runtime": {
            "root": str(runtime_root().resolve()),
            "environment": runtime_env,
            "cwd": str(Path.cwd()),
            "env": {
                "DAMASK_MCP_RUNTIME_DIR": os.environ.get("DAMASK_MCP_RUNTIME_DIR"),
                "DAMASK_MCP_WORKSPACES": os.environ.get("DAMASK_MCP_WORKSPACES"),
                "DAMASK_GRID_EXECUTABLE": os.environ.get("DAMASK_GRID_EXECUTABLE"),
                "CONDA_PREFIX": os.environ.get("CONDA_PREFIX"),
            },
        },
        "recommendations": recommendations,
    }


def get_damask_version() -> dict[str, Any]:
    """Return the local DAMASK Python package version."""
    result = check_damask_installation()
    if not result["ok"]:
        return result
    return {
        "ok": True,
        "version": result["version"],
        "module_file": result["module_file"],
    }


def list_damask_modules() -> dict[str, Any]:
    """List the main modules and classes exported by DAMASK."""
    try:
        damask = import_damask()
        exported = sorted(name for name in dir(damask) if not name.startswith("_"))
        return {
            "ok": True,
            "count": len(exported),
            "exports": exported,
        }
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def inspect_damask_class(class_name: str) -> dict[str, Any]:
    """Inspect a DAMASK class exported from the top-level package."""
    try:
        damask = import_damask()
        obj = getattr(damask, class_name)
        if not inspect.isclass(obj):
            return {"ok": False, "class_name": class_name, "error": f"{class_name} is not a class."}
        methods = []
        for name, member in inspect.getmembers(obj):
            if name.startswith("_"):
                continue
            if callable(member):
                methods.append({"name": name, "signature": _safe_signature(member)})
        return {
            "ok": True,
            "class_name": class_name,
            "module": getattr(obj, "__module__", None),
            "doc": _safe_doc(obj),
            "method_count": len(methods),
            "methods": methods[:200],
            "truncated": len(methods) > 200,
        }
    except Exception as exc:
        return {"ok": False, "class_name": class_name, "error": f"{type(exc).__name__}: {exc}"}


def inspect_damask_function(function_name: str) -> dict[str, Any]:
    """Inspect a DAMASK function from the top-level package or main submodules."""
    module_candidates = [
        "damask",
        "damask.mechanics",
        "damask.tensor",
        "damask.util",
        "damask.grid_filters",
        "damask.seeds",
    ]
    for module_name in module_candidates:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, function_name):
                obj = getattr(module, function_name)
                if not callable(obj):
                    return {
                        "ok": False,
                        "function_name": function_name,
                        "module": module_name,
                        "error": f"{function_name} exists in {module_name} but is not callable.",
                    }
                return {
                    "ok": True,
                    "function_name": function_name,
                    "module": module_name,
                    "signature": _safe_signature(obj),
                    "doc": _safe_doc(obj),
                }
        except Exception:
            continue
    return {"ok": False, "function_name": function_name, "error": f"Function not found: {function_name}"}


__all__ = [
    "check_damask_installation",
    "diagnose_damask_runtime",
    "get_damask_version",
    "inspect_damask_class",
    "inspect_damask_function",
    "list_damask_modules",
]
