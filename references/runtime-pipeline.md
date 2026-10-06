# Runtime pipeline

A typical path is:

PMX/MMD → Blender audit → non-destructive toon preview → animation/export prep → FBX/GLB test → runtime prototype → profile → final wallpaper integration.

## Runtime choice

- **Unity:** strong first candidate when character-focused toon rendering and established toon tooling matter most.
- **Godot 4:** attractive when an open-source/lighter project workflow is preferred.
- **WebGL/Three.js:** useful when browser-style deployment or a small runtime footprint materially matters.

Do not choose an engine solely because its first prototype appears easiest.

## Export verification

Verify only the data the project actually needs: armature, animation, required BlendShapes/Shape Keys, material/texture references, scale/orientation, naming, and runtime performance.

Do not decimate simply because the asset will run in real time. Profile first, then optimize the measured bottleneck.

For interactive wallpaper, start with a constrained camera around an explicit focus rather than unrestricted 360° orbit unless unrestricted orbit is a stated product requirement.
