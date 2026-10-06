#!/usr/bin/env python3
"""Run inventory, third-party terms discovery, and optional config validation.

Exit codes:
  0 success
  1 operational/filesystem error
  2 CLI usage error (reserved for argparse)
  3 configuration content/validation failure

All tool-generated outcomes are emitted as JSON on stdout. argparse retains its
normal usage/error output on stderr for exit code 2.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import EXIT_OPERATIONAL_ERROR, EXIT_SUCCESS
from audit_assets import audit
from check_project import scan
from validate_config import exit_code_for_result, validate_config_file


def build_report(
    root: Path,
    excludes: list[str] | None = None,
    details_limit: int = 300,
    config: Path | None = None,
    require_directories: bool = False,
) -> dict:
    root = root.resolve()
    report = {
        "schema_version": 2,
        "ok": True,
        "project": scan(root, excludes, details_limit),
        "third_party_assets": audit(root, excludes),
    }
    if config is not None:
        config_result = validate_config_file(
            config,
            root,
            require_directories,
        )
        report["config_validation"] = config_result
        report["ok"] = bool(config_result.get("valid", False))
    return report


def _operational_error(code: str, message: str, **details: object) -> dict:
    payload: dict[str, object] = {
        "schema_version": 1,
        "ok": False,
        "error": {
            "category": "operational",
            "code": code,
            "message": message,
        },
    }
    if details:
        payload["error"]["details"] = details  # type: ignore[index]
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".", help="Project root")
    ap.add_argument("--out", help="Optional combined JSON output path")
    ap.add_argument("--exclude", action="append", default=[], help="Extra glob/path exclusion; repeatable")
    ap.add_argument(
        "--details-limit",
        type=int,
        default=300,
        help=(
            "Maximum asset detail rows in the project inventory only. "
            "Third-party terms discovery is not truncated."
        ),
    )
    ap.add_argument("--config", help="Optional pipeline config JSON to validate")
    ap.add_argument(
        "--require-directories",
        action="store_true",
        help="With --config, treat missing configured working directories as validation errors",
    )
    args = ap.parse_args()

    try:
        report = build_report(
            Path(args.root),
            args.exclude,
            args.details_limit,
            Path(args.config) if args.config else None,
            args.require_directories,
        )
    except (OSError, ValueError) as exc:
        print(json.dumps(
            _operational_error("PROJECT_AUDIT_FAILED", str(exc), root=str(Path(args.root))),
            ensure_ascii=False,
            indent=2,
        ))
        return EXIT_OPERATIONAL_ERROR

    payload = json.dumps(report, ensure_ascii=False, indent=2)

    if args.out:
        out = Path(args.out)
        try:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload + "\n", encoding="utf-8")
        except OSError as exc:
            print(json.dumps(
                _operational_error("REPORT_WRITE_FAILED", str(exc), output=str(out)),
                ensure_ascii=False,
                indent=2,
            ))
            return EXIT_OPERATIONAL_ERROR

    print(payload)

    config_result = report.get("config_validation")
    if config_result is not None:
        return exit_code_for_result(config_result)
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
