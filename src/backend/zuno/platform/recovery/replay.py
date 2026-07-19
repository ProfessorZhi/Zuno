from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from zuno.platform.contracts import canonical_sha256


class ReplayContractError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ReplaySourceFact:
    source_ref: str
    owner_module: str
    recovery_point: str
    replay_generation: int
    ordering_sequence: int
    payload: dict[str, Any]
    payload_hash: str

    @classmethod
    def create(
        cls,
        *,
        source_ref: str,
        owner_module: str,
        recovery_point: str,
        replay_generation: int,
        ordering_sequence: int,
        payload: dict[str, Any],
    ) -> "ReplaySourceFact":
        return cls(
            source_ref=source_ref,
            owner_module=owner_module,
            recovery_point=recovery_point,
            replay_generation=replay_generation,
            ordering_sequence=ordering_sequence,
            payload=payload,
            payload_hash=canonical_sha256(payload),
        )


@dataclass(frozen=True, slots=True)
class ReplayProjectionReceipt:
    source_ref: str
    projection_ref: str
    owner_module: str
    recovery_point: str
    replay_generation: int
    ordering_sequence: int
    source_hash: str
    projection_hash: str
    duplicate: bool


class ReplayPort(Protocol):
    def replay_projection(
        self,
        *,
        source: ReplaySourceFact,
        projection_ref: str,
        expected_generation: int,
        projection_payload: dict[str, Any],
    ) -> ReplayProjectionReceipt:
        ...


class InMemoryReplayPort:
    """Contract-test replay port; production adapters persist equivalent receipts."""

    def __init__(self) -> None:
        self._receipts: dict[tuple[str, str, int], ReplayProjectionReceipt] = {}

    def replay_projection(
        self,
        *,
        source: ReplaySourceFact,
        projection_ref: str,
        expected_generation: int,
        projection_payload: dict[str, Any],
    ) -> ReplayProjectionReceipt:
        if source.replay_generation != expected_generation:
            raise ReplayContractError("stale replay generation rejected")
        if source.ordering_sequence < 1:
            raise ReplayContractError("ordering sequence must be positive")
        if canonical_sha256(source.payload) != source.payload_hash:
            raise ReplayContractError("source payload hash mismatch")
        projection_hash = canonical_sha256(projection_payload)
        if projection_hash == source.payload_hash:
            raise ReplayContractError("derived projection must not replace authoritative source")
        key = (source.source_ref, projection_ref, expected_generation)
        existing = self._receipts.get(key)
        if existing is not None:
            return ReplayProjectionReceipt(
                source_ref=existing.source_ref,
                projection_ref=existing.projection_ref,
                owner_module=existing.owner_module,
                recovery_point=existing.recovery_point,
                replay_generation=existing.replay_generation,
                ordering_sequence=existing.ordering_sequence,
                source_hash=existing.source_hash,
                projection_hash=existing.projection_hash,
                duplicate=True,
            )
        receipt = ReplayProjectionReceipt(
            source_ref=source.source_ref,
            projection_ref=projection_ref,
            owner_module=source.owner_module,
            recovery_point=source.recovery_point,
            replay_generation=expected_generation,
            ordering_sequence=source.ordering_sequence,
            source_hash=source.payload_hash,
            projection_hash=projection_hash,
            duplicate=False,
        )
        self._receipts[key] = receipt
        return receipt
