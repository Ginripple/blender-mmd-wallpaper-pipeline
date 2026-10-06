#!/usr/bin/env python3
"""List generated/test-prefixed files and directories without deleting them.

This helper is intentionally read-only. It can read generated prefixes from the
project config so users can review likely cleanup targets before removing any
artifacts manually or with an explicitly authorized cleanup step.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import walk_files

DEFAULT_PREFIXES = ("WP_", "TOON_", "TEST_")


def _load_prefixes(config: Path | None) -> tuple[str, ...]:
    if config is None:
        return DEFAULT_PREFIXES
    data = json.loads(config.read_text(encoding="utf-8"))
    values = data.get("generated_prefixes", [])
    prefixes = tuple(v for v in values if isinstance(v, str) and v)
    return prefixes or DEFAULT_PREFIXES


def list_generated(
    root: Path,
    prefixes: tuple[str, ...] = DEFAULT_PREFIXES,
    excludes: list[str] | None = None,
    max_depth: int | None = None,
) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    files = []
    dirs: set[str] = set()
    for path in walk_files(root, excludes, max_depth=max_depth):
        rel = path.relative_to(root)
        if path.name.startswith(prefixes):
            files.append(rel.as_posix())
        for parent in rel.parents:
            if parent == Path("."):
                continue
            if parent.name.startswith(prefixes):
                dirs.add(parent.as_posix())

    return {
        "schema_version": 1,
        "read_only": True,
        "root": str(root),
        "prefixes": list(prefixes),
        "max_depth": max_depth,
        "matching_files": sorted(files),
        "matching_directories": sorted(dirs),
        "note": "Review these paths before cleanup. This script never deletes them.",
    }


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".", help="Project root")
    ap.add_argument("--config", help="Optional config JSON used to load generated_prefixes")
    ap.add_argument("--exclude", action="append", default=[], help="Extra glob/path exclusion; repeatable")
    ap.add_argument(
        "--max-depth",
        type=_non_negative_int,
        default=None,
        help="Maximum directory depth to traverse (0 = project root only)",
    )
    args = ap.parse_args()
    report = list_generated(
        Path(args.root),
        _load_prefixes(Path(args.config)) if args.config else DEFAULT_PREFIXES,
        args.exclude,
        args.max_depth,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
