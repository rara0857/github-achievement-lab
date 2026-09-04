import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_tracker.py"
SPEC = importlib.util.spec_from_file_location("validate_tracker", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


VALID_TRACKER = """\
version: 1
account: example
last_checked: 2026-09-05
achievements:
  - id: one
    status: earned
  - id: two
    status: pending
  - id: three
    status: planned
"""


class TrackerTests(unittest.TestCase):
    def test_summary_has_stable_status_order(self):
        self.assertEqual(
            MODULE.format_summary(VALID_TRACKER),
            "earned: 1\npending: 1\nplanned: 1",
        )

    def test_invalid_status_is_reported(self):
        errors = MODULE.validate_text(VALID_TRACKER.replace("status: pending", "status: unknown"))
        self.assertEqual(errors, ["Unknown status value: unknown"])

    def test_command_summary_uses_repository_tracker(self):
        with tempfile.TemporaryDirectory() as directory:
            tracker = Path(directory) / "achievements.yml"
            tracker.write_text(VALID_TRACKER, encoding="utf-8")
            original = MODULE.TRACKER
            try:
                MODULE.TRACKER = tracker
                self.assertEqual(MODULE.main(["--summary"]), 0)
            finally:
                MODULE.TRACKER = original


if __name__ == "__main__":
    unittest.main()
