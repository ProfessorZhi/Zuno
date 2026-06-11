from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMMANDS: list[list[str]] = [
    ["python", "tools/scripts/verify_public_demo_docs.py"],
    ["python", "tools/scripts/verify_repo_structure.py"],
    ["pytest", "-q", "tests/test_publish_boundary.py"],
    ["pytest", "-q", "tests/test_repo_structure_consistency.py"],
]


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    for cmd in COMMANDS:
        proc = _run(cmd)
        if proc.returncode != 0:
            print(f"ERROR: command failed: {' '.join(cmd)}")
            print(proc.stdout.strip())
            print(proc.stderr.strip())
            print("phase7 readiness check failed.")
            return 1

    print("phase7 readiness check passed.")
    for cmd in COMMANDS:
        print(" ".join(cmd))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
