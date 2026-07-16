from __future__ import annotations

import importlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE03_READINESS = REPO_ROOT / ".agent" / "programs" / "work-products" / "phase03-readiness.yaml"


def verify_phase03_contract_bundle() -> list[str]:
    errors: list[str] = []
    contract_root = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "contracts"
    required_files = ["__init__.py", "canonical.py", "registry.py", "shared.py"]
    for name in required_files:
        if not (contract_root / name).exists():
            errors.append(f"missing contract bundle file: {name}")
    if errors:
        return errors

    combined = "\n".join((contract_root / name).read_text(encoding="utf-8") for name in required_files)
    forbidden_imports = ["fastapi", "sqlalchemy", "langgraph", "vue", "openai", "anthropic"]
    for forbidden in forbidden_imports:
        if re.search(rf"^\s*(from|import)\s+{forbidden}\b", combined, re.MULTILINE):
            errors.append(f"contract bundle imports forbidden runtime dependency: {forbidden}")

    try:
        module = importlib.import_module("zuno.platform.contracts")
        registry = module.build_wave1_contract_registry()
        manifest = registry.manifest()
    except Exception as exc:  # pragma: no cover - reported as verifier error
        return [f"cannot load contract bundle: {exc}"]

    names = {entry.contract_name for entry in manifest.entries}
    required_contracts = {
        "CrossModuleEnvelopeV1",
        "ProductCommandV1",
        "SourceObjectRefV1",
        "KnowledgeVersionRefV1",
        "MemoryContextRefV1",
        "CapabilityInvocationRefV1",
        "ObservabilityEventRefV1",
        "InfrastructureLeaseRefV1",
        "EffectiveSecurityEpochRefV1",
        "SecurityApprovalDecisionV1",
        "AuditPersistenceReceiptV1",
        "ModelUsageReceiptV1",
        "IndexWriteBatchV1",
        "IndexWriteReceiptV1",
        "WriteVisibilityReceiptV1",
        "ActionProposalV1",
        "ActionExecutionBindingV1",
        "PreparedToolActionV1",
        "ToolObservationV1",
        "EffectReceiptV1",
        "EffectReconciliationV1",
        "FailureCodeV1",
    }
    missing = sorted(required_contracts - names)
    if missing:
        errors.append(f"contract registry missing required contracts: {missing}")
    if not manifest.bundle_hash:
        errors.append("contract bundle manifest missing bundle_hash")
    for entry in manifest.entries:
        if not entry.schema_hash:
            errors.append(f"contract entry missing schema hash: {entry.contract_name}")
        if not entry.owner_module:
            errors.append(f"contract entry missing owner: {entry.contract_name}")

    fixture_root = REPO_ROOT / "tests" / "contracts" / "fixtures"
    for fixture_name in ["CrossModuleEnvelopeV1.json", "FailureCodeV1.json"]:
        if not (fixture_root / fixture_name).exists():
            errors.append(f"missing contract fixture: {fixture_name}")
    readiness = PHASE03_READINESS.read_text(encoding="utf-8") if PHASE03_READINESS.exists() else ""
    for task_id in [f"P03-T{index:02d}" for index in range(1, 8)]:
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase03-readiness.yaml")
    if "coordinator_approval: approved" not in readiness:
        errors.append("PHASE03 coordinator approval is not approved")
    if "may_start_phase04_after_validation: true" not in readiness:
        errors.append("PHASE04 start gate remains closed")
    return errors


def main() -> int:
    errors = verify_phase03_contract_bundle()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE03 contract bundle verification failed.")
        return 1
    print("PHASE03 contract bundle verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
