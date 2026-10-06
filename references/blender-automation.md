# Blender automation and inspection

Use this reference when Blender version, add-ons, scene structure, or API compatibility matters. The stable safety contract lives in `SKILL.md`; this file contains implementation detail rather than redefining those red lines.

## Read-only first

Prefer a read-only probe before writing version-sensitive `bpy` automation.

### Environment probe

```bash
blender --background project.blend --python scripts/blender_probe.py -- --out reports/blender-probe.json
```

Reports Blender/Python version, active render engine, resolution, active camera, installed add-ons, linked libraries, and selected API capability indicators. It does not save the `.blend` file.

### Scene inspection

```bash
blender --background project.blend --python scripts/inspect_scene.py -- --out reports/scene.json
```

Reports generic Blender structure plus best-effort MMD-relevant evidence:

- object types and modifiers;
- mesh vertex/edge/polygon counts;
- material slots and material → image-texture references;
- Shape Key counts and names;
- armature bone counts and names;
- Blender rigid bodies and rigid-body constraints;
- exposed `mmd_type` hints and display-frame names when an installed add-on makes those properties available;
- linked libraries, images, and missing external paths;
- generated/test-prefixed objects.

The MMD-specific fields are intentionally **best effort** and do not import or require a particular MMD add-on. If deeper MMD structure auditing is required—such as add-on-specific Morph categories, physics metadata, display-item contents, or exporter-only structures—extend inspection on a working copy and gate it to the detected add-on/API version rather than assuming one implementation.

Use `--member-limit` to cap bone/Shape Key/display-frame names when reports would otherwise become too large.

## Version-sensitive code

Before using an API that may differ by Blender version:

1. record `bpy.app.version`;
2. inspect the relevant type/property in the installed Blender;
3. isolate the smallest script that proves the API behavior;
4. only then integrate it into the project workflow.

Do not guess renamed/deprecated properties from memory when a probe can answer the question.

## Write scripts

When a task genuinely needs scene changes, use an explicitly designated working file, scope edits to named targets, keep generated helpers removable, log what changed, and make destinations explicit. Prefer idempotent or safely rerunnable operations when practical.
