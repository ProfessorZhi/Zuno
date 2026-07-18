from __future__ import annotations

from pathlib import Path

import pytest

from zuno.platform.contracts import (
    CANONICAL_FAILURE_CODES,
    ContractRegistry,
    ContractRegistryEntry,
    CrossModuleRuntimeBatchError,
    CrossModuleEnvelopeV1,
    validate_cross_module_runtime_batch,
    validate_cross_module_runtime_batch_from_repo,
)
from zuno.platform.contracts.registry import ContractVersion


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_xmod_runtime_batch_validates_all_ten_requirements_from_repo() -> None:
    report = validate_cross_module_runtime_batch_from_repo(REPO_ROOT)

    assert report.requirement_ids == tuple(
        f"ARCH-XMOD-{index:03d}" for index in range(1, 11)
    )
    assert report.contract_count >= 20
    assert len(report.manifest_hash) == 64
    assert report.failure_code_count == len(CANONICAL_FAILURE_CODES)
    assert report.confirmed_registry is True
    assert report.confirmed_adr is True


def test_xmod_rejects_duplicate_contract_owner() -> None:
    good_entry = ContractRegistryEntry(
        contract_name="CrossModuleEnvelopeV1",
        version=ContractVersion(major=1, minor=0),
        schema_hash="hash-a",
        owner_module="Infrastructure",
        producer_modules=("ALL",),
        consumer_modules=("ALL",),
    )
    conflicting_owner = ContractRegistryEntry(
        contract_name="CrossModuleEnvelopeV1",
        version=ContractVersion(major=1, minor=1),
        schema_hash="hash-a",
        owner_module="Agent Core",
        producer_modules=("ALL",),
        consumer_modules=("ALL",),
    )
    registry = ContractRegistry([good_entry, conflicting_owner])

    with pytest.raises(CrossModuleRuntimeBatchError, match="duplicate owners"):
        validate_cross_module_runtime_batch(registry=registry)


def test_xmod_rejects_missing_producer_consumer_coverage() -> None:
    entry = ContractRegistryEntry(
        contract_name="CrossModuleEnvelopeV1",
        version=ContractVersion(major=1, minor=0),
        schema_hash="hash-a",
        owner_module="Infrastructure",
    )
    registry = ContractRegistry([entry])

    with pytest.raises(CrossModuleRuntimeBatchError) as exc_info:
        validate_cross_module_runtime_batch(registry=registry)

    assert "missing producer modules" in str(exc_info.value)
    assert "missing consumer modules" in str(exc_info.value)


def test_xmod_rejects_unconfirmed_adr_and_registry_evidence() -> None:
    with pytest.raises(CrossModuleRuntimeBatchError) as exc_info:
        validate_cross_module_runtime_batch(
            registry_doc="ARCH-XMOD-001",
            adr_doc="status: draft",
        )

    assert "status: confirmed-target" in str(exc_info.value)
    assert "confirmed_wave1_main_sha" in str(exc_info.value)


def test_xmod_cross_module_envelope_schema_carries_shared_runtime_boundary() -> None:
    schema_fields = set(CrossModuleEnvelopeV1.model_json_schema()["properties"])

    assert {
        "contract_version",
        "contract_bundle_version",
        "correlation_id",
        "causation_id",
        "tenant_id",
        "workspace_id",
        "deadline_at",
        "data_classification",
        "trace_id",
        "payload_hash",
        "idempotency_key",
        "expected_generation",
    } <= schema_fields
