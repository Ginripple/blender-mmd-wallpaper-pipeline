from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterator

# Stable CLI exit-code contract shared by command-line scripts.
EXIT_SUCCESS = 0
EXIT_OPERATIONAL_ERROR = 1
EXIT_USAGE_ERROR = 2  # Reserved for argparse usage/argument errors.
EXIT_VALIDATION_FAILED = 3

DEFAULT_IGNORED_DIRS = {
    ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".idea", ".vscode", ".venv", "venv", "env",
    "node_modules", "cache", ".cache", "temp", "tmp", "renders",
}


def _matches_pattern(rel: Path, pattern: str) -> bool:
    posix = rel.as_posix()
    return fnmatch.fnmatch(posix, pattern) or any(
        fnmatch.fnmatch(part, pattern) for part in rel.parts
    )


def walk_files(
    root: Path,
    extra_excludes: list[str] | None = None,
    max_depth: int | None = None,
) -> Iterator[Path]:
    """Yield files under root while pruning noise and optionally bounding depth.

    Depth is measured from the project root: root files are depth 0, files in a
    direct child directory are depth 1, and so on. ``max_depth`` prunes
    traversal instead of merely filtering yielded results.
    """
    root = root.resolve()
    patterns = [p for p in (extra_excludes or []) if p]
    if max_depth is not None and max_depth < 0:
        raise ValueError("max_depth must be >= 0")

    for current, dirs, files in os.walk(root):
        current_path = Path(current)
        rel_current = current_path.relative_to(root)
        current_depth = 0 if rel_current == Path(".") else len(rel_current.parts)

        kept_dirs: list[str] = []
        for dirname in dirs:
            rel = rel_current / dirname
            if dirname.lower() in DEFAULT_IGNORED_DIRS:
                continue
            if any(_matches_pattern(rel, pat) for pat in patterns):
                continue
            kept_dirs.append(dirname)
        dirs[:] = [] if max_depth is not None and current_depth >= max_depth else kept_dirs

        for filename in files:
            p = current_path / filename
            rel = p.relative_to(root)
            if any(_matches_pattern(rel, pat) for pat in patterns):
                continue
            yield p
