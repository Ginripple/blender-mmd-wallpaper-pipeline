from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from _common import walk_files  # noqa: E402
from audit_assets import audit  # noqa: E402
from check_project import scan  # noqa: E402
from run_audit import build_report  # noqa: E402


class ScannerTests(unittest.TestCase):
    def test_inventory_counts_assets_and_prunes_noise(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "source").mkdir()
            (root / "source" / "character.pmx").write_bytes(b"pmx")
            (root / "textures").mkdir()
            (root / "textures" / "face.png").write_bytes(b"png")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "ignored.png").write_bytes(b"png")
            (root / "README.md").write_text("terms", encoding="utf-8")

            report = scan(root)
            self.assertEqual(report["asset_count"], 2)
            self.assertEqual(report["asset_group_counts"]["model"], 1)
            self.assertEqual(report["asset_group_counts"]["texture"], 1)
            self.assertIn("source/character.pmx", report["source_like_paths"])
            self.assertIn("README.md", report["documentation_candidates"])

    def test_details_limit_keeps_counts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(5):
                (root / f"x{i}.png").write_bytes(b"x")
            report = scan(root, details_limit=2)
            self.assertEqual(report["asset_count"], 5)
            self.assertEqual(len(report["assets"]), 2)
            self.assertEqual(report["omitted_asset_details"], 3)

    def test_terms_audit_finds_parent_readme(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pack = root / "third_party_model"
            model_dir = pack / "model"
            model_dir.mkdir(parents=True)
            (model_dir / "char.pmx").write_bytes(b"pmx")
            (pack / "利用規約.txt").write_text("rules", encoding="utf-8")

            report = audit(root)
            self.assertEqual(report["model_asset_count"], 1)
            entry = report["assets"][0]
            self.assertIn("third_party_model/利用規約.txt", entry["nearby_terms"])
            self.assertEqual(entry["permission_status"], "REQUIRES_HUMAN_REVIEW")

    def test_explicit_exclude(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "old_backups").mkdir()
            (root / "old_backups" / "old.pmx").write_bytes(b"pmx")
            (root / "live.pmx").write_bytes(b"pmx")
            report = scan(root, excludes=["old_backups/*"])
            self.assertEqual(report["asset_count"], 1)
            self.assertEqual(report["assets"][0]["path"], "live.pmx")

    def test_walk_files_prunes_default_and_explicit_excludes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "keep").mkdir()
            (root / "keep" / "a.txt").write_text("a", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "noise.txt").write_text("x", encoding="utf-8")
            (root / "old_backups").mkdir()
            (root / "old_backups" / "old.txt").write_text("x", encoding="utf-8")

            rels = {
                p.relative_to(root.resolve()).as_posix()
                for p in walk_files(root, ["old_backups/*"])
            }
            self.assertEqual(rels, {"keep/a.txt"})

    def test_walk_files_max_depth_prunes_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "root.txt").write_text("r", encoding="utf-8")
            (root / "one" / "two").mkdir(parents=True)
            (root / "one" / "one.txt").write_text("1", encoding="utf-8")
            (root / "one" / "two" / "two.txt").write_text("2", encoding="utf-8")

            depth0 = {p.relative_to(root.resolve()).as_posix() for p in walk_files(root, max_depth=0)}
            depth1 = {p.relative_to(root.resolve()).as_posix() for p in walk_files(root, max_depth=1)}

            self.assertEqual(depth0, {"root.txt"})
            self.assertEqual(depth1, {"root.txt", "one/one.txt"})

    def test_combined_audit_preserves_unlimited_terms_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for i in range(4):
                (root / f"model{i}.pmx").write_bytes(b"pmx")
            (root / "README_terms.txt").write_text("rules", encoding="utf-8")

            report = build_report(root, details_limit=1)
            self.assertEqual(len(report["project"]["assets"]), 1)
            self.assertEqual(report["project"]["asset_count"], 4)
            self.assertEqual(report["third_party_assets"]["model_asset_count"], 4)
            self.assertEqual(len(report["third_party_assets"]["assets"]), 4)

    def test_run_audit_cli_writes_combined_json(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "char.pmx").write_bytes(b"pmx")
            out = root / "reports" / "audit.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "run_audit.py"),
                    str(root),
                    "--out",
                    str(out),
                    "--details-limit",
                    "0",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            stdout_report = json.loads(completed.stdout)
            disk_report = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(stdout_report["project"]["asset_count"], 1)
            self.assertEqual(disk_report, stdout_report)
            self.assertEqual(stdout_report["project"]["assets"], [])
            self.assertEqual(stdout_report["third_party_assets"]["model_asset_count"], 1)


if __name__ == "__main__":
    unittest.main()
