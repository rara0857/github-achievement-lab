import importlib.util
import contextlib
import io
import json
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
    name: One
    availability: current
    status: earned
    evidence:
      - https://github.com/example/repo/issues/1
    note: Evidence exists.
  - id: two
    name: Two
    availability: current
    status: pending
    evidence: []
    note: Waiting for confirmation.
  - id: three
    name: Three
    availability: retired
    status: planned
    evidence: []
    note: Historical event.
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

    def test_invalid_availability_is_reported(self):
        tracker = VALID_TRACKER.replace("availability: current", "availability: mystery", 1)
        self.assertEqual(MODULE.validate_text(tracker), ["Unknown availability value: mystery"])

    def test_earned_entry_requires_evidence(self):
        tracker = VALID_TRACKER.replace(
            "    evidence:\n      - https://github.com/example/repo/issues/1",
            "    evidence: []",
        )
        self.assertEqual(
            MODULE.validate_text(tracker),
            ["Entry one: earned status requires evidence"],
        )

    def test_retired_entry_must_remain_planned(self):
        tracker = VALID_TRACKER.replace("availability: retired\n    status: planned", "availability: retired\n    status: pending")
        self.assertEqual(
            MODULE.validate_text(tracker),
            ["Entry three: retired entries must remain planned"],
        )

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

    def test_json_output_contains_metadata_and_counts(self):
        payload = json.loads(MODULE.format_json(VALID_TRACKER))
        self.assertEqual(payload["account"], "example")
        self.assertEqual(payload["last_checked"], "2026-09-05")
        self.assertEqual(payload["counts"], {"earned": 1, "pending": 1, "planned": 1})

    def test_invalid_json_command_returns_error_without_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            tracker = Path(directory) / "achievements.yml"
            tracker.write_text(VALID_TRACKER.replace("status: pending", "status: unknown"), encoding="utf-8")
            original = MODULE.TRACKER
            output = io.StringIO()
            try:
                MODULE.TRACKER = tracker
                with contextlib.redirect_stdout(output):
                    result = MODULE.main(["--json"])
            finally:
                MODULE.TRACKER = original
            self.assertEqual(result, 1)
            self.assertIn("Unknown status value: unknown", output.getvalue())
            self.assertNotIn('"counts"', output.getvalue())


if __name__ == "__main__":
    unittest.main()
