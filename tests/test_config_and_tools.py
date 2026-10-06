from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from list_generated import list_generated  # noqa: E402
from run_audit import build_report  # noqa: E402
from validate_config import validate_config_data, validate_config_file  # noqa: E402


class ConfigTests(unittest.TestCase):
    def _valid_config(self) -> dict:
        return {
            "schema_version": 1,
            "generated_prefixes": ["WP_", "TOON_", "TEST_"],
            "working_directories": ["working", "generated", "exports", "reports"],
            "camera": {
                "focus_name": "WP_Focus",
                "yaw_degrees": 15.0,
                "pitch_degrees": 8.0,
                "zoom_min": 0.9,
                "zoom_max": 1.1,
            },
            "preview": {
                "max_consecutive_inconclusive_renders": 2,
                "prefer_single_frame": True,
            },
            "runtime_target": {"width": 2560, "height": 1440, "fps": 60},
        }

    def test_example_config_is_schema_valid(self) -> None:
        result = validate_config_file(ROOT / "assets" / "config.example.json")
        self.assertTrue(result["valid"], result["errors"])

    def test_config_directory_checks_warn_or_fail_by_mode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            data = self._valid_config()
            relaxed = validate_config_data(data, root, require_directories=False)
            strict = validate_config_data(data, root, require_directories=True)
            self.assertTrue(relaxed["valid"])
            self.assertGreaterEqual(len(relaxed["warnings"]), 1)
            self.assertFalse(strict["valid"])
            self.assertGreaterEqual(len(strict["errors"]), 1)

    def test_config_rejects_bad_camera_range(self) -> None:
        data = self._valid_config()
        data["camera"]["yaw_degrees"] = 120
        data["camera"]["zoom_min"] = 1.2
        data["camera"]["zoom_max"] = 0.8
        result = validate_config_data(data)
        self.assertFalse(result["valid"])
        self.assertTrue(any("yaw_degrees" in x for x in result["errors"]))
        self.assertTrue(any("zoom_min must be <=" in x for x in result["errors"]))

    def test_run_audit_can_validate_config(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "char.pmx").write_bytes(b"pmx")
            config = root / "pipeline.json"
            config.write_text(json.dumps(self._valid_config()), encoding="utf-8")
            report = build_report(root, config=config)
            self.assertIn("config_validation", report)
            self.assertTrue(report["config_validation"]["valid"])

    def test_list_generated_is_read_only_and_respects_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "WP_preview.txt").write_text("x", encoding="utf-8")
            (root / "normal.txt").write_text("x", encoding="utf-8")
            (root / "TOON_cache").mkdir()
            (root / "TOON_cache" / "data.bin").write_bytes(b"x")
            report = list_generated(root)
            self.assertIn("WP_preview.txt", report["matching_files"])
            self.assertIn("TOON_cache", report["matching_directories"])
            self.assertNotIn("normal.txt", report["matching_files"])
            self.assertTrue((root / "WP_preview.txt").exists())

    def test_list_generated_max_depth_prunes_deep_tree(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "WP_root.txt").write_text("x", encoding="utf-8")
            level1 = root / "level1"
            level2 = level1 / "level2"
            level2.mkdir(parents=True)
            (level1 / "WP_one.txt").write_text("x", encoding="utf-8")
            (level2 / "WP_two.txt").write_text("x", encoding="utf-8")

            report0 = list_generated(root, max_depth=0)
            report1 = list_generated(root, max_depth=1)

            self.assertEqual(report0["matching_files"], ["WP_root.txt"])
            self.assertIn("level1/WP_one.txt", report1["matching_files"])
            self.assertNotIn("level1/level2/WP_two.txt", report1["matching_files"])
            self.assertEqual(report1["max_depth"], 1)

    def test_list_generated_rejects_negative_max_depth(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "max_depth must be >= 0"):
                list_generated(Path(td), max_depth=-1)


if __name__ == "__main__":
    unittest.main()
