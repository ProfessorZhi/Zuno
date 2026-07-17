from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / ".agent" / "programs" / "work-products" / "requirement-ledger.yaml"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _path_exists(ref: str) -> bool:
    path = ref.split(":", 1)[0]
    if not path or path.startswith("needs_evidence") or path.startswith("EV-"):
        return False
    return (REPO_ROOT / path).exists()


def verify_requirement_ledger_evidence_gate() -> list[str]:
    errors: list[str] = []
    data = yaml.safe_load(LEDGER.read_text(encoding="utf-8"))
    requirements = list(data.get("requirements") or [])
    actual_counts = Counter(str(item.get("current_status")) for item in requirements)
    declared_counts = dict(data.get("current_status_counts") or {})
    if dict(actual_counts) != declared_counts:
        errors.append(
            f"current_status_counts mismatch: declared={declared_counts!r} actual={dict(actual_counts)!r}"
        )

    for item in requirements:
        if item.get("current_status") != "implementation_available":
            continue
        requirement_id = str(item.get("requirement_id") or "<missing>")
        current_paths = _as_list(item.get("current_paths"))
        test_ids = _as_list(item.get("test_ids"))
        evidence_refs = _as_list(item.get("evidence_refs"))
        reverse_refs = _as_list(item.get("reverse_trace_refs"))

        if not current_paths:
            errors.append(
                f"{requirement_id} has implementation_available without current_paths"
            )
        if not any(_path_exists(path) for path in current_paths):
            errors.append(f"{requirement_id} has no existing current path")
        if all(path.startswith("docs/modules/") for path in current_paths):
            errors.append(f"{requirement_id} only points current_paths at target docs")

        if not test_ids:
            errors.append(
                f"{requirement_id} has implementation_available without test_ids"
            )
        if any(
            test_id.startswith(("INFRA-", "AGENT-", "MODEL-", "SEC-"))
            for test_id in test_ids
        ):
            errors.append(
                f"{requirement_id} still uses planned test ids as current tests"
            )
        path_like_tests = [
            test_id for test_id in test_ids if test_id.startswith(("tests/", "tools/"))
        ]
        if path_like_tests and not all(
            _path_exists(test_id) for test_id in path_like_tests
        ):
            errors.append(
                f"{requirement_id} references missing test path(s): {path_like_tests!r}"
            )

        if not evidence_refs:
            errors.append(
                f"{requirement_id} has implementation_available without evidence_refs"
            )
        if any(ref.startswith("needs_evidence") for ref in evidence_refs):
            errors.append(
                f"{requirement_id} still uses needs_evidence as current evidence"
            )
        path_like_evidence = [
            ref for ref in evidence_refs if ref.startswith(("docs/", ".agent/"))
        ]
        if path_like_evidence and not all(
            _path_exists(ref) for ref in path_like_evidence
        ):
            errors.append(
                f"{requirement_id} references missing evidence path(s): {path_like_evidence!r}"
            )

        required_prefixes = ("target:", "current:", "test:", "evidence:")
        for prefix in required_prefixes:
            if not any(ref.startswith(prefix) for ref in reverse_refs):
                errors.append(f"{requirement_id} reverse_trace_refs missing {prefix}")

    return errors


def main() -> int:
    errors = verify_requirement_ledger_evidence_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Requirement ledger evidence gate failed.")
        return 1
    print("Requirement ledger evidence gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
