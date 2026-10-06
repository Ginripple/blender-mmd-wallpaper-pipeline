# Originality and Related Work

`blender-mmd-wallpaper-pipeline` is published as an independently developed open-source Agent Skill focused on:

**PMX/MMD → Blender toon/NPR → animated or interactive wallpaper workflows.**

## What is distinctive about this project

The project combines several concerns that are usually handled separately:

- non-destructive PMX/MMD project and third-party-asset auditing;
- bounded Blender environment and scene inspection;
- toon/NPR and camera guidance for wallpaper-oriented presentation;
- phase-aware animation/runtime preparation;
- generated-artifact review and bounded traversal for large projects;
- structured agent evals and deterministic regression tests;
- context-efficient routing so references and diagnostics are loaded only when needed.

## Standard conventions are not claimed as original

This repository follows common Agent Skill conventions such as `SKILL.md`, `scripts/`, `references/`, `assets/`, and progressive disclosure of supporting material. These are ecosystem conventions and are not claimed as project-specific inventions.

Likewise, general engineering practices such as source preservation, reversible changes, tests, CI, structured JSON reports, and explicit license/terms review are common practices.

## Related public work reviewed before publication

A pre-publication search on 2026-10-07 found projects in adjacent areas, including:

- `Star-957/vrm-avatar-polish-loop` — VRM/MMD/Blender avatar repair, validation, evidence, and reversible candidate workflows.
- `CyclopsRay/2DCosplayerToMMD` — image-to-3D/MMD character generation, rigging, VMD motion, validation, and rendering.
- general Blender Agent Skills and Blender automation/MCP projects.
- wallpaper-generation and wallpaper-enhancement Agent Skills.

These projects overlap in domain vocabulary or general workflow principles, but their primary goals and implementations differ from this repository's MMD-to-Blender-to-wallpaper pipeline.

No source code from the projects listed above is incorporated into this repository unless a future change explicitly identifies that code, its license, and its attribution.

## If you find prior art or an accidental similarity

Open an issue with the repository/file and the specific overlapping section. The maintainers can review provenance, add attribution where appropriate, or revise wording/implementation if an accidental close similarity is discovered.
