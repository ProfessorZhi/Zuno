from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = REPO_ROOT / "tools/scripts/verify_wave1_contract_freeze.py"
ADR = REPO_ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
REGISTRY = REPO_ROOT / "docs/governance/wave1-cross-module-contract-registry.md"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_wave1_contract_freeze", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_wave1_contract_freeze_verifier_passes() -> None:
    verifier = _load_verifier()
    assert verifier.verify() == []


def test_physical_infrastructure_owner_is_platform() -> None:
    content = ADR.read_text(encoding="utf-8")
    assert "src/backend/zuno/platform/" in content
    assert "不新增 `src/backend/zuno/infrastructure/` 顶层目录" in content
    for term in [
        "├── database/",
        "├── storage/",
        "├── jobs/",
        "├── checkpoint/",
        "├── coordination/",
        "├── data_services/",
        "├── operations/",
        "├── network/",
        "├── release/",
    ]:
        assert term in content


def test_shared_contract_fields_are_frozen() -> None:
    content = ADR.read_text(encoding="utf-8")
    for term in [
        "CrossModuleEnvelopeV1",
        "EffectiveSecurityEpochRefV1",
        "CredentialVersionRefV1",
        "SecretLeaseV1",
        "SecurityAuditRequirementV1",
        "AuditPersistenceReceiptV1",
        "ProviderConnectionRequestV1",
        "ModelQuotaReservationV1",
        "ModelUsageReceiptV1",
        "ModelCancellationReceiptV1",
        "IndexWriteBatchV1",
        "IndexWriteReceiptV1",
        "WriteVisibilityReceiptV1",
    ]:
        assert term in content


def test_prepared_action_conflict_is_resolved() -> None:
    content = ADR.read_text(encoding="utf-8")
    for term in [
        "ActionProposalV1",
        "PreparedToolActionV1",
        "ActionExecutionBinding",
        "SecurityApprovalDecision",
        "EffectReceipt",
        "EffectReconciliation",
        "canonical_args_hash",
        "effective_security_epoch_hash",
        "prepared_action_hash",
    ]:
        assert term in content

    assert "Queue ACK != Tool Effect Success" in content
    assert "Audit Persistence != Tool Effect Success" in content
    assert "Checkpoint Commit != Domain Commit" in content


def test_registry_is_confirmed_target_not_current() -> None:
    content = REGISTRY.read_text(encoding="utf-8")
    assert "status: confirmed-target" in content
    assert content.count("`CONFIRMED_TARGET`") >= 25
    assert "| `FIELD_FROZEN_PENDING_MERGE` |" not in content
    assert "状态：`FIELD_FROZEN_PENDING_MERGE`" not in content
    assert "协调状态：`CONFLICT_REQUIRES_DECISION`" not in content
    assert "本文件当前所有条目最高只能是 `ALIGNED_PENDING_FIELDS`" not in content
    assert "本 Registry 已随 Wave 1 合并确认为 `CONFIRMED_TARGET`" in content
    assert "IMPLEMENTATION_AVAILABLE" in content
    assert "CURRENT" in content


def test_failure_namespaces_and_canonical_codes_are_frozen() -> None:
    content = REGISTRY.read_text(encoding="utf-8")
    for prefix in ["SEC_*", "INFRA_*", "MODEL_*", "OBS_*", "TOOL_*", "KNOW_*", "MEM_*", "AGENT_*"]:
        assert prefix in content
    for code in [
        "SEC_STALE_EPOCH",
        "INFRA_CONDITIONAL_WRITE_CONFLICT",
        "MODEL_ATTEMPT_UNKNOWN",
        "OBS_INGEST_GAP",
        "TOOL_EFFECT_UNKNOWN",
        "KNOW_INDEX_MANIFEST_REJECTED",
    ]:
        assert code in content


def test_cross_module_requirement_registry_is_complete() -> None:
    content = REGISTRY.read_text(encoding="utf-8")
    for number in range(1, 11):
        assert content.count(f"ARCH-XMOD-{number:03d}") == 1
        assert f"XMOD-{number:03d}-UT" in content
        assert f"XMOD-{number:03d}-IT" in content
        assert f"EV-XMOD-{number:03d}" in content
