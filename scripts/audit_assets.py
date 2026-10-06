#!/usr/bin/env python3
"""Locate likely license/terms documents near third-party model assets.

This is a discovery aid, not a legal-permission classifier. It does not copy,
modify, or interpret model assets or terms. Only --out writes a report file.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import walk_files

MODEL_EXTS = {".pmx", ".pmd", ".blend", ".fbx", ".glb", ".gltf", ".obj"}
TERMS_KEYWORDS = (
    "readme", "license", "licence", "terms", "利用規約", "規約", "禁止",
    "配布", "再配布", "改変", "credit", "credits", "作者", "author",
)


def is_terms_candidate(path: Path) -> bool:
    name = path.name.lower()
    return any(keyword.lower() in name for keyword in TERMS_KEYWORDS)


def collect_terms_files(root: Path, excludes: list[str] | None = None) -> list[Path]:
    return [p for p in walk_files(root, excludes) if is_terms_candidate(p)]


def nearby_terms(model: Path, project_root: Path, all_terms: list[Path]) -> list[str]:
    ancestors = set()
    current = model.parent.resolve()
    project_root = project_root.resolve()
    while True:
        try:
            current.relative_to(project_root)
        except ValueError:
            break
        ancestors.add(current)
        if current == project_root:
            break
        current = current.parent

    candidates = []
    for p in all_terms:
        # Same directory or any ancestor directory is strongest evidence.
        if p.parent.resolve() in ancestors:
            candidates.append(p.relative_to(project_root).as_posix())
            continue
        # Also allow a terms file one directory below the model directory
        # (common for docs/readme subfolders).
        try:
            rel = p.parent.resolve().relative_to(model.parent.resolve())
            if len(rel.parts) <= 1:
                candidates.append(p.relative_to(project_root).as_posix())
        except ValueError:
            pass
    return sorted(set(candidates))


def audit(root: Path, excludes: list[str] | None = None) -> dict:
    root = root.resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Project root is not a directory: {root}")

    files = list(walk_files(root, excludes))
    models = [p for p in files if p.suffix.lower() in MODEL_EXTS]
    all_terms = [p for p in files if is_terms_candidate(p)]

    entries = []
    for p in models:
        terms = nearby_terms(p, root, all_terms)
        entries.append({
            "asset": p.relative_to(root).as_posix(),
            "nearby_terms": terms,
            "permission_status": "REQUIRES_HUMAN_REVIEW",
            "risk": "NO_NEARBY_TERMS_FOUND" if not terms else "TERMS_FOUND_NOT_INTERPRETED",
        })

    return {
        "schema_version": 2,
        "root": str(root),
        "model_asset_count": len(models),
        "terms_candidate_count": len(all_terms),
        "assets": entries,
        "terms_candidates": sorted(p.relative_to(root).as_posix() for p in all_terms),
        "extra_excludes": excludes or [],
        "warning": (
            "This script only locates possible terms/readme files. It does not determine whether "
            "reuse, transfer, redistribution, derivative work, or commercial use is allowed."
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default=".", help="Project root")
    ap.add_argument("--out", help="Optional JSON output path")
    ap.add_argument("--exclude", action="append", default=[], help="Extra glob/path exclusion; repeatable")
    args = ap.parse_args()

    report = audit(Path(args.root), args.exclude)
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
