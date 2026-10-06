#!/usr/bin/env python3
"""Fast, non-destructive inventory for Blender/MMD wallpaper projects.

The scanner never changes project assets. It writes only the explicitly requested
report path passed with --out.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from _common import DEFAULT_IGNORED_DIRS, walk_files

ASSET_GROUPS = {
    "model": {".pmx", ".pmd", ".fbx", ".glb", ".gltf", ".obj"},
    "animation": {".vmd", ".vpd", ".bvh"},
    "blender": {".blend"},
    "texture": {".png", ".jpg", ".jpeg", ".webp", ".tga", ".bmp", ".dds", ".exr", ".hdr", ".ktx", ".ktx2"},
    "audio": {".wav", ".mp3", ".ogg", ".flac", ".m4a"},
    "video": {".mp4", ".webm", ".mov", ".mkv"},
}
ALL_ASSET_EXTS = set().union(*ASSET_GROUPS.values())
DOC_KEYWORDS = ("readme", "license", "licence", "terms", "利用規約", "規約", "禁止", "配布", "credit")
SOURCE_HINTS = {"source", "sources", "original", "orig", "原始", "原版", "元データ"}
OUTPUT_HINTS = {"generated", "working", "exports", "export", "reports", "preview", "previews"}


def _group_for(ext: str) -> str:
    for group, exts in ASSET_GROUPS.items():
        if ext in exts:
            return group
    return "other"


def scan(root: Path, excludes: list[str] | None = None, details_limit: int = 500) -> dict:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    ext_counts: Counter[str] = Counter()
    group_counts: Counter[str] = Counter()
    asset_details: list[dict] = []
    docs: list[str] = []
    source_like: set[str] = set()
    output_like: set[str] = set()
    scanned_files = 0
    total_assets = 0

    for p in walk_files(root, excludes):
        scanned_files += 1
        rel = p.relative_to(root)
        rel_posix = rel.as_posix()
        lower_parts = {part.lower() for part in rel.parts}
        ext = p.suffix.lower()

        if lower_parts & SOURCE_HINTS:
            source_like.add(rel_posix)
        if lower_parts & OUTPUT_HINTS:
            output_like.add(rel_posix)

        name_lower = p.name.lower()
        if any(keyword in name_lower for keyword in DOC_KEYWORDS):
            docs.append(rel_posix)

        if ext in ALL_ASSET_EXTS:
            total_assets += 1
            ext_counts[ext] += 1
            group = _group_for(ext)
            group_counts[group] += 1
            if len(asset_details) < max(0, details_limit):
                try:
                    size = p.stat().st_size
                except OSError:
                    size = None
                asset_details.append({
                    "path": rel_posix,
                    "group": group,
                    "ext": ext,
                    "size_bytes": size,
                })

    return {
        "schema_version": 2,
        "root": str(root),
        "scanned_file_count": scanned_files,
        "asset_count": total_assets,
        "asset_group_counts": dict(sorted(group_counts.items())),
        "asset_extension_counts": dict(sorted(ext_counts.items())),
        "assets": asset_details,
        "omitted_asset_details": max(0, total_assets - len(asset_details)),
        "source_like_paths": sorted(source_like),
        "output_like_paths": sorted(output_like),
        "documentation_candidates": sorted(set(docs)),
        "default_ignored_directories": sorted(DEFAULT_IGNORED_DIRS),
        "extra_excludes": excludes or [],
        "notes": [
            "Inventory is non-destructive; only --out writes a report file.",
            "Asset presence does not imply permission to reuse, transfer, or redistribute it.",
            "Asset details are capped to keep reports compact; counts still cover all scanned assets.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".", help="Project root (default: current directory)")
    ap.add_argument("--out", help="Optional JSON output path")
    ap.add_argument("--exclude", action="append", default=[], help="Extra glob/path exclusion; repeatable")
    ap.add_argument("--details-limit", type=int, default=500, help="Maximum asset detail rows (default: 500)")
    args = ap.parse_args()

    report = scan(Path(args.root), args.exclude, args.details_limit)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
