---
name: blender-mmd-wallpaper-pipeline
description: Audit and develop PMX/MMD character projects into non-destructive Blender toon/NPR wallpaper pipelines. Use for MMD asset audits, toon previews, camera/animation/export prep, or wallpaper runtime integration; not for generic Blender modeling.
---

# Blender MMD Wallpaper Pipeline

Use this skill for PMX/MMD character work that is specifically headed toward a Blender toon/NPR preview, animated wallpaper, or runtime wallpaper pipeline.

Do **not** load it for unrelated Blender modeling, sculpting, ordinary rendering, generic Unity/Godot work, or non-MMD projects.

## Core contract

1. Preserve original assets.
2. Establish the current project phase before broad changes.
3. Prefer evidence and reversible tests over speculative edits.
4. Continue safe work inside the current phase to completion; do not cross into the next phase without the user's intent.
5. Treat third-party asset presence as **not** granting reuse permission.

Original/source PMX, PMD, VMD, VPD, BLEND, FBX, GLB, textures, readmes, and license/terms files are read-only unless the user explicitly authorizes a source change. Prefer `working/`, `generated/`, `exports/`, and `reports/` for derived work.

For destructive geometry, rig, weight, Morph/Shape Key, UV, Apply Modifier/Transform, source material replacement, or destructive Git actions, use [references/safety-and-boundaries.md](references/safety-and-boundaries.md).

## Route by task

- **Project inventory / unknown project state:** run `scripts/run_audit.py` or `scripts/check_project.py`; optionally validate project settings with `scripts/validate_config.py`; then read [references/project-phases.md](references/project-phases.md).
- **Third-party mesh/texture/material reuse:** run `scripts/audit_assets.py`; then read [references/third-party-assets.md](references/third-party-assets.md).
- **Blender version / add-on / renderer uncertainty:** run `scripts/blender_probe.py` through Blender; then read [references/blender-automation.md](references/blender-automation.md).
- **Scene structure / missing textures / armature / Morph / modifier inspection:** run `scripts/inspect_scene.py` through Blender.
- **Generated/test artifact review before cleanup:** run `scripts/list_generated.py`; listing is read-only and deletion remains explicit.
- **Toon material, outline, lighting, camera:** read [references/toon-and-camera.md](references/toon-and-camera.md).
- **Animation, FBX/GLB, engine/runtime work:** read [references/runtime-pipeline.md](references/runtime-pipeline.md).
- **Repeated failures or expensive renders:** read [references/efficient-workflow.md](references/efficient-workflow.md).

Do not read every reference by default. Load only what the current task needs.

## Phase boundary

Use these four phases:

1. **Audit / infrastructure** — inventory, environment, inspectors, reports, scaffolding.
2. **Non-destructive toon preview** — copied materials, removable outline tests, test lighting/camera, cheap still previews.
3. **Animation / runtime asset prep** — subtle motion, camera rig, export tests, runtime-compatible mapping.
4. **Runtime integration** — Unity/Godot/WebGL integration and performance work.

A successful task does not imply permission to enter the next phase. Within the current phase, continue through ordinary reversible implementation and validation without asking at every small step.

## Cost discipline

Use the smallest useful evidence-gathering step first. Reuse recent reports when project state has not changed materially. Prefer one-object/one-material/one-frame tests before full-scene or animation renders.

For the same unresolved issue, after **2 failed automatic fix attempts** or **2 inconclusive preview renders**, stop changing things and report the evidence and remaining hypotheses instead of looping.

## Blender scripting defaults

Prefer small idempotent `bpy` modules, explicit object identifiers, `pathlib`, and generated prefixes such as `WP_`, `TOON_`, and `TEST_`. Avoid hard-coded user paths and selection-state-only logic. Important automation should be runnable from Blender CLI when practical.

Do not assume a specific Blender major version. Probe the installed version/API before relying on version-sensitive shader, Grease Pencil, Line Art, exporter, or add-on behavior.

## Third-party assets

Visual study is allowed. Directly copying another model's authored mesh, texture pixels, material, bone, Morph, animation, or proprietary configuration requires relevant terms to allow that use. When unclear, report the uncertainty and prefer an independently recreated equivalent.

## Default visual/runtime target

Treat the visual direction as an anime illustration brought to life rather than generic glossy PBR: controlled 2–3 tone shading, dedicated face handling, restrained outline/post effects, and angle-stable presentation.

For an interactive wallpaper camera, use an explicit visual focus and start around yaw ±15°, pitch ±8°, and zoom 0.9×–1.1× unless the project specifies otherwise. Profile before aggressive geometry reduction.

## Output contract

Before substantial work, state only the current phase, goal, scope, and validation method. After work, summarize changed files, validation result, risk/blocker, and the next phase-safe step. Put verbose machine-readable diagnostics in `reports/` rather than flooding chat.
