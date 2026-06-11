from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CHECKS: list[tuple[str, list[str]]] = [
    (
        "docs_surface",
        [sys.executable, "tools/scripts/verify_docs_surface.py"],
    ),
    (
        "repo_structure",
        [sys.executable, "tools/scripts/verify_repo_structure.py"],
    ),
    (
        "docs_structure_publish_tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_docs_surface_consistency.py",
            "tests/test_repo_structure_consistency.py",
            "tests/test_publish_boundary.py",
        ],
    ),
    (
        "runtime_smoke_tests",
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_zuno_public_entrypoints.py",
            "src/backend/agentchat/test/test_zuno_alias_imports.py",
            "tests/test_zuno_runtime_chain_guard.py",
        ],
    ),
    (
        "import_zuno_main_smoke",
        [
            sys.executable,
            "-c",
            (
                "import importlib, sys; "
                "sys.path.insert(0, 'src/backend'); "
                "importlib.import_module('zuno.main'); "
                "print('phase7-zuno-main-smoke-ok')"
            ),
        ],
    ),
]


def _run_check(name: str, command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    combined_output = "\n".join(
        part.strip()
        for part in [result.stdout, result.stderr]
        if part and part.strip()
    ).strip()
    if result.returncode == 0:
        return True, combined_output
    error_text = combined_output or f"{name} failed with exit code {result.returncode}"
    return False, error_text


def main() -> int:
    for name, command in CHECKS:
        ok, output = _run_check(name, command)
        if not ok:
            print(f"[phase7_readiness:{name}] FAIL")
            print("command:", " ".join(command))
            print(output)
            print("Phase 7 readiness verification failed.")
            return 1

        print(f"[phase7_readiness:{name}] PASS")
        if output:
            print(output)

    print("Phase 7 readiness verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
