#!/usr/bin/env python3
"""Read-only Blender environment probe.

Run with Blender, for example:
  blender --background project.blend --python scripts/blender_probe.py -- --out reports/blender-probe.json

The script does not save the .blend file or modify project assets.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path


def _script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def _safe_str(value) -> str:
    """Convert Blender build metadata to text across bytes/str API variants."""
    if isinstance(value, (bytes, bytearray)):
        return value.decode(errors="replace")
    return "" if value is None else str(value)


def main() -> None:
    try:
        import bpy  # type: ignore
    except ImportError as exc:
        raise SystemExit("blender_probe.py must be run by Blender's Python interpreter") from exc

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="Optional JSON output path")
    args = ap.parse_args(_script_args())

    prefs = bpy.context.preferences
    addon_modules = sorted(getattr(prefs, "addons", {}).keys())
    render = bpy.context.scene.render

    report = {
        "schema_version": 1,
        "read_only": True,
        "blender": {
            "version": bpy.app.version_string,
            "version_tuple": list(bpy.app.version),
            "background": bool(bpy.app.background),
            "build_branch": _safe_str(getattr(bpy.app, "build_branch", "")),
            "build_hash": _safe_str(getattr(bpy.app, "build_hash", "")),
            "file": bpy.data.filepath or None,
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "scene": {
            "name": bpy.context.scene.name,
            "render_engine": render.engine,
            "resolution_x": render.resolution_x,
            "resolution_y": render.resolution_y,
            "resolution_percentage": render.resolution_percentage,
            "frame_start": bpy.context.scene.frame_start,
            "frame_end": bpy.context.scene.frame_end,
            "fps": render.fps,
            "active_camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
        },
        "addons": addon_modules,
        "capabilities": {
            "geometry_nodes": hasattr(bpy.types, "GeometryNodeTree"),
            "grease_pencil": hasattr(bpy.types, "GreasePencil"),
            "lineart_modifier_type_exposed": hasattr(bpy.types, "LineartGpencilModifier"),
        },
        "linked_libraries": sorted(lib.filepath for lib in bpy.data.libraries if lib.filepath),
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
