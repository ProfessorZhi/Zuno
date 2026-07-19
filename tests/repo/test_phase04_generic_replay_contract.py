from __future__ import annotations

import pytest

from zuno.platform.recovery import InMemoryReplayPort, ReplayContractError, ReplaySourceFact


def test_generic_replay_port_enforces_generation_hash_ordering_and_duplicates() -> None:
    port = InMemoryReplayPort()
    source = ReplaySourceFact.create(
        source_ref="product-source:phase04",
        owner_module="Product",
        recovery_point="restore:phase04",
        replay_generation=7,
        ordering_sequence=3,
        payload={"source": "product", "watermark": 3},
    )

    receipt = port.replay_projection(
        source=source,
        projection_ref="product-projection:phase04",
        expected_generation=7,
        projection_payload={"projection": "product", "source_ref": source.source_ref},
    )
    duplicate = port.replay_projection(
        source=source,
        projection_ref="product-projection:phase04",
        expected_generation=7,
        projection_payload={"projection": "product", "source_ref": source.source_ref},
    )

    assert receipt.duplicate is False
    assert duplicate.duplicate is True
    assert duplicate.projection_hash == receipt.projection_hash
    assert receipt.source_hash != receipt.projection_hash
    assert receipt.ordering_sequence == 3

    with pytest.raises(ReplayContractError, match="stale replay generation"):
        port.replay_projection(
            source=source,
            projection_ref="product-projection:phase04-stale",
            expected_generation=6,
            projection_payload={"projection": "stale"},
        )


def test_future_domain_replay_contract_does_not_claim_domain_runtime() -> None:
    port = InMemoryReplayPort()
    source = ReplaySourceFact.create(
        source_ref="future-domain-source:phase04",
        owner_module="FutureDomain",
        recovery_point="restore:phase04",
        replay_generation=1,
        ordering_sequence=1,
        payload={"contract_only": True, "domain_runtime": "target_not_current"},
    )

    receipt = port.replay_projection(
        source=source,
        projection_ref="future-domain-projection:phase04",
        expected_generation=1,
        projection_payload={"derived": True, "source_ref": source.source_ref},
    )

    assert receipt.owner_module == "FutureDomain"
    assert receipt.duplicate is False
