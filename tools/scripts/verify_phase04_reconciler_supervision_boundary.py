from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

IDEMPOTENCY_SOURCE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "idempotency.py"
)
LEASE_SOURCE = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "lease.py"
)
IDEMPOTENCY_SUPERVISION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_idempotency_supervision.py"
)
LEASE_COORDINATION_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_lease_worker_coordination.py"
)
IDEMPOTENCY_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-idempotency-claim.md"
LEASE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-lease-fencing.md"
BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-reconciler-supervision-boundary.md"
)
COMPLETE_BLOCKER_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
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


def verify_phase04_reconciler_supervision_boundary() -> list[str]:
    errors: list[str] = []

    idempotency_source = _require_file(IDEMPOTENCY_SOURCE, errors)
    lease_source = _require_file(LEASE_SOURCE, errors)
    idempotency_evidence = _require_file(IDEMPOTENCY_EVIDENCE, errors)
    lease_evidence = _require_file(LEASE_EVIDENCE, errors)
    boundary_evidence = _require_file(BOUNDARY_EVIDENCE, errors)
    complete_evidence = _require_file(COMPLETE_BLOCKER_EVIDENCE, errors)

    for path in [IDEMPOTENCY_SUPERVISION_VERIFIER, LEASE_COORDINATION_VERIFIER]:
        if not path.exists():
            errors.append(f"missing verifier: {path.relative_to(REPO_ROOT).as_posix()}")

    for phrase in [
        "class IdempotencyWorkerSupervisor",
        "reconcile: Callable[[], str | None]",
        "recovered = reconcile()",
        "self._complete(scope, key, owner, claim.generation, recovered)",
        "reconciled=True",
        "replayed=True",
        "operation=lambda: operation_calls.append",
        "operation_calls",
    ]:
        if phrase not in idempotency_source and phrase not in _read(
            IDEMPOTENCY_SUPERVISION_VERIFIER
        ):
            errors.append(f"idempotency reconciler boundary missing phrase: {phrase}")

    for phrase in [
        "class LeaseWorkerCoordinator",
        "heartbeat.start()",
        "commit(",
        "repo.assert_fence(",
        "clock_tolerance_seconds=self.clock_tolerance_seconds",
        "FencingRejectedError",
        "lease heartbeat failed; ownership is unknown",
    ]:
        if phrase not in lease_source:
            errors.append(f"lease/fencing reconciler boundary missing phrase: {phrase}")

    for phrase in [
        "worker_heartbeat_supervision: passed",
        "effect_reconciliation_after_process_exit: passed",
        "lost_completion_no_reexecution: passed",
        "process_cancellation_propagates: passed",
        "Idempotency Claim != Domain Success",
    ]:
        if phrase not in idempotency_evidence:
            errors.append(f"idempotency evidence missing phrase: {phrase}")

    for phrase in [
        "worker_heartbeat_scheduler: passed",
        "crash_handoff: passed",
        "network_partition_heartbeat_loss: passed",
        "fenced_commit_same_transaction: passed",
        "不能代表领域结果成功",
    ]:
        if phrase not in lease_evidence:
            errors.append(f"lease evidence missing phrase: {phrase}")

    for phrase in [
        "reconciler_supervision_boundary: passed",
        "idempotency_reconcile_no_reexecution: passed",
        "lease_fencing_supervision: passed",
        "postgres_partition_fail_closed: passed",
        "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
        "不证明所有产品 Reconciler 已接入",
    ]:
        if phrase not in boundary_evidence:
            errors.append(f"reconciler boundary evidence missing phrase: {phrase}")

    for phrase in [
        "idempotency_worker_supervision: passed",
        "lease_worker_coordination: passed",
    ]:
        if phrase not in complete_evidence:
            errors.append(f"complete blocker evidence missing phrase: {phrase}")

    return errors


def main() -> int:
    errors = verify_phase04_reconciler_supervision_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 reconciler supervision boundary verification failed.")
        return 1
    print("PHASE04 reconciler supervision boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
