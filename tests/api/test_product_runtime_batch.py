from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from zuno.product.runtime_batch import (
    CommandReceipt,
    CommandReceiptStatus,
    PRODUCT_REQUIREMENT_IDS,
    ProductRuntimeBatchError,
    ProjectionEventKind,
    _stream_event,
    build_product_runtime_batch_fixture,
    validate_product_runtime_batch,
    validate_product_runtime_batch_from_repo,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_product_runtime_batch_validates_all_eighty_requirements_from_repo() -> None:
    report = validate_product_runtime_batch_from_repo(REPO_ROOT)

    assert report.requirement_ids == PRODUCT_REQUIREMENT_IDS
    assert report.requirement_ids[0] == "ARCH-PRODUCT-001"
    assert report.requirement_ids[-1] == "ARCH-PRODUCT-080"
    assert report.command_count == 1
    assert report.receipt_count == 3
    assert report.stream_event_count == 4
    assert report.outcome_count == 7
    assert report.frontend_contract_checked is True


def test_product_runtime_batch_rejects_receipt_that_claims_domain_success() -> None:
    fixture = build_product_runtime_batch_fixture()
    bad_receipts = (
        *fixture.receipts,
        CommandReceipt(
            "receipt:bad",
            fixture.command.command_id,
            4,
            CommandReceiptStatus.ACCEPTED,
            domain_success_ref="agent-run:succeeded",
        ),
    )

    with pytest.raises(ProductRuntimeBatchError, match="domain success"):
        validate_product_runtime_batch(replace(fixture, receipts=bad_receipts))


def test_product_runtime_batch_rejects_heartbeat_as_success() -> None:
    fixture = build_product_runtime_batch_fixture()
    bad_events = tuple(
        _stream_event(event.event_id, ProjectionEventKind.HEARTBEAT, "completed", 20)
        if event.type == "HEARTBEAT"
        else event
        for event in fixture.stream_events
    )

    with pytest.raises(ProductRuntimeBatchError, match="Heartbeat"):
        validate_product_runtime_batch(replace(fixture, stream_events=bad_events))


def test_product_runtime_batch_rejects_expired_action_token() -> None:
    fixture = build_product_runtime_batch_fixture()
    bad_token = replace(
        fixture.action_token,
        expires_at=datetime(2026, 7, 18, 11, 59, tzinfo=timezone.utc),
    )

    with pytest.raises(ProductRuntimeBatchError, match="ActionToken"):
        validate_product_runtime_batch(replace(fixture, action_token=bad_token))


def test_product_runtime_batch_rejects_frontend_forbidden_secret_fields() -> None:
    with pytest.raises(ProductRuntimeBatchError, match="api_key"):
        validate_product_runtime_batch(
            workspace_api_text=(
                "WorkspaceProductMode WorkspaceTaskStatus WorkspaceTaskLifecycleSnapshot "
                "WorkspaceApprovalRequest WorkspaceCancelRequest workspaceTaskEventsStreamAPI "
                "downloadWorkspaceArtifactAPI responseType: 'blob' api_key"
            )
        )
