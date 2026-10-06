#!/usr/bin/env python3
"""Read-only Blender scene inspector for MMD/toon wallpaper projects.

Run with Blender, for example:
  blender --background project.blend --python scripts/inspect_scene.py -- --out reports/scene.json

It reports generic Blender structure plus best-effort MMD hints without requiring a
specific MMD add-on. It never saves the .blend file.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def _script_args() -> list[str]:
    return sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def _abs_blender_path(bpy, path: str) -> str:
    if not path:
        return ""
    try:
        return bpy.path.abspath(path)
    except Exception:
        return path


def _limited_names(items: Iterable, limit: int) -> tuple[list[str], int]:
    names = [str(getattr(item, "name", item)) for item in items]
    limit = max(0, limit)
    return names[:limit], max(0, len(names) - limit)


def _mmd_type(obj) -> str | None:
    """Best-effort mmd_tools-style object type without importing the add-on."""
    try:
        value = getattr(obj, "mmd_type", None)
        if value:
            return str(value)
    except Exception:
        pass
    try:
        value = obj.get("mmd_type")
        if value:
            return str(value)
    except Exception:
        pass
    return None


def _display_frame_names(obj, limit: int) -> tuple[list[str], int]:
    """Read mmd_tools display frames if an exposed property group is present."""
    try:
        root = getattr(obj, "mmd_root", None)
        frames = getattr(root, "display_item_frames", None) if root else None
        if frames is None:
            return [], 0
        return _limited_names(frames, limit)
    except Exception:
        return [], 0


def _material_image_refs(material, bpy) -> list[dict]:
    tree = getattr(material, "node_tree", None)
    if not tree:
        return []
    refs = []
    seen = set()
    for node in tree.nodes:
        if getattr(node, "type", None) != "TEX_IMAGE":
            continue
        image = getattr(node, "image", None)
        if image is None:
            continue
        key = (node.name, image.name)
        if key in seen:
            continue
        seen.add(key)
        raw = getattr(image, "filepath", "") or getattr(image, "filepath_raw", "")
        refs.append({
            "node": node.name,
            "image": image.name,
            "path": raw or None,
            "resolved": _abs_blender_path(bpy, raw) or None,
        })
    return refs


def main() -> None:
    try:
        import bpy  # type: ignore
    except ImportError as exc:
        raise SystemExit("inspect_scene.py must be run by Blender's Python interpreter") from exc

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", help="Optional JSON output path")
    ap.add_argument("--object-limit", type=int, default=300, help="Maximum object detail rows")
    ap.add_argument(
        "--member-limit",
        type=int,
        default=200,
        help="Maximum bone/Shape Key/display-frame names per object",
    )
    args = ap.parse_args(_script_args())

    object_counts = Counter(obj.type for obj in bpy.data.objects)
    objects = []
    generated = []
    prefixes = ("WP_", "TOON_", "TEST_")
    mmd_type_counts: Counter[str] = Counter()
    mmd_objects: dict[str, list[str]] = defaultdict(list)
    rigid_body_objects: list[str] = []
    rigid_body_constraints: list[str] = []
    display_frames: list[dict] = []
    material_users: dict[str, set[str]] = defaultdict(set)

    for obj in bpy.data.objects:
        for slot in getattr(obj, "material_slots", []):
            material = getattr(slot, "material", None)
            if material:
                material_users[material.name].add(obj.name)
        mmd_type = _mmd_type(obj)
        if mmd_type:
            mmd_type_counts[mmd_type] += 1
            mmd_objects[mmd_type].append(obj.name)
        if getattr(obj, "rigid_body", None) is not None:
            rigid_body_objects.append(obj.name)
        if getattr(obj, "rigid_body_constraint", None) is not None:
            rigid_body_constraints.append(obj.name)
        frame_names, omitted_frames = _display_frame_names(obj, args.member_limit)
        if frame_names or omitted_frames:
            display_frames.append({
                "object": obj.name,
                "names": frame_names,
                "omitted_names": omitted_frames,
            })

    for obj in list(bpy.data.objects)[: max(0, args.object_limit)]:
        row = {
            "name": obj.name,
            "type": obj.type,
            "collection_names": sorted(c.name for c in obj.users_collection),
            "parent": obj.parent.name if obj.parent else None,
            "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers],
        }
        mmd_type = _mmd_type(obj)
        if mmd_type:
            row["mmd_type_hint"] = mmd_type
        if obj.name.startswith(prefixes):
            generated.append(obj.name)
        if obj.type == "MESH" and getattr(obj, "data", None):
            mesh = obj.data
            shape_keys = getattr(mesh, "shape_keys", None)
            shape_blocks = list(shape_keys.key_blocks) if shape_keys else []
            shape_names, omitted_shapes = _limited_names(shape_blocks, args.member_limit)
            row["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "polygons": len(mesh.polygons),
                "materials": [slot.material.name if slot.material else None for slot in obj.material_slots],
                "shape_key_count": len(shape_blocks),
                "shape_key_names": shape_names,
                "omitted_shape_key_names": omitted_shapes,
            }
        elif obj.type == "ARMATURE" and getattr(obj, "data", None):
            bones = list(obj.data.bones)
            bone_names, omitted_bones = _limited_names(bones, args.member_limit)
            row["armature"] = {
                "bone_count": len(bones),
                "bone_names": bone_names,
                "omitted_bone_names": omitted_bones,
            }
        objects.append(row)

    missing_paths = []
    images = []
    for image in bpy.data.images:
        raw = getattr(image, "filepath", "") or getattr(image, "filepath_raw", "")
        resolved = _abs_blender_path(bpy, raw)
        packed = bool(getattr(image, "packed_file", None))
        exists = True if packed or not resolved else os.path.exists(resolved)
        if raw and not exists:
            missing_paths.append({"kind": "image", "name": image.name, "path": raw, "resolved": resolved})
        images.append({
            "name": image.name,
            "path": raw or None,
            "packed": packed,
            "source": getattr(image, "source", None),
            "exists": exists,
        })

    libraries = []
    for lib in bpy.data.libraries:
        raw = lib.filepath
        resolved = _abs_blender_path(bpy, raw)
        exists = os.path.exists(resolved) if resolved else True
        if raw and not exists:
            missing_paths.append({"kind": "library", "name": lib.name, "path": raw, "resolved": resolved})
        libraries.append({"name": lib.name, "path": raw, "resolved": resolved or None, "exists": exists})

    materials = []
    for mat in bpy.data.materials:
        materials.append({
            "name": mat.name,
            "use_nodes": bool(getattr(mat, "use_nodes", False)),
            "node_count": len(mat.node_tree.nodes) if getattr(mat, "node_tree", None) else 0,
            "objects_using": sorted(material_users.get(mat.name, set())),
            "image_textures": _material_image_refs(mat, bpy),
        })

    report = {
        "schema_version": 2,
        "read_only": True,
        "blend_file": bpy.data.filepath or None,
        "scene": bpy.context.scene.name,
        "active_camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
        "object_type_counts": dict(sorted(object_counts.items())),
        "objects": objects,
        "omitted_object_details": max(0, len(bpy.data.objects) - len(objects)),
        "materials": materials,
        "images": images,
        "linked_libraries": libraries,
        "missing_external_paths": missing_paths,
        "generated_or_test_objects": sorted(generated),
        "physics": {
            "rigid_body_objects": sorted(rigid_body_objects),
            "rigid_body_constraint_objects": sorted(rigid_body_constraints),
        },
        "mmd_hints": {
            "object_type_counts": dict(sorted(mmd_type_counts.items())),
            "objects_by_mmd_type": {k: sorted(v) for k, v in sorted(mmd_objects.items())},
            "display_frames": display_frames,
            "note": (
                "MMD fields are best-effort introspection of exposed Blender/add-on properties; "
                "no MMD add-on is imported or required."
            ),
        },
        "summary": {
            "objects": len(bpy.data.objects),
            "materials": len(bpy.data.materials),
            "images": len(bpy.data.images),
            "armatures": object_counts.get("ARMATURE", 0),
            "meshes": object_counts.get("MESH", 0),
            "rigid_body_objects": len(rigid_body_objects),
            "rigid_body_constraints": len(rigid_body_constraints),
            "mmd_typed_objects": sum(mmd_type_counts.values()),
            "missing_external_paths": len(missing_paths),
        },
    }

    payload = json.dumps(report, ensure_ascii=False, indent=2)
    print(payload)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(payload + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
