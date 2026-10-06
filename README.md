# Blender MMD Wallpaper Pipeline Skill

An **open-source** Codex/OpenAI Agent Skill for **PMX/MMD → Blender toon/NPR → animated or interactive wallpaper** work, with a strong bias toward source preservation, cheap diagnosis, third-party asset awareness, and phase-safe automation.

## What this skill is

This is primarily a **workflow + inspection skill**, not a one-click MMD converter. It helps an agent decide what to inspect, what is safe to change, which project phase it is in, and when to stop speculative Blender/render loops.

Version **0.1.1** is the first public open-source release, with stricter eval contracts, bounded generated-artifact scanning, release-grade regression checks, and an explicit MIT license.

## Layout

```text
blender-mmd-wallpaper-pipeline/
├─ SKILL.md
├─ README.md
├─ CHANGELOG.md
├─ LICENSE
├─ ORIGINALITY.md
├─ ACKNOWLEDGEMENTS.md
├─ VERSION
├─ assets/
│  ├─ config.example.json
│  ├─ phase-report-template.md
│  └─ THIRD_PARTY_ASSETS.template.md
├─ evals/
│  ├─ README.md
│  ├─ cases.json
│  └─ cases.schema.json
├─ references/
├─ scripts/
│  ├─ _common.py
│  ├─ audit_assets.py
│  ├─ blender_probe.py
│  ├─ check_project.py
│  ├─ inspect_scene.py
│  ├─ list_generated.py
│  ├─ run_audit.py
│  └─ validate_config.py
└─ tests/
```

## Install as a Skill

Upload/import the whole `blender-mmd-wallpaper-pipeline` directory, or a ZIP containing that **single top-level folder**. The required manifest is `SKILL.md`.

The root manifest is intentionally short. It routes the agent to a reference or script only when the current task needs it, reducing unnecessary context.

## Useful commands

### Fast combined project audit

```bash
python scripts/run_audit.py . --out reports/project-audit.json
```

Extra noisy paths can be excluded repeatedly:

```bash
python scripts/run_audit.py . \
  --exclude "downloads/*" \
  --exclude "old_backups/*" \
  --out reports/project-audit.json
```

`--details-limit` applies only to detailed rows in the **project inventory**. Asset counts remain complete, and third-party model/terms discovery is not truncated by that option.

The scanners ignore common noise such as `.git`, virtual environments, `node_modules`, caches, temp folders, and `renders` by default.

### Validate the pipeline config

The example config is executable documentation rather than an unused sample:

```bash
python scripts/validate_config.py assets/config.example.json --project-root .
```

It validates `schema_version`, generated prefixes, camera ranges, preview/runtime values, and configured working directories. Missing working directories are warnings by default because they may not exist yet. Use `--require-directories` to make missing directories validation errors.

The combined audit can validate a config in the same run:

```bash
python scripts/run_audit.py . \
  --config assets/config.example.json \
  --out reports/project-audit.json
```

### CLI exit-code contract

`validate_config.py` and `run_audit.py` use a stable exit-code contract so CI and agent harnesses do not have to infer failure types from tracebacks:

```text
0 = success
1 = operational/filesystem error
2 = command-line usage error (reserved for argparse)
3 = configuration content/validation failure
```

Tool-generated success/failure payloads are JSON on stdout. `argparse` keeps its normal usage/error text on stderr for exit code `2`. Operational failures such as a missing project root or an unwritable report path are converted to structured JSON rather than an uncaught traceback.

### Blender environment probe

Run through Blender, not system Python:

```bash
blender --background project.blend \
  --python scripts/blender_probe.py -- \
  --out reports/blender-probe.json
```

### Blender scene inspection

```bash
blender --background project.blend \
  --python scripts/inspect_scene.py -- \
  --out reports/scene.json
```

The scene inspector reports generic Blender data plus best-effort MMD hints including bone names, Shape Key names, rigid-body/constraint objects, exposed MMD object types/display frames, and material→image references. It does not import or require a specific MMD add-on.

Both Blender scripts are designed to **inspect without saving the `.blend` file**. They only write the explicit `--out` report when requested.

## How to review generated/test artifacts before cleanup

Generated helpers should use configured prefixes such as `WP_`, `TOON_`, and `TEST_`. Before deleting anything, list likely generated artifacts:

```bash
python scripts/list_generated.py . --config assets/config.example.json
```

On very large projects, bound traversal depth to keep cleanup reports compact:

```bash
python scripts/list_generated.py . --max-depth 3
```

Depth `0` scans only files in the project root; depth `1` also scans direct child directories, and so on. The option prunes traversal rather than merely hiding deeper results.

This command is read-only: it only lists matching files/directories. It intentionally does **not** delete them. Review the list first, then remove only artifacts you are sure are disposable. Blender objects with the same prefixes are also reported by `inspect_scene.py`; remove them only from a working `.blend` or another explicitly authorized target.

## Suggested first prompt

> Use `blender-mmd-wallpaper-pipeline`. Audit the current PMX/MMD wallpaper project and determine the current phase. Preserve source assets. Reuse existing reports if still valid. Do not start a toon rewrite or runtime integration unless that is already within the requested phase.

## Third-party models and materials

The skill treats another model's presence in a folder as **not** granting permission to copy its textures, meshes, materials, Morphs, or animation. `scripts/audit_assets.py` only finds likely nearby terms; it intentionally leaves permission interpretation to a human/agent review.

## Development checks

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py
```

The deterministic tests exercise scanner behavior, exclusions, combined audit output, config validation, generated-artifact listing, and pure Blender-script helpers. Blender-specific runtime behavior should additionally be smoke-tested inside every Blender version claimed as supported.

Agent behavior cases—routing, phase discipline, permission reasoning, and render-loop stopping—are defined separately in `evals/cases.json`. Their expectations use structured assertions (`field` / `operator` / `value`), and `evals/cases.schema.json` strictly validates the complete manifest, including valid field/operator/value combinations. A harness still needs an adapter that normalizes its own trace into the documented result contract.

A GitHub Actions workflow is included to run the CPython unit/compile checks on pushes and pull requests.

## Open-source license

This project is open source under the [MIT License](LICENSE). You may use, copy, modify, merge, publish, distribute, sublicense, and sell copies of this project's code and documentation subject to the license terms.

The MIT License covers **this repository's own code and documentation only**. It does not grant rights to third-party PMX/PMD/VMD/VPD/BLEND/FBX/GLB files, textures, motions, character designs, or other assets that users process with the skill. Review the applicable asset terms separately.

For the project's originality boundary and adjacent public work reviewed before publication, see [ORIGINALITY.md](ORIGINALITY.md). General ecosystem acknowledgements and third-party attribution policy are in [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md).

## Contributing

Issues and pull requests are welcome. Contributions should preserve the project's non-destructive defaults, structured CLI contracts, bounded scans, and test coverage. Any contribution that incorporates third-party code or data should identify its upstream source, license, and required attribution.

## Safety note

“Read-only” here means the inspectors do not intentionally modify project assets or save the Blender project. Any script called with `--out` can create or overwrite that explicitly named report file.
