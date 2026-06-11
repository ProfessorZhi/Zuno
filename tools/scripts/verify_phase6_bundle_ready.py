from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
PREVIEW_SCRIPT = REPO_ROOT / "tools" / "scripts" / "preview_phase6_bundle_scope.py"
EXPECTED_GROUP_COUNTS = {
    "docs_and_contract": 3,
    "logical_phase6_delta": 5,
    "eval_entrypoints": 4,
    "runtime_foundations": 6,
    "verification_tests": 19,
    "phase6_node_ops": 6,
}
EXPECTED_TOTAL = 43
REQUIRED_RECOMMENDATIONS = [
    "review docs_and_contract first to keep the closure claim honest",
    "then confirm logical_phase6_delta matches the direct Phase 6 behavior change",
    "on the current main base, keep eval_entrypoints and runtime_foundations together",
    "keep verification_tests with the final bundled node, not as a separate proof story",
    "keep phase6_node_ops with the same node so the staging contract stays reproducible",
]
EXPECTED_BUNDLE_SUBJECTS = {
    "phase6: close eval evidence bundle",
    "phase6: rebuild evidence bundle on foundation base",
}
RECENT_BUNDLE_SCAN_LIMIT = 8


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _find_matching_bundle_commit() -> tuple[str, str] | None:
    log_proc = _run(
        [
            "git",
            "log",
            f"-{RECENT_BUNDLE_SCAN_LIMIT}",
            "--pretty=%H%x09%s",
        ]
    )
    if log_proc.returncode != 0:
        return None

    for line in log_proc.stdout.splitlines():
        if not line.strip():
            continue
        commit_sha, _, subject = line.partition("\t")
        if subject.strip() not in EXPECTED_BUNDLE_SUBJECTS:
            continue

        paths_proc = _run(["git", "show", "--name-only", "--format=", commit_sha])
        if paths_proc.returncode != 0:
            continue

        paths = [entry.strip() for entry in paths_proc.stdout.splitlines() if entry.strip()]
        counts = _count_paths_against_groups(paths)
        total = sum(counts.values())
        if counts == EXPECTED_GROUP_COUNTS and total == EXPECTED_TOTAL:
            return commit_sha, subject.strip()

    return None


def _parse_summary(output: str) -> tuple[dict[str, int], int]:
    counts: dict[str, int] = {}
    total = -1
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and ": " in stripped and " changed" in stripped:
            item = stripped[2:]
            group_name, _, remainder = item.partition(": ")
            count_text, _, _ = remainder.partition(" changed")
            counts[group_name.strip()] = int(count_text.strip())
        if stripped.startswith("[phase6_bundle_total_changed]"):
            total = int(stripped.split("]", 1)[1].strip())
    return counts, total


def _parse_dry_run_counts(output: str) -> tuple[dict[str, int], int]:
    counts: dict[str, int] = {}
    total = 0
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("- ") and stripped.endswith(")") and " (" in stripped:
            item = stripped[2:]
            group_name, _, count_part = item.partition(" (")
            counts[group_name.strip()] = int(count_part[:-1])
            total += counts[group_name.strip()]
    return counts, total


def _load_preview_module():
    spec = importlib.util.spec_from_file_location("phase6_bundle_scope_verify", PREVIEW_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["phase6_bundle_scope_verify"] = module
    spec.loader.exec_module(module)
    return module


def _count_paths_against_groups(paths: list[str]) -> dict[str, int]:
    module = _load_preview_module()
    matched_prefixes = {group_name: set() for group_name in EXPECTED_GROUP_COUNTS}
    for path in paths:
        normalized = path.replace("\\", "/").strip()
        for group_name, prefixes in module.PHASE6_BUNDLE_GROUPS.items():
            matched_prefix = next(
                (
                    prefix
                    for prefix in prefixes
                    if normalized == prefix or normalized.startswith(prefix)
                ),
                None,
            )
            if matched_prefix is not None:
                matched_prefixes[group_name].add(matched_prefix)
                break
    return {
        group_name: len(prefixes)
        for group_name, prefixes in matched_prefixes.items()
    }


def main() -> int:
    summary = _run(["python", "tools/scripts/preview_phase6_bundle_scope.py", "--summary"])
    dry_run = _run(["python", "tools/scripts/preview_phase6_bundle_scope.py", "--dry-run"])

    if summary.returncode != 0:
        print(summary.stderr.strip() or summary.stdout.strip() or "phase6 summary failed")
        return 1
    if dry_run.returncode != 0:
        print(dry_run.stderr.strip() or dry_run.stdout.strip() or "phase6 dry run failed")
        return 1

    summary_counts, summary_total = _parse_summary(summary.stdout)
    dry_run_counts, dry_run_total = _parse_dry_run_counts(dry_run.stdout)

    errors: list[str] = []
    if summary_counts != EXPECTED_GROUP_COUNTS:
        errors.append(
            f"summary counts differ: expected={EXPECTED_GROUP_COUNTS} actual={summary_counts}"
        )
    if dry_run_counts != EXPECTED_GROUP_COUNTS:
        errors.append(
            f"dry-run counts differ: expected={EXPECTED_GROUP_COUNTS} actual={dry_run_counts}"
        )
    if summary_total != EXPECTED_TOTAL:
        errors.append(
            f"summary total differs: expected={EXPECTED_TOTAL} actual={summary_total}"
        )
    if dry_run_total != EXPECTED_TOTAL:
        errors.append(
            f"dry-run total differs: expected={EXPECTED_TOTAL} actual={dry_run_total}"
        )
    for recommendation in REQUIRED_RECOMMENDATIONS:
        if recommendation not in summary.stdout:
            errors.append(f"missing recommended sequence line: {recommendation}")
    if "[phase6_bundle_stage_command:all]" not in dry_run.stdout:
        errors.append("dry-run output missing final stage command")

    if errors:
        matching_commit = _find_matching_bundle_commit()
        if matching_commit is not None:
            commit_sha, subject = matching_commit
            print("phase6 bundle readiness check passed.")
            print("mode=matching_commit_history")
            for group_name, count in EXPECTED_GROUP_COUNTS.items():
                print(f"{group_name}={count}")
            print(f"total_changed={EXPECTED_TOTAL}")
            print(f"bundle_commit={commit_sha}")
            print(f"bundle_commit_subject={subject}")
            return 0

        for error in errors:
            print(f"ERROR: {error}")
        print("phase6 bundle readiness check failed.")
        return 1

    print("phase6 bundle readiness check passed.")
    print("mode=worktree")
    for group_name, count in EXPECTED_GROUP_COUNTS.items():
        print(f"{group_name}={count}")
    print(f"total_changed={EXPECTED_TOTAL}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
