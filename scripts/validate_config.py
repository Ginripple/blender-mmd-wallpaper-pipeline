#!/usr/bin/env python3
"""Validate a blender-mmd-wallpaper-pipeline JSON configuration.

The validator is read-only. It validates schema/value ranges and checks whether
configured working directories exist under a project root. Missing working
folders are warnings by default because they may be created later; use
--require-directories to make them validation errors.

Exit codes:
  0 success
  1 operational/filesystem error
  2 CLI usage error (reserved for argparse)
  3 configuration content/validation failure
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import (
    EXIT_OPERATIONAL_ERROR,
    EXIT_SUCCESS,
    EXIT_VALIDATION_FAILED,
)

SUPPORTED_SCHEMA_VERSION = 1


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _expect_dict(data: dict, key: str, errors: list[str]) -> dict:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _result(
    *,
    valid: bool,
    errors: list[str],
    warnings: list[str],
    directory_checks: list[dict],
    operational_errors: list[str] | None = None,
) -> dict:
    operational_errors = operational_errors or []
    return {
        "schema_version": 1,
        "ok": valid,
        "valid": valid,
        "errors": errors,
        "operational_errors": operational_errors,
        "warnings": warnings,
        "directory_checks": directory_checks,
    }


def validate_config_data(
    data: Any,
    project_root: Path | None = None,
    require_directories: bool = False,
) -> dict:
    errors: list[str] = []
    operational_errors: list[str] = []
    warnings: list[str] = []
    directory_checks: list[dict] = []

    if not isinstance(data, dict):
        return _result(
            valid=False,
            errors=["configuration root must be a JSON object"],
            warnings=[],
            directory_checks=[],
        )

    schema_version = data.get("schema_version")
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SUPPORTED_SCHEMA_VERSION}; got {schema_version!r}"
        )

    prefixes = data.get("generated_prefixes")
    if not isinstance(prefixes, list) or not prefixes:
        errors.append("generated_prefixes must be a non-empty array")
    else:
        for index, prefix in enumerate(prefixes):
            if not isinstance(prefix, str) or not prefix.strip():
                errors.append(f"generated_prefixes[{index}] must be a non-empty string")

    working_dirs = data.get("working_directories")
    if not isinstance(working_dirs, list) or not working_dirs:
        errors.append("working_directories must be a non-empty array")
        working_dirs = []
    else:
        for index, item in enumerate(working_dirs):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"working_directories[{index}] must be a non-empty string")

    root = project_root.resolve() if project_root is not None else None
    if root is not None:
        if not root.exists() or not root.is_dir():
            message = f"project root is not a directory: {root}"
            errors.append(message)
            operational_errors.append(message)
        else:
            for item in working_dirs:
                if not isinstance(item, str) or not item.strip():
                    continue
                path = (root / item).resolve()
                try:
                    path.relative_to(root)
                    inside_root = True
                except ValueError:
                    inside_root = False
                exists = path.is_dir()
                directory_checks.append({
                    "configured": item,
                    "resolved": str(path),
                    "inside_project_root": inside_root,
                    "exists": exists,
                })
                if not inside_root:
                    errors.append(f"working directory escapes project root: {item}")
                elif not exists:
                    message = f"working directory does not exist yet: {item}"
                    (errors if require_directories else warnings).append(message)

    camera = _expect_dict(data, "camera", errors)
    yaw = camera.get("yaw_degrees")
    pitch = camera.get("pitch_degrees")
    zoom_min = camera.get("zoom_min")
    zoom_max = camera.get("zoom_max")
    if not _number(yaw) or not 0 <= float(yaw) <= 90:
        errors.append("camera.yaw_degrees must be a number in [0, 90]")
    if not _number(pitch) or not 0 <= float(pitch) <= 60:
        errors.append("camera.pitch_degrees must be a number in [0, 60]")
    if not _number(zoom_min) or float(zoom_min) <= 0:
        errors.append("camera.zoom_min must be a positive number")
    if not _number(zoom_max) or float(zoom_max) <= 0:
        errors.append("camera.zoom_max must be a positive number")
    if _number(zoom_min) and _number(zoom_max) and float(zoom_min) > float(zoom_max):
        errors.append("camera.zoom_min must be <= camera.zoom_max")

    preview = _expect_dict(data, "preview", errors)
    max_renders = preview.get("max_consecutive_inconclusive_renders")
    if not isinstance(max_renders, int) or isinstance(max_renders, bool) or max_renders < 1:
        errors.append("preview.max_consecutive_inconclusive_renders must be an integer >= 1")
    prefer_single = preview.get("prefer_single_frame")
    if not isinstance(prefer_single, bool):
        errors.append("preview.prefer_single_frame must be boolean")

    runtime = _expect_dict(data, "runtime_target", errors)
    for key in ("width", "height", "fps"):
        value = runtime.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            errors.append(f"runtime_target.{key} must be a positive integer")

    return _result(
        valid=not errors,
        errors=errors,
        operational_errors=operational_errors,
        warnings=warnings,
        directory_checks=directory_checks,
    )


def validate_config_file(
    config_path: Path,
    project_root: Path | None = None,
    require_directories: bool = False,
) -> dict:
    config_path = config_path.resolve()
    if not config_path.is_file():
        message = f"config file does not exist: {config_path}"
        result = _result(
            valid=False,
            errors=[message],
            operational_errors=[message],
            warnings=[],
            directory_checks=[],
        )
        result["config"] = str(config_path)
        result["error_code"] = "CONFIG_FILE_NOT_FOUND"
        return result

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        message = f"failed to read config file: {exc}"
        result = _result(
            valid=False,
            errors=[message],
            operational_errors=[message],
            warnings=[],
            directory_checks=[],
        )
        result["config"] = str(config_path)
        result["error_code"] = "CONFIG_READ_FAILED"
        return result

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        result = _result(
            valid=False,
            errors=[f"invalid JSON config: {exc}"],
            warnings=[],
            directory_checks=[],
        )
        result["config"] = str(config_path)
        result["error_code"] = "CONFIG_INVALID_JSON"
        return result

    result = validate_config_data(data, project_root, require_directories)
    result["config"] = str(config_path)
    if not result["valid"] and not result["operational_errors"]:
        result["error_code"] = "CONFIG_VALIDATION_FAILED"
    elif result["operational_errors"]:
        result["error_code"] = "PROJECT_ROOT_INVALID"
    return result


def exit_code_for_result(result: dict) -> int:
    if result.get("valid", False):
        return EXIT_SUCCESS
    if result.get("operational_errors"):
        return EXIT_OPERATIONAL_ERROR
    return EXIT_VALIDATION_FAILED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("config", nargs="?", default="assets/config.example.json", help="JSON config path")
    ap.add_argument("--project-root", help="Optional project root used for working-directory checks")
    ap.add_argument(
        "--require-directories",
        action="store_true",
        help="Treat missing configured working directories as errors instead of warnings",
    )
    args = ap.parse_args()

    result = validate_config_file(
        Path(args.config),
        Path(args.project_root) if args.project_root else None,
        args.require_directories,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code_for_result(result)


if __name__ == "__main__":
    raise SystemExit(main())
