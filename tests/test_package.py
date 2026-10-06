from __future__ import annotations

import json
import re
import unittest
from copy import deepcopy

from jsonschema import Draft202012Validator, ValidationError
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


class PackageTests(unittest.TestCase):
    def test_skill_frontmatter_exists(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertRegex(text, r"(?m)^name:\s*blender-mmd-wallpaper-pipeline\s*$")
        self.assertRegex(text, r"(?m)^description:\s*.+$")

    def _assert_local_markdown_links_exist(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        local_links = [x for x in links if not x.startswith(("http://", "https://", "#"))]
        for link in local_links:
            target = (path.parent / link).resolve()
            self.assertTrue(target.exists(), f"{path.relative_to(ROOT)} -> {link}")

    def test_skill_local_links_exist(self) -> None:
        self._assert_local_markdown_links_exist(ROOT / "SKILL.md")

    def test_reference_local_links_exist(self) -> None:
        for path in (ROOT / "references").glob("*.md"):
            self._assert_local_markdown_links_exist(path)

    def test_version_is_semver_and_matches_docs(self) -> None:
        version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

        self.assertRegex(version, SEMVER_RE)
        self.assertIn(f"Version **{version}**", readme)
        self.assertRegex(changelog, rf"(?m)^##\s+{re.escape(version)}(?:\s|—|$)")


    def test_open_source_license_is_present_and_documented(self) -> None:
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertTrue(license_text.startswith("MIT License\n"))
        self.assertIn("[MIT License](LICENSE)", readme)
        self.assertNotIn("does **not** choose a public software license", readme)
        self.assertTrue((ROOT / "ORIGINALITY.md").is_file())
        self.assertTrue((ROOT / "ACKNOWLEDGEMENTS.md").is_file())

    def _eval_schema_and_data(self) -> tuple[dict, dict]:
        schema = json.loads((ROOT / "evals" / "cases.schema.json").read_text(encoding="utf-8"))
        data = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        return schema, data

    def test_eval_json_schema_is_valid_and_manifest_conforms(self) -> None:
        schema, data = self._eval_schema_and_data()
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], 2)
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(data)

    def test_eval_schema_rejects_wrong_assertion_value_type(self) -> None:
        schema, data = self._eval_schema_and_data()
        bad = deepcopy(data)
        bad["cases"][0]["assertions"][0]["value"] = "true"
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(bad)

    def test_eval_schema_rejects_invalid_field_operator_combination(self) -> None:
        schema, data = self._eval_schema_and_data()
        bad = deepcopy(data)
        bad["cases"][0]["assertions"][0] = {
            "field": "skill_selected",
            "operator": "contains",
            "value": "true",
        }
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(bad)

    def test_eval_schema_rejects_contract_drift_and_extra_fields(self) -> None:
        schema, data = self._eval_schema_and_data()
        validator = Draft202012Validator(schema)

        bad_contract = deepcopy(data)
        bad_contract["result_contract"]["phase"] = "number|null"
        with self.assertRaises(ValidationError):
            validator.validate(bad_contract)

        extra = deepcopy(data)
        extra["cases"][0]["unexpected"] = True
        with self.assertRaises(ValidationError):
            validator.validate(extra)

    def test_eval_manifest_has_machine_parseable_assertions(self) -> None:
        data = json.loads((ROOT / "evals" / "cases.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 2)

        contract = data["assertion_contract"]
        allowed_fields = set(contract["fields"])
        allowed_operators = set(contract["operators"])
        self.assertTrue(allowed_fields)
        self.assertEqual(allowed_operators, {"eq", "contains", "not_contains"})

        cases = data["cases"]
        ids = [case["id"] for case in cases]
        self.assertGreaterEqual(len(cases), 7)
        self.assertEqual(len(ids), len(set(ids)))

        for case in cases:
            self.assertTrue(case["prompt"].strip())
            self.assertNotIn("expect", case)
            assertions = case.get("assertions")
            self.assertIsInstance(assertions, list)
            self.assertTrue(assertions)
            for assertion in assertions:
                self.assertEqual(set(assertion), {"field", "operator", "value"})
                self.assertIn(assertion["field"], allowed_fields)
                self.assertIn(assertion["operator"], allowed_operators)

                if assertion["operator"] == "eq" and assertion["field"] == "skill_selected":
                    self.assertIsInstance(assertion["value"], bool)
                if assertion["operator"] in {"contains", "not_contains"}:
                    self.assertIsInstance(assertion["value"], str)
                    self.assertTrue(assertion["value"].strip())


if __name__ == "__main__":
    unittest.main()
