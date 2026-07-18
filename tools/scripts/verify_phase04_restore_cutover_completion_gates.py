from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_complete_infrastructure.py"
)
DR_PROFILE = REPO_ROOT / "docs" / "governance" / "infrastructure-dr-profile.yaml"
BACKUP_RESTORE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-backup-restore-replay.md"
)
COMPLETE_BLOCKER_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
)
BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-restore-cutover-completion-gates.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_file(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(
            f"missing required file: {path.relative_to(REPO_ROOT).as_posix()}"
        )
        return ""
    return _read(path)


def verify_phase04_restore_cutover_completion_gates() -> list[str]:
    errors: list[str] = []

    complete_verifier = _require_file(COMPLETE_VERIFIER, errors)
    backup_evidence = _require_file(BACKUP_RESTORE_EVIDENCE, errors)
    complete_evidence = _require_file(COMPLETE_BLOCKER_EVIDENCE, errors)
    boundary_evidence = _require_file(BOUNDARY_EVIDENCE, errors)
    dr_text = _require_file(DR_PROFILE, errors)
    if not dr_text:
        return errors

    dr_profile = yaml.safe_load(dr_text)
    cutover_policy = dr_profile.get("cutover_policy", {})
    if cutover_policy.get("explicit_cutover_required") is not True:
        errors.append("cutover policy must require explicit cutover approval")
    if cutover_policy.get("cutover_allowed_by_default") is not False:
        errors.append("cutover policy must fail closed by default")
    if cutover_policy.get("approval_owner") != "Coordinator":
        errors.append("cutover approval owner must be Coordinator")

    for phrase in [
        '"backup_restore_replay: proven"',
        '"combined_dependency_fault: proven"',
        "PHASE04 coordinator approval is not approved",
        "PHASE05 start gate remains closed",
        "official LangGraph PostgreSQL Checkpointer is not importable/proven",
    ]:
        if phrase not in complete_verifier:
            errors.append(
                f"complete verifier missing completion/cutover gate phrase: {phrase}"
            )

    for phrase in [
        "postgres_backup: passed",
        "postgres_restore: passed",
        "object_manifest_restore: passed",
        "checkpoint_table_restore: passed",
        "product_projection_replay: passed",
        "product_projection_recovery_set: passed",
        "runtime_restart_after_restore: passed",
        "official_checkpointer_restore: proven_separately",
        "pitr: proven_separately",
        "临时 `zuno_phase04_restore_<marker>`",
    ]:
        if phrase not in backup_evidence:
            errors.append(f"backup/restore evidence missing phrase: {phrase}")

    for phrase in [
        "backup_restore_replay: missing",
        "backup_restore_replay_subset: passed",
        "combined_dependency_fault: missing",
        "coordinator_decision: not_approved",
        "status: blocked",
    ]:
        if phrase not in complete_evidence:
            errors.append(f"complete blocker evidence missing phrase: {phrase}")

    for phrase in [
        "backup_completed_requires_verification_gate: passed",
        "restore_isolated_before_cutover_gate: passed",
        "recovery_cutover_explicit_allow_gate: passed",
        "phase_completion: blocked_graph_resume_retention_and_combined_fault",
        "不证明 graph-level Checkpointer interrupt/resume、retention/prune 或 combined-service fault",
    ]:
        if phrase not in boundary_evidence:
            errors.append(f"restore/cutover gate evidence missing phrase: {phrase}")

    return errors


def main() -> int:
    errors = verify_phase04_restore_cutover_completion_gates()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 restore/cutover completion gate verification failed.")
        return 1
    print("PHASE04 restore/cutover completion gate verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
