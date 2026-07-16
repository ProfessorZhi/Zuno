from __future__ import annotations

import re
import socket
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"
PHASE04_READINESS = WORK_PRODUCTS / "phase04-readiness.yaml"
PHASE04_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
PARTIAL_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase04-postgres-foundation.md"

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


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _tcp_open(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


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
