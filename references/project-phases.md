# Project phases

Use phases to prevent a successful audit from silently becoming a full visual/runtime rewrite.

## Phase 1 — Audit and infrastructure

Typical work:
- inventory PMX/PMD/VMD/VPD/BLEND/FBX/GLB/textures/reference files;
- identify likely source vs generated/output paths;
- inspect Blender version, renderer and add-ons;
- inspect objects, meshes, armatures, materials, images, Shape Keys and modifiers;
- create reports, config, inspectors and project scaffolding.

Exit when project state and major risks are understood. Enter Phase 2 when the user's goal includes visual/toon work.

## Phase 2 — Non-destructive toon preview

Typical work:
- copied/working materials;
- removable outline prototypes;
- dedicated test light/camera/focus objects;
- inexpensive representative still previews.

Keep experiments removable and avoid source overwrite. Validate the face, hair, transparency and silhouette over the intended camera range, not only one flattering angle.

## Phase 3 — Animation and runtime asset prep

Typical work:
- subtle breathing/blinking;
- light hair/clothing motion where appropriate;
- camera rig;
- FBX/GLB export tests;
- runtime-compatible material mapping.

Do not alter core rig hierarchy, weights, Morph semantics, or destructive mesh topology without explicit approval and a working-copy checkpoint.

## Phase 4 — Runtime integration

Integrate the tested asset into the selected runtime, implement interaction, profile performance, then optimize the measured bottleneck.

A default evaluation order may be Unity toon tooling, Godot 4, then WebGL/Three.js, but choose according to the actual deployment target rather than habit.
