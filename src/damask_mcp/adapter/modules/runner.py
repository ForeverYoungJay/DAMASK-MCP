"""Safe runner helpers for DAMASK_grid."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from damask_mcp.adapter.validators import ensure_existing_directory, ensure_existing_file, ensure_path_within_workspaces, resolve_workspace_dir
from damask_mcp.adapter.workspace import project_root

RESULT_SUFFIXES = {".hdf5", ".h5", ".vti", ".vtu", ".vtp", ".xdmf", ".csv"}
INPUT_FILENAMES = {"geometry.vti", "load.yaml", "material.yaml", "numerics.yaml"}


def _executable_probe() -> tuple[list[Path], list[dict[str, Any]]]:
    probes: list[dict[str, Any]] = []
    candidates: list[Path] = []

    def add_probe(source: str, path: str | Path | None, hint: str | None = None) -> None:
        if path is None:
            probes.append({"source": source, "path": None, "exists": False, "hint": hint})
            return
        candidate = Path(path).expanduser()
        exists = candidate.exists()
        executable = exists and os.access(candidate, os.X_OK)
        probes.append(
            {
                "source": source,
                "path": str(candidate),
                "exists": exists,
                "executable": executable,
                "hint": hint,
            }
        )
        if executable:
            candidates.append(candidate)

    configured = os.environ.get("DAMASK_GRID_EXECUTABLE")
    add_probe(
        "DAMASK_GRID_EXECUTABLE",
        configured,
        "Set this environment variable to the absolute DAMASK_grid path when it is not on PATH.",
    )

    add_probe("PATH", shutil.which("DAMASK_grid"), "Resolved with shutil.which('DAMASK_grid').")
    add_probe("python_env_bin", Path(sys.executable).resolve().parent / "DAMASK_grid")

    conda_prefix = os.environ.get("CONDA_PREFIX")
    add_probe("CONDA_PREFIX/bin", Path(conda_prefix) / "bin" / "DAMASK_grid" if conda_prefix else None)

    for candidate in [
        project_root() / "damask-3.0.2" / "bin" / "DAMASK_grid",
        project_root() / "damask-3.0.2" / "build" / "DAMASK_grid",
        project_root() / "damask-3.0.2" / "src" / "grid" / "DAMASK_grid",
    ]:
        add_probe("local_damask_source", candidate)

    unique: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        resolved = str(path.resolve())
        if resolved not in seen:
            unique.append(path.resolve())
            seen.add(resolved)
    return unique, probes


def _candidate_executables() -> list[Path]:
    candidates, _ = _executable_probe()
    return candidates


def find_damask_executables() -> dict[str, Any]:
    """Find DAMASK_grid executables on PATH and in common local build locations."""
    candidates, probes = _executable_probe()
    guidance = [
        "DAMASK_grid is the solver executable; the damask Python package alone may not provide it.",
        "If DAMASK_grid is installed but not discoverable, set DAMASK_GRID_EXECUTABLE to its absolute path.",
        "Common locations are a Conda environment bin directory, ~/.local/bin, or a local DAMASK build directory.",
    ]
    return {
        "ok": True,
        "count": len(candidates),
        "executables": [str(path) for path in candidates],
        "selected": str(candidates[0]) if candidates else None,
        "probes": probes,
        "environment": {
            "python_executable": sys.executable,
            "conda_prefix": os.environ.get("CONDA_PREFIX"),
            "path_preview": os.environ.get("PATH", "").split(os.pathsep)[:12],
        },
        "guidance": guidance,
    }


def list_workspace_files(workspace: str) -> dict[str, Any]:
    """List files under a named workspace."""
    try:
        workspace_dir = ensure_existing_directory(resolve_workspace_dir(workspace))
        files = sorted(str(path) for path in workspace_dir.rglob("*") if path.is_file())
        return {"ok": True, "workspace": workspace, "count": len(files), "files": files}
    except Exception as exc:
        return {"ok": False, "workspace": workspace, "error": f"{type(exc).__name__}: {exc}"}


def collect_result_files(workspace: str) -> dict[str, Any]:
    """Collect result-like files under a named workspace."""
    try:
        workspace_dir = ensure_existing_directory(resolve_workspace_dir(workspace))
        results_dir = workspace_dir / "results"
        search_roots = [results_dir, workspace_dir] if results_dir.exists() else [workspace_dir]
        files: list[str] = []
        seen: set[str] = set()
        for root in search_roots:
            for path in sorted(root.rglob("*")):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in RESULT_SUFFIXES:
                    continue
                if path.name in INPUT_FILENAMES and path.parent == workspace_dir:
                    continue
                resolved = str(path.resolve())
                if resolved in seen:
                    continue
                files.append(resolved)
                seen.add(resolved)
        return {"ok": True, "workspace": workspace, "count": len(files), "files": files}
    except Exception as exc:
        return {"ok": False, "workspace": workspace, "error": f"{type(exc).__name__}: {exc}"}


def run_damask_grid(
    workspace: str,
    geometry: str,
    load: str,
    material: str,
    numerics: str | None = None,
    timeout_seconds: int = 3600,
) -> dict[str, Any]:
    """Run DAMASK_grid with workspace-local input files using a safe subprocess call."""
    try:
        executables = _candidate_executables()
        if not executables:
            return {
                "ok": False,
                "workspace": workspace,
                "error": (
                    "DAMASK_grid executable not found in this MCP runtime. "
                    "Install/build DAMASK_grid, add it to PATH, or set DAMASK_GRID_EXECUTABLE "
                    "to its absolute path. The damask Python package alone may not include the solver binary."
                ),
            }
        workspace_dir = ensure_existing_directory(resolve_workspace_dir(workspace))
        geometry_path = ensure_path_within_workspaces(workspace_dir / geometry)
        load_path = ensure_path_within_workspaces(workspace_dir / load)
        material_path = ensure_path_within_workspaces(workspace_dir / material)
        numerics_path = ensure_path_within_workspaces(workspace_dir / numerics) if numerics else None
        ensure_existing_file(geometry_path)
        ensure_existing_file(load_path)
        ensure_existing_file(material_path)
        if numerics_path is not None:
            ensure_existing_file(numerics_path)
        executable = executables[0]
        command = [
            str(executable),
            "--geom",
            str(geometry_path),
            "--load",
            str(load_path),
            "--material",
            str(material_path),
            "--workingdir",
            str(workspace_dir),
        ]
        if numerics_path is not None:
            command.extend(["--numerics", str(numerics_path)])
        process = subprocess.run(
            command,
            cwd=workspace_dir,
            env=os.environ.copy(),
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        return {
            "ok": process.returncode == 0,
            "workspace": workspace,
            "executable": str(executable),
            "returncode": int(process.returncode),
            "stdout_tail": process.stdout.splitlines()[-50:],
            "stderr_tail": process.stderr.splitlines()[-50:],
            "result_files": collect_result_files(workspace).get("files", []),
        }
    except subprocess.TimeoutExpired as exc:
        return {"ok": False, "workspace": workspace, "error": f"TimeoutExpired: {exc}"}
    except Exception as exc:
        return {"ok": False, "workspace": workspace, "error": f"{type(exc).__name__}: {exc}"}


__all__ = [
    "collect_result_files",
    "find_damask_executables",
    "list_workspace_files",
    "run_damask_grid",
]
