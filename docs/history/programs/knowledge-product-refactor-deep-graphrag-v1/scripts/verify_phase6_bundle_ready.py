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
    "runtime_foundations": 22,
    "verification_tests": 20,
    "phase6_node_ops": 6,
}
EXPECTED_TOTAL = 60
REQUIRED_RECOMMENDATIONS = [
    "review docs_and_contract first to keep the closure claim honest",
    "then confirm logical_phase6_delta matches the direct Phase 6 behavior change",
    "if branch base lacks earlier foundations, include eval_entrypoints and runtime_foundations together",
    "keep verification_tests with the final bundled node, not as a separate proof story",
    "keep phase6_node_ops with the same node so the staging contract stays reproducible",
]
EXPECTED_PRIMARY_COMMIT_SUBJECT = "phase6: solidify eval evidence bundle"
EXPECTED_FOLLOWUP_COMMIT_SUBJECT = "phase6: sync local node readiness state"


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


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
    counts = {group_name: 0 for group_name in EXPECTED_GROUP_COUNTS}
    for path in paths:
        normalized = path.replace("\\", "/").strip()
        for group_name, prefixes in module.PHASE6_BUNDLE_GROUPS.items():
            if any(normalized == prefix or normalized.startswith(prefix) for prefix in prefixes):
                counts[group_name] += 1
                break
    return counts


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
        head_subject = _run(["git", "log", "-1", "--pretty=%s"])
        head_paths_proc = _run(["git", "show", "--name-only", "--format=", "HEAD"])
        if head_subject.returncode == 0 and head_paths_proc.returncode == 0:
            head_paths = [line.strip() for line in head_paths_proc.stdout.splitlines() if line.strip()]
            head_counts = _count_paths_against_groups(head_paths)
            head_total = sum(head_counts.values())
            head_errors: list[str] = []
            if head_subject.stdout.strip() != EXPECTED_PRIMARY_COMMIT_SUBJECT:
                head_errors.append(
                    f"head subject differs: expected={EXPECTED_PRIMARY_COMMIT_SUBJECT!r} actual={head_subject.stdout.strip()!r}"
                )
            if head_counts != EXPECTED_GROUP_COUNTS:
                head_errors.append(
                    f"head commit counts differ: expected={EXPECTED_GROUP_COUNTS} actual={head_counts}"
                )
            if head_total != EXPECTED_TOTAL:
                head_errors.append(
                    f"head commit total differs: expected={EXPECTED_TOTAL} actual={head_total}"
                )
            if not head_errors:
                print("phase6 bundle readiness check passed.")
                print("mode=head_commit")
                for group_name, count in EXPECTED_GROUP_COUNTS.items():
                    print(f"{group_name}={count}")
                print(f"total_changed={EXPECTED_TOTAL}")
                print(f"head_commit_subject={head_subject.stdout.strip()}")
                return 0

        range_subjects = _run(["git", "log", "-2", "--pretty=%s"])
        range_paths_proc = _run(["git", "diff", "--name-only", "HEAD~2..HEAD"])
        if range_subjects.returncode == 0 and range_paths_proc.returncode == 0:
            subjects = [line.strip() for line in range_subjects.stdout.splitlines() if line.strip()]
            range_paths = [line.strip() for line in range_paths_proc.stdout.splitlines() if line.strip()]
            range_counts = _count_paths_against_groups(range_paths)
            range_total = sum(range_counts.values())
            range_errors: list[str] = []
            expected_subjects = [
                EXPECTED_FOLLOWUP_COMMIT_SUBJECT,
                EXPECTED_PRIMARY_COMMIT_SUBJECT,
            ]
            if subjects != expected_subjects:
                range_errors.append(
                    f"recent commit subjects differ: expected={expected_subjects!r} actual={subjects!r}"
                )
            if range_counts != EXPECTED_GROUP_COUNTS:
                range_errors.append(
                    f"recent commit range counts differ: expected={EXPECTED_GROUP_COUNTS} actual={range_counts}"
                )
            if range_total != EXPECTED_TOTAL:
                range_errors.append(
                    f"recent commit range total differs: expected={EXPECTED_TOTAL} actual={range_total}"
                )
            if not range_errors:
                print("phase6 bundle readiness check passed.")
                print("mode=head_commit_range")
                for group_name, count in EXPECTED_GROUP_COUNTS.items():
                    print(f"{group_name}={count}")
                print(f"total_changed={EXPECTED_TOTAL}")
                print(f"recent_commit_subjects={subjects}")
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
