# Changelog

## 0.1.1 — 2026-10-07

First public open-source release of the independently developed workflow skill, incorporating the full engineering review and release-hardening pass.

### Fixed
- Replaced free-form eval expectation strings with structured `field`/`operator`/`value` assertions.
- Made `evals/cases.schema.json` fully strict: it now validates the complete manifest, exact contract metadata, case shape, assertion field/operator compatibility, and assertion value types.
- Removed the hard-coded release number from version tests; `VERSION` is the source of truth and is checked as SemVer against README/CHANGELOG references.
- Defined stable CLI exit codes for `validate_config.py` and `run_audit.py`: `0` success, `1` operational error, `2` argparse usage error, `3` config validation failure.
- Converted `run_audit.py` operational failures into structured JSON instead of uncaught tracebacks.
- Added subprocess regression tests for success, validation failure, missing files/roots, report-write failure, and argparse errors.

### Changed
- Reworked `SKILL.md` into a smaller task router with narrower triggering guidance.
- Clarified that ordinary reversible work may continue inside the active phase, while phase crossing and destructive work require explicit intent.
- Replaced hard line/file-count stopping language with scope-aware checkpoints.
- Clarified “read-only” semantics: project assets are not modified; explicit `--out` report paths are writable.
- Refined toon/runtime/third-party guidance and separated version-sensitive Blender automation into its own reference.
- Reduced policy duplication in references by treating the stable red lines in `SKILL.md` as canonical.
- Refactored Blender build metadata conversion into `_safe_str()` for readability and bytes/str compatibility.
- Documented that `run_audit.py --details-limit` truncates only project inventory detail rows, not third-party audit entries.
- Added bounded traversal to `list_generated.py` through `--max-depth` so large projects can prune deep cleanup scans.

### Added
- MIT `LICENSE`, making the project explicitly open source for public GitHub release.
- `ORIGINALITY.md` documenting the project's scope, standard Agent Skill conventions, adjacent public work reviewed before publication, and the process for reporting accidental similarity.
- `ACKNOWLEDGEMENTS.md` clarifying ecosystem acknowledgements and the boundary between this repository's MIT-licensed code/documentation and third-party model assets.
- `scripts/run_audit.py` to combine inventory + terms discovery in one command.
- Default high-noise directory pruning and repeatable `--exclude` patterns.
- Compact report detail limits to reduce context/output size on large projects.
- `scripts/blender_probe.py` for Blender/Python/render/add-on environment inspection.
- `scripts/inspect_scene.py` for read-only scene inspection, including bone/Shape Key names, material→image references, physics hints, and best-effort MMD metadata without requiring a specific add-on.
- `scripts/validate_config.py` plus `run_audit.py --config` support so `assets/config.example.json` is validated and usable by tooling.
- `scripts/list_generated.py` to safely list likely `WP_`/`TOON_`/`TEST_` cleanup candidates without deleting anything.
- `assets/config.example.json` and `assets/THIRD_PARTY_ASSETS.template.md`.
- Expanded unit tests covering scanners, exclusions, combined audit behavior, config validation, generated-artifact listing, CLI report writing, JSON Schema validation, and pure Blender helper functions.
- `evals/cases.json` with structured agent-behavior eval cases and guidance separating model evals from deterministic Python tests.
- GitHub Actions workflow for CPython unit tests, strict eval-schema validation, and script compilation.

## 0.1.0 — 2026-10-07

Initial optimized baseline of the workflow skill.
