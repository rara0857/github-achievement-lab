"""Validate the small, dependency-free achievement tracker."""

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "achievements.yml"
STATUS_ORDER = ("earned", "pending", "planned")


def validate_text(text: str) -> list[str]:
    """Return validation errors for tracker text."""
    required = ("version:", "account:", "last_checked:", "achievements:")
    errors = [f"Missing tracker section: {marker}" for marker in required if marker not in text]

    statuses = set(re.findall(r"^    status: (\w+)$", text, re.MULTILINE))
    unknown = statuses - set(STATUS_ORDER)
    errors.extend(f"Unknown status value: {status}" for status in sorted(unknown))

    urls = re.findall(r"https://github\.com/[^\s]+", text)
    if any(url.endswith((".", ",", ")")) for url in urls):
        errors.append("Evidence URL contains trailing punctuation")
    return errors


def summarize(text: str) -> dict[str, int]:
    """Count tracker entries by status in a stable order."""
    statuses = re.findall(r"^    status: (\w+)$", text, re.MULTILINE)
    return {status: statuses.count(status) for status in STATUS_ORDER}


def format_summary(text: str) -> str:
    counts = summarize(text)
    return "\n".join(f"{status}: {counts[status]}" for status in STATUS_ORDER)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = TRACKER.read_text(encoding="utf-8")
    errors = validate_text(text)
    if errors:
        print("\n".join(errors))
        return 1

    if "--summary" in argv:
        print(format_summary(text))
    else:
        statuses = summarize(text)
        urls = re.findall(r"https://github\.com/[^\s]+", text)
        print(f"Tracker OK: {sum(statuses.values())} entries, {len(urls)} evidence URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
