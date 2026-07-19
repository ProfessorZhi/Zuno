from __future__ import annotations

import re
import socket
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
REQUIREMENT_LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
PHASE04_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
BACKUP_RESTORE_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-backup-restore-replay.md"
SCHEMA_UPGRADE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-official-checkpointer-schema-upgrade.md"
)

REAL_SERVICES = {
    "PostgreSQL": ("localhost", 5432),
    "RabbitMQ": ("localhost", 5672),
    "MinIO": ("localhost", 9000),
}

REQUIRED_PRE_CLOSURE_MARKERS = [
    "real_services_smoke: passed",
    "langgraph_postgres_checkpointer: proven",
    "backup_restore_replay: proven",
    "official_checkpointer_schema_upgrade: proven",
    "generic_replay_framework: proven",
    "rabbitmq_fault_evidence: proven",
    "minio_restore_evidence: proven",
    "combined_dependency_fault: proven",
]

REQUIRED_BACKUP_MARKERS = [
    "postgres_backup: passed",
    "postgres_restore: passed",
    "object_manifest_restore: passed",
    "checkpoint_table_restore: passed",
    "product_projection_replay: passed",
    "generic_replay_framework: passed",
    "replay_generation: passed",
    "replay_duplicate_handling: passed",
    "replay_stale_generation_reject: passed",
    "future_domain_replay_port_contract: passed",
    "cross_domain_recovery_set: passed",
    "cross_domain_hash_verification: passed",
    "runtime_restart_after_restore: passed",
]

REQUIRED_SCHEMA_UPGRADE_MARKERS = [
    "official_checkpointer_schema_upgrade: proven",
    "official_old_schema_v8_created: passed",
    "official_setup_migrated_to_v9: passed",
    "official_pre_upgrade_checkpoint_recovered: passed",
    "official_v9_task_path_write: passed",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tcp_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except OSError:
        return False


def _require_phrases(label: str, text: str, phrases: list[str]) -> list[str]:
    return [f"{label} missing marker: {phrase}" for phrase in phrases if phrase not in text]


def _phase04_target_not_current_requirements(ledger: str) -> list[str]:
    errors: list[str] = []
    for block in re.split(r"\n(?=  - requirement_id: )", ledger):
        if 'target_phase: "PHASE04"' not in block:
            continue
        if "mandatory: true" not in block:
            continue
        if "current_status: target_not_current" in block:
            match = re.search(r"requirement_id:\s+([A-Z0-9-]+)", block)
            errors.append(match.group(1) if match else "unknown PHASE04 requirement")
    return errors


def verify_phase04_pre_closure_gate() -> list[str]:
    errors: list[str] = []
    if not PHASE04_READINESS.exists():
        return ["missing PHASE04 readiness file"]
    if not REQUIREMENT_LEDGER.exists():
        return ["missing Requirement Ledger"]

    readiness = _read(PHASE04_READINESS)
    for task_id in [f"P04-T{index:02d}" for index in range(1, 6)]:
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase04-readiness.yaml")
    for task_id in ["P04-T06", "P04-T07"]:
        if (
            re.search(
                rf"(?s){task_id}:\s*\n\s+state:\s+(completed|completion_candidate)\b",
                readiness,
            )
            is None
        ):
            errors.append(
                f"{task_id} is neither completed nor completion_candidate in phase04-readiness.yaml"
            )

    for label, (host, port) in REAL_SERVICES.items():
        if not _tcp_open(host, port):
            errors.append(f"{label} real service is not reachable at {host}:{port}")

    ledger = _read(REQUIREMENT_LEDGER)
    phase04_gaps = _phase04_target_not_current_requirements(ledger)
    if phase04_gaps:
        errors.append(
            "PHASE04 mandatory target_not_current requirements remain: "
            + ", ".join(phase04_gaps)
        )
    if "implementation_available: 74" not in ledger or "target_not_current: 682" not in ledger:
        errors.append("Requirement Ledger current_status_counts are not 74/682")

    if not PHASE04_EVIDENCE.exists():
        errors.append("missing PHASE04 infrastructure evidence")
    else:
        errors.extend(
            _require_phrases(
                "PHASE04 infrastructure evidence",
                _read(PHASE04_EVIDENCE),
                REQUIRED_PRE_CLOSURE_MARKERS,
            )
        )
    if not BACKUP_RESTORE_EVIDENCE.exists():
        errors.append("missing PHASE04 backup/restore/replay evidence")
    else:
        errors.extend(
            _require_phrases(
                "PHASE04 backup/restore/replay evidence",
                _read(BACKUP_RESTORE_EVIDENCE),
                REQUIRED_BACKUP_MARKERS,
            )
        )
    if not SCHEMA_UPGRADE_EVIDENCE.exists():
        errors.append("missing PHASE04 official Checkpointer schema upgrade evidence")
    else:
        errors.extend(
            _require_phrases(
                "PHASE04 official Checkpointer schema upgrade evidence",
                _read(SCHEMA_UPGRADE_EVIDENCE),
                REQUIRED_SCHEMA_UPGRADE_MARKERS,
            )
        )
    return errors


def main() -> int:
    errors = verify_phase04_pre_closure_gate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 pre-closure gate failed.")
        return 1
    print("PHASE04 pre-closure gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
