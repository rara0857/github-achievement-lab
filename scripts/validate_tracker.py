"""Validate the small, dependency-free achievement tracker."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "achievements.yml"


def main() -> int:
    text = TRACKER.read_text(encoding="utf-8")
    required = ("version:", "account:", "last_checked:", "achievements:")
    missing = [marker for marker in required if marker not in text]
    if missing:
        print(f"Missing tracker sections: {', '.join(missing)}")
        return 1

    statuses = set(re.findall(r"^    status: (\w+)$", text, re.MULTILINE))
    allowed = {"earned", "pending", "planned"}
    unknown = statuses - allowed
    if unknown:
        print(f"Unknown status values: {', '.join(sorted(unknown))}")
        return 1

    urls = re.findall(r"https://github\.com/[^\s]+", text)
    if any(url.endswith(('.', ',', ')')) for url in urls):
        print("Evidence URL contains trailing punctuation")
        return 1

    print(f"Tracker OK: {len(statuses)} status types, {len(urls)} evidence URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
