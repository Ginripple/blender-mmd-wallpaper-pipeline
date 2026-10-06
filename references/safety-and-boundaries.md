# Safety and boundaries

`SKILL.md` is the canonical source for the stable red lines: preserve source assets, require intent for destructive/high-risk edits, and do not assume third-party reuse permission. This reference expands the operational checks used when one of those boundaries is relevant.

## Before a high-risk Blender operation

For decimate/remesh/retopology, Apply Transform/Modifier, bulk normal or UV rewrites, armature hierarchy edits, vertex-weight edits, Shape Key/Morph edits, destructive merge/delete operations, or source material/texture replacement:

1. verify the target is a working copy or that source modification was explicitly authorized;
2. scope the edit to named targets;
3. state likely effects on MMD compatibility, Shape Keys, rigging, and export;
4. validate the affected structure afterward.

## Git/filesystem

Do not use destructive recovery commands such as `git reset --hard`, `git clean -fd`, or forced checkout over user work without explicit intent. Do not delete unrelated files to “clean up” a project.

Generated helpers should be discoverable before cleanup. Use `scripts/list_generated.py` to list likely `WP_`, `TOON_`, and `TEST_` artifacts; deletion remains a separate, explicit action.

## Unknown compatibility

If Blender/add-on/exporter behavior is uncertain, inspect the actual version and make a minimal reproduction instead of guessing an old API name.
