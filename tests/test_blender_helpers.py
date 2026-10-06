from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from blender_probe import _safe_str  # noqa: E402
from inspect_scene import _limited_names  # noqa: E402


class BlenderHelperTests(unittest.TestCase):
    def test_safe_str_handles_bytes_str_and_none(self) -> None:
        self.assertEqual(_safe_str(b"main"), "main")
        self.assertEqual(_safe_str("release"), "release")
        self.assertEqual(_safe_str(None), "")

    def test_limited_names_caps_detail_without_losing_omitted_count(self) -> None:
        names, omitted = _limited_names(["a", "b", "c"], 2)
        self.assertEqual(names, ["a", "b"])
        self.assertEqual(omitted, 1)


if __name__ == "__main__":
    unittest.main()
