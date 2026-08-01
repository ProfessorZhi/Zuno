from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List


REQUIRED_SECTIONS = [
    "## Agent Attribution",
    "## Current",
    "## Evidence",
    "## Tests Run",
    "## Tests Not Run",
    "## Not Claimed",
]


def verify_agent_pr_body(file_path: Path) -> bool:
    if not file_path.exists():
        print(f"PR Body file does not exist: {file_path}", file=sys.stderr)
        return False

    content = file_path.read_text(encoding="utf-8", errors="replace")
    errors: List[str] = []

    for section in REQUIRED_SECTIONS:
        if section not in content:
            errors.append(f"Missing required section: '{section}'")

    if errors:
        print(f"PR Body Verification Failed for {file_path}:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return False

    print(f"PR Body Verification Passed for {file_path}.")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Agent PR Body Sections")
    parser.add_argument("--file", required=True, help="Path to PR body markdown file")

    args = parser.parse_args()
    file_path = Path(args.file)

    if not verify_agent_pr_body(file_path):
        sys.exit(1)


if __name__ == "__main__":
    main()
