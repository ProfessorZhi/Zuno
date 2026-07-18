from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from zuno.agent.runtime_batch import (
    AGENT_REQUIREMENT_IDS,
    AgentRuntimeBatchError,
    ResultValidity,
    build_agent_runtime_batch_fixture,
    validate_agent_runtime_batch,
)


def test_agent_runtime_batch_validates_all_eighty_requirements() -> None:
    report = validate_agent_runtime_batch()

    assert report.requirement_ids == AGENT_REQUIREMENT_IDS
    assert report.requirement_ids[0] == "ARCH-AGENT-001"
    assert report.requirement_ids[-1] == "ARCH-AGENT-080"
    assert report.node_count == 10
    assert report.step_count == 4
    assert report.action_count == 1
    assert report.outbox_count == 5
    assert report.reconciler_count == 8
    assert report.checkpoint_count >= 10


def test_agent_runtime_batch_rejects_plan_cycles() -> None:
    fixture = build_agent_runtime_batch_fixture()
    cyclic_plan = replace(
        fixture.plan_version,
        dependency_edges=(
            ("step:retrieve", "step:act"),
            ("step:act", "step:retrieve"),
        ),
    )

    with pytest.raises(AgentRuntimeBatchError, match="cycle"):
        validate_agent_runtime_batch(replace(fixture, plan_version=cyclic_plan))


def test_agent_runtime_batch_rejects_unknown_effect_without_reconcile() -> None:
    fixture = build_agent_runtime_batch_fixture()
    bad_action = replace(fixture.actions[0], replay_policy="RETRY_IMMEDIATELY")

    with pytest.raises(AgentRuntimeBatchError, match="UNKNOWN action"):
        validate_agent_runtime_batch(replace(fixture, actions=(bad_action,)))


def test_agent_runtime_batch_rejects_publication_without_valid_result() -> None:
    fixture = build_agent_runtime_batch_fixture()
    bad_publication = replace(fixture.publication, result_validity=ResultValidity.STALE)

    with pytest.raises(AgentRuntimeBatchError, match="Publication must revalidate"):
        validate_agent_runtime_batch(replace(fixture, publication=bad_publication))


def test_agent_runtime_batch_rejects_naive_deadline_time() -> None:
    fixture = build_agent_runtime_batch_fixture()
    bad_time = replace(
        fixture.time_semantics,
        deadline_at=datetime(2026, 7, 18, 12, 0),
        expires_at=datetime(2026, 7, 18, 13, 0, tzinfo=timezone.utc),
    )

    with pytest.raises(AgentRuntimeBatchError, match="time semantics"):
        validate_agent_runtime_batch(replace(fixture, time_semantics=bad_time))
