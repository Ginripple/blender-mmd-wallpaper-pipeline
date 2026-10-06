from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def valid_config() -> dict:
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


class CliContractTests(unittest.TestCase):
    def _run(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_validate_config_success_is_zero(self) -> None:
        completed = self._run("validate_config.py", str(ROOT / "assets" / "config.example.json"))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertTrue(payload["valid"])

    def test_validate_config_content_failure_is_three(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "bad.json"
            data = valid_config()
            data["camera"]["yaw_degrees"] = 999
            config.write_text(json.dumps(data), encoding="utf-8")
            completed = self._run("validate_config.py", str(config))
            self.assertEqual(completed.returncode, 3, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["valid"])
            self.assertEqual(payload["error_code"], "CONFIG_VALIDATION_FAILED")

    def test_validate_config_invalid_json_is_three(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            config = Path(td) / "broken.json"
            config.write_text("{not json", encoding="utf-8")
            completed = self._run("validate_config.py", str(config))
            self.assertEqual(completed.returncode, 3, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["error_code"], "CONFIG_INVALID_JSON")

    def test_validate_config_missing_file_is_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing.json"
            completed = self._run("validate_config.py", str(missing))
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["error_code"], "CONFIG_FILE_NOT_FOUND")
            self.assertTrue(payload["operational_errors"])

    def test_validate_config_argparse_error_remains_two(self) -> None:
        completed = self._run("validate_config.py", "--unknown-option")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("usage:", completed.stderr.lower())

    def test_run_audit_success_is_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "char.pmx").write_bytes(b"pmx")
            completed = self._run("run_audit.py", str(root))
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["project"]["asset_count"], 1)

    def test_run_audit_invalid_root_is_one_with_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            missing = Path(td) / "missing-root"
            completed = self._run("run_audit.py", str(missing))
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["category"], "operational")
            self.assertEqual(payload["error"]["code"], "PROJECT_AUDIT_FAILED")
            self.assertNotIn("Traceback", completed.stderr)

    def test_run_audit_invalid_config_is_three(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "char.pmx").write_bytes(b"pmx")
            config = root / "pipeline.json"
            data = valid_config()
            data["camera"]["pitch_degrees"] = 999
            config.write_text(json.dumps(data), encoding="utf-8")
            completed = self._run("run_audit.py", str(root), "--config", str(config))
            self.assertEqual(completed.returncode, 3, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["config_validation"]["error_code"], "CONFIG_VALIDATION_FAILED")

    def test_run_audit_missing_config_is_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            completed = self._run(
                "run_audit.py",
                str(root),
                "--config",
                str(root / "missing.json"),
            )
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["config_validation"]["error_code"], "CONFIG_FILE_NOT_FOUND")

    def test_run_audit_report_write_failure_is_one(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            completed = self._run("run_audit.py", str(root), "--out", str(root))
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["ok"])
            self.assertEqual(payload["error"]["code"], "REPORT_WRITE_FAILED")

    def test_run_audit_argparse_error_remains_two(self) -> None:
        completed = self._run("run_audit.py", "--unknown-option")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("usage:", completed.stderr.lower())

    def test_list_generated_negative_max_depth_is_argparse_two(self) -> None:
        completed = self._run("list_generated.py", ".", "--max-depth", "-1")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("must be >= 0", completed.stderr)


if __name__ == "__main__":
    unittest.main()
