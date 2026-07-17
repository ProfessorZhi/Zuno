from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CONTRACTS = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "contracts" / "shared.py"
)
MINIO_MANIFEST_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_minio_manifest_adoption.py"
)

REQUIRED_BOUNDARY_PHRASES = {
    "docs/evidence/phase04-outbox-rabbitmq-publisher.md": [
        "Queue ACK != Domain Success",
        "domain success remains owned by the producing and consuming domain transactions",
    ],
    "docs/evidence/phase04-rabbitmq-transport.md": [
        "Queue ACK != Domain Success",
        "domain commit remains owned by the PostgreSQL transaction and inbox/outbox boundary",
    ],
    "docs/evidence/phase04-outbox-delivery-policy.md": [
        "Queue ACK != Domain Success",
        "Outbox 的 published、dead-letter 和 replay 都是基础设施交付事实",
    ],
    "docs/evidence/phase04-rabbitmq-network-partition.md": [
        "Queue ACK != Domain Success",
        "不得解释为领域成功",
    ],
    "docs/evidence/phase04-rabbitmq-out-of-order.md": [
        "Queue ACK != Domain Success",
        "不表示领域结果成功",
    ],
    "docs/evidence/phase04-minio-object-store.md": [
        "Object Commit != Domain Success",
        "物理 Object receipt 不会自动推进领域成功",
    ],
    "docs/evidence/phase04-idempotency-claim.md": [
        "Idempotency Claim != Domain Success",
        "领域 Owner 仍拥有结果含义与有效性",
    ],
    "docs/evidence/phase04-operator-readiness.md": [
        "Operator telemetry 是运行观测事实",
        "不冒充领域成功",
    ],
}

INFRA_RECEIPT_CLASSES = [
    "AuditPersistenceReceiptV1",
    "IndexWriteReceiptV1",
    "WriteVisibilityReceiptV1",
    "EffectReceiptV1",
    "InfrastructureLeaseRefV1",
]

FORBIDDEN_TERMINAL_TERMS = [
    "DOMAIN_SUCCESS",
    "BUSINESS_SUCCESS",
    "RUN_OUTCOME_SUCCESS",
    "FINAL_SUCCESS",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _class_block(text: str, class_name: str) -> str:
    match = re.search(
        rf"(?ms)^class {re.escape(class_name)}\b.*?(?=^class |\Z)",
        text,
    )
    return "" if match is None else match.group(0)


def verify_phase04_infrastructure_domain_boundary() -> list[str]:
    errors: list[str] = []

    if not CONTRACTS.exists():
        return ["missing shared contracts module"]
    contract_text = _read(CONTRACTS)
    for class_name in INFRA_RECEIPT_CLASSES:
        block = _class_block(contract_text, class_name)
        if not block:
            errors.append(f"missing infrastructure receipt contract: {class_name}")
            continue
        for forbidden in FORBIDDEN_TERMINAL_TERMS:
            if forbidden in block:
                errors.append(
                    f"{class_name} contains forbidden terminal term {forbidden}"
                )

    for relative_path, phrases in REQUIRED_BOUNDARY_PHRASES.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"missing boundary evidence: {relative_path}")
            continue
        text = _read(path)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{relative_path} missing boundary phrase: {phrase}")

    if not MINIO_MANIFEST_VERIFIER.exists():
        errors.append("missing MinIO manifest adoption verifier")
    else:
        manifest_verifier = _read(MINIO_MANIFEST_VERIFIER)
        for phrase in [
            "simulated crash before domain success commit",
            "domain success and visible manifest did not roll back together",
            "object receipt was incorrectly interpreted as domain success",
        ]:
            if phrase not in manifest_verifier:
                errors.append(
                    f"MinIO manifest verifier missing boundary check: {phrase}"
                )

    return errors


def main() -> int:
    errors = verify_phase04_infrastructure_domain_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 infrastructure domain boundary verification failed.")
        return 1
    print("PHASE04 infrastructure domain boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
