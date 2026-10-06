# Efficient workflow / quota discipline

Use this reference when the task is looping, repeatedly launching Blender, rescanning a large project, or rendering more than necessary.

## Evidence loop

1. Reuse current reports/config if project state is still compatible.
2. Form one concrete hypothesis.
3. Pick the cheapest test that distinguishes it.
4. Make one reversible change when a change is necessary.
5. Verify the affected behavior.
6. Stop when the requested outcome is achieved.

For the same unresolved issue, after two failed automatic fixes, stop editing and switch to diagnosis. After two inconclusive preview renders, do the same unless the user explicitly asks for further visual iteration.

## Render ladder

Prefer, when sufficient:

1. viewport/material preview;
2. isolated object/material;
3. single frame;
4. crop or low resolution;
5. low samples;
6. representative final-quality still;
7. full animation sequence only when the task actually requires it.

Do not validate shader wiring with a final-resolution animation render.

## Context discipline

- Keep stable policy in this skill.
- Keep mutable project state in project config/reports.
- Prefer `scripts/run_audit.py` over separate broad rescans when both inventory and terms discovery are needed.
- Cap report detail for large projects; counts and risk summaries are often enough.
- Read only the reference relevant to the current task.
- Summarize diffs instead of restating whole files.

## Scope checkpoint

If the implementation expands well beyond the user's stated goal (for example, many unrelated files or a technology-route change), summarize the expanded scope before continuing into that new problem. Do not stop ordinary safe work merely because a numeric line-count threshold was crossed.
