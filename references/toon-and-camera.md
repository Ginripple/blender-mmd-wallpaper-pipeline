# Toon/NPR and camera guidance

## Visual target

Aim for an anime illustration brought to life: controlled tonal separation, deliberate face/hair treatment, restrained specular response, and stable readability as the camera moves.

Avoid default MMD appearance, generic glossy/plastic PBR, uniformly thick pure-black outlines, and post effects that hide material problems.

## Materials

A practical starting structure is:
- face: dedicated shadow logic/control;
- hair: toon shadow plus stylized highlight/rim;
- eyes: separate handling where useful;
- skin/clothes/accessories: role-specific tuning;
- authored base textures preserved unless a working copy is intentionally created.

Centralize thresholds/softness/outline widths instead of scattering hard-coded values across scripts.

## Outline

Prototype one approach at a time, for example inverted hull, backface/material methods, Geometry Nodes, Line Art, or Freestyle. Do not assume one method is best across Blender versions and runtime targets.

Check silhouette stability, front-face occlusion, interior artifacts, transparency, normals, scale sensitivity, and camera-angle stability.

## Camera

Use an explicit focus object (for example `WP_Focus`) at the intended visual center. For interactive wallpaper, a reasonable starting envelope is yaw ±15°, pitch ±8°, zoom 0.9×–1.1× with smooth damping. Adjust to composition and clipping rather than treating these as mandatory constants.
