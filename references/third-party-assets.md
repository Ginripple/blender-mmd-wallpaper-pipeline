# Third-party asset policy

`SKILL.md` contains the canonical rule: asset presence is not reuse permission. This reference describes how to review a reuse request.

## Visual-reference path

For stockings/black-silk, hair highlights, skin, clothing, or similar effects, prefer studying the visual result and general technique, then recreating an independent material/configuration on the target model. Avoid copying source-authored texture pixels, geometry, Morphs, animation, or proprietary configuration unless the terms allow it.

## Direct-reuse path

Before direct reuse, locate nearby README/LICENSE/terms/利用規約/author notes. `scripts/audit_assets.py` helps locate candidates but deliberately does not interpret permission.

Record, when known, in `THIRD_PARTY_ASSETS.md`: resource/source, author, terms location, modification permission, cross-model transfer permission, redistribution permission, commercial-use permission, credit requirement, and unresolved restrictions.

If the permission needed for the requested reuse is ambiguous, report the uncertainty and prefer an independently recreated equivalent where possible.

This workflow reduces project risk; it is not legal advice.
