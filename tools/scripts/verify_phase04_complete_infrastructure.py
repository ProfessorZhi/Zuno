from __future__ import annotations

import re
import socket
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
PHASE04_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
PARTIAL_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md"
REAL_SERVICES_SMOKE = REPO_ROOT / "tools" / "scripts" / "verify_phase04_real_services_smoke.py"
RABBITMQ_TRANSPORT_VERIFIER = REPO_ROOT / "tools" / "scripts" / "verify_phase04_rabbitmq_transport.py"
RABBITMQ_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-rabbitmq-transport.md"

REQUIRED_REAL_SERVICES = {
    "PostgreSQL": ("localhost", 5432),
    "RabbitMQ": ("localhost", 5672),
    "MinIO/S3": ("localhost", 9000),
}

REQUIRED_EVIDENCE_PHRASES = [
    "RabbitMQ publisher confirm",
    "RabbitMQ redelivery",
    "RabbitMQ DLQ",
    "MinIO/S3 object staging",
    "MinIO/S3 restore",
    "LangGraph PostgreSQL Checkpointer",
    "Backup/Restore/Replay",
    "PITR",
    "combined dependency fault",
]

REQUIRED_COMPLETION_PROOF_MARKERS = [
    "real_services_smoke: passed",
    "langgraph_postgres_checkpointer: proven",
    "backup_restore_replay: proven",
    "rabbitmq_fault_evidence: proven",
    "minio_restore_evidence: proven",
    "combined_dependency_fault: proven",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _load_verifier(path: Path, module_name: str, function_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load verifier: {path.relative_to(REPO_ROOT).as_posix()}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def _official_langgraph_postgres_checkpointer_available() -> bool:
    return (
        find_spec("langgraph.checkpoint.postgres") is not None
        or find_spec("langgraph_checkpoint_postgres") is not None
    )


def verify_phase04_complete_infrastructure() -> list[str]:
    errors: list[str] = []
    if not PHASE04_READINESS.exists():
        return ["missing PHASE04 readiness: .agent/programs/work-products/phase04-readiness.yaml"]

    readiness = _read(PHASE04_READINESS)
    for task_id in [f"P04-T{index:02d}" for index in range(1, 8)]:
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase04-readiness.yaml")
    if "coordinator_approval: approved" not in readiness:
        errors.append("PHASE04 coordinator approval is not approved")
    if "may_start_phase05_after_validation: true" not in readiness:
        errors.append("PHASE05 start gate remains closed")

    for label, (host, port) in REQUIRED_REAL_SERVICES.items():
        if not _tcp_open(host, port):
            errors.append(f"{label} real service is not reachable at {host}:{port}")

    if not REAL_SERVICES_SMOKE.exists():
        errors.append("missing PHASE04 real services smoke verifier")
    else:
        smoke_errors = _load_verifier(
            REAL_SERVICES_SMOKE,
            "verify_phase04_real_services_smoke",
            "verify_phase04_real_services_smoke",
        )()
        for smoke_error in smoke_errors:
            errors.append(f"PHASE04 real service smoke failed: {smoke_error}")

    if not _official_langgraph_postgres_checkpointer_available():
        errors.append("official LangGraph PostgreSQL Checkpointer is not importable/proven")

    if not RABBITMQ_TRANSPORT_VERIFIER.exists():
        errors.append("missing PHASE04 RabbitMQ transport verifier")
    else:
        rabbit_errors = _load_verifier(
            RABBITMQ_TRANSPORT_VERIFIER,
            "verify_phase04_rabbitmq_transport",
            "verify_phase04_rabbitmq_transport",
        )()
        for rabbit_error in rabbit_errors:
            errors.append(f"PHASE04 RabbitMQ transport verification failed: {rabbit_error}")

    if not RABBITMQ_EVIDENCE.exists():
        errors.append("missing PHASE04 RabbitMQ transport evidence")
    else:
        rabbit_evidence = _read(RABBITMQ_EVIDENCE)
        for phrase in [
            "publisher_confirm: passed",
            "redelivery: passed",
            "dlq: passed",
            "Queue ACK != Domain Success",
        ]:
            if phrase not in rabbit_evidence:
                errors.append(f"PHASE04 RabbitMQ transport evidence missing phrase: {phrase}")

    if not PARTIAL_EVIDENCE.exists():
        errors.append("missing partial PHASE04 evidence: docs/evidence/phase04-postgres-foundation.md")
    else:
        partial = _read(PARTIAL_EVIDENCE)
        for phrase in ["partial_implementation_available", "phase_completion: `withdrawn`"]:
            if phrase not in partial:
                errors.append(f"partial PHASE04 evidence missing boundary phrase: {phrase}")

    if not PHASE04_EVIDENCE.exists():
        errors.append("missing PHASE04 complete infrastructure evidence/blocker file")
    else:
        evidence = _read(PHASE04_EVIDENCE)
        for phrase in REQUIRED_EVIDENCE_PHRASES:
            if phrase not in evidence:
                errors.append(f"PHASE04 evidence missing required real dependency proof: {phrase}")
        for marker in REQUIRED_COMPLETION_PROOF_MARKERS:
            if marker not in evidence:
                errors.append(f"PHASE04 evidence missing completion proof marker: {marker}")
        if "status: blocked" not in evidence and "coordinator_decision: approved" not in evidence:
            errors.append("PHASE04 evidence must explicitly record blocked status or approved closure")
    return errors


def main() -> int:
    errors = verify_phase04_complete_infrastructure()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 complete infrastructure verification failed.")
        return 1
    print("PHASE04 complete infrastructure verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
