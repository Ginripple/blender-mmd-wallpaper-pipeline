# Testing and evaluation

Use this reference when changing the skill itself or preparing a public release.

## Deterministic package tests

Run from the skill root:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py
```

The unit tests cover package structure, local links, project scanning, terms discovery, default/external exclusions, combined audit behavior, config validation, generated-artifact listing, and pure helper functions used by the Blender scripts.

The Blender-only scripts cannot be fully exercised by ordinary CPython because `bpy` is available only inside Blender. At minimum, compile them with CPython and run smoke tests with each Blender major/minor version you claim to support.

## Agent behavior evals

Routing, phase discipline, third-party permission reasoning, and repeated-render stopping are **agent behaviors**, not deterministic Python functions. They should be evaluated with an actual agent/model harness rather than faked as unit tests.

Machine-readable cases live in `evals/cases.json`, with a strict Draft 2020-12 JSON Schema in `evals/cases.schema.json`. The schema validates the complete manifest, including field/operator/value compatibility for every assertion. Each case uses structured assertions over a normalized harness result (`skill_selected`, `phase`, `behaviors`, `actions`, `tool_calls`) rather than free-form expectation strings. Current cases cover:

1. audit-only behavior;
2. negative routing for an unrelated generic Blender task;
3. third-party material reuse;
4. phase-boundary discipline;
5. safe continuation inside Phase 2;
6. unknown/version-sensitive Blender API use;
7. repeated preview/render failure.

For every release candidate, record model/config/tool availability, the normalized harness result, per-assertion pass/fail, and a short failure note. Harness-specific traces should be converted by a small adapter; the eval case file itself should remain harness-neutral. A longer prompt is not automatically a safer or more effective skill.

## CLI contract tests

`tests/test_cli_contract.py` executes `validate_config.py` and `run_audit.py` as subprocesses and verifies the stable exit codes: `0` success, `1` operational/filesystem error, `2` argparse usage error, and `3` configuration validation failure. This protects agent/CI integrations from accidental interface drift.
