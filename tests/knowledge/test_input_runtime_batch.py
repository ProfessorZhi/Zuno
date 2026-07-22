from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from zuno.knowledge.ingestion.runtime_batch import (
    INPUT_REQUIREMENT_IDS,
    InputRuntimeBatchError,
    build_input_runtime_batch_fixture,
    validate_input_runtime_batch,
)


def test_input_runtime_batch_validates_all_eighty_requirements() -> None:
    report = validate_input_runtime_batch()

    assert report.requirement_ids == INPUT_REQUIREMENT_IDS
    assert report.requirement_ids[0] == "ARCH-ING-001"
    assert report.requirement_ids[-1] == "ARCH-ING-080"
    assert report.source_verified is True
    assert report.parse_status == "succeeded"
    assert report.blocked_status == "review_pending"
    assert report.queue_outbox_count >= 5


def test_input_runtime_batch_rejects_late_parse_attempt() -> None:
    fixture = build_input_runtime_batch_fixture()
    bad_attempt = replace(
        fixture.attempt_control,
        lease_expires_at=datetime(2026, 7, 18, 11, 59, tzinfo=timezone.utc),
    )

    with pytest.raises(InputRuntimeBatchError, match="late parse"):
        validate_input_runtime_batch(replace(fixture, attempt_control=bad_attempt))


def test_input_runtime_batch_rejects_lossy_transform_that_drops_original() -> None:
    fixture = build_input_runtime_batch_fixture()
    bad_transform = replace(fixture.transform_records[1], keeps_original=False)

    with pytest.raises(InputRuntimeBatchError, match="lossy"):
        validate_input_runtime_batch(
            replace(fixture, transform_records=(fixture.transform_records[0], bad_transform))
        )


def test_input_runtime_batch_rejects_missing_delete_receipts() -> None:
    fixture = build_input_runtime_batch_fixture()
    bad_receipts = replace(fixture.deletion_receipts, knowledge_receipt="")

    with pytest.raises(InputRuntimeBatchError, match="delete completion"):
        validate_input_runtime_batch(replace(fixture, deletion_receipts=bad_receipts))


def test_input_runtime_batch_rejects_incomplete_format_preservation() -> None:
    fixture = build_input_runtime_batch_fixture()
    bad_office = replace(fixture.office_preservation, excel_formula_cache_display=False)

    with pytest.raises(InputRuntimeBatchError, match="format preservation"):
        validate_input_runtime_batch(replace(fixture, office_preservation=bad_office))
