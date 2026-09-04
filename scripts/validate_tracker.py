"""Validate the small, dependency-free achievement tracker."""

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "achievements.yml"
STATUS_ORDER = ("earned", "pending", "planned")
AVAILABILITY_VALUES = {"current", "experimental", "retired"}


def validate_text(text: str) -> list[str]:
    """Return validation errors for tracker text."""
    required = ("version:", "account:", "last_checked:", "achievements:")
    errors = [f"Missing tracker section: {marker}" for marker in required if marker not in text]

    statuses = set(re.findall(r"^    status: (\w+)$", text, re.MULTILINE))
    unknown = statuses - set(STATUS_ORDER)
    errors.extend(f"Unknown status value: {status}" for status in sorted(unknown))

    availability = set(re.findall(r"^    availability: (\w+)$", text, re.MULTILINE))
    unknown_availability = availability - AVAILABILITY_VALUES
    errors.extend(
        f"Unknown availability value: {value}" for value in sorted(unknown_availability)
    )

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


def metadata(text: str) -> dict[str, str]:
    values = {}
    for key in ("account", "last_checked"):
        match = re.search(rf"^{key}:\s*(.+)$", text, re.MULTILINE)
        if match:
            values[key] = match.group(1).strip()
    return values


def format_json(text: str) -> str:
    payload = {
        **metadata(text),
        "counts": summarize(text),
    }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    text = TRACKER.read_text(encoding="utf-8")
    errors = validate_text(text)
    if errors:
        print("\n".join(errors))
        return 1

    if "--json" in argv:
        print(format_json(text))
    elif "--summary" in argv:
        print(format_summary(text))
    else:
        statuses = summarize(text)
        urls = re.findall(r"https://github\.com/[^\s]+", text)
        print(f"Tracker OK: {sum(statuses.values())} entries, {len(urls)} evidence URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
