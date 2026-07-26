from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_json, canonical_sha256
from zuno.platform.database.foundation import InfrastructureRepository


class CapabilitySupplyChainConflict(RuntimeError):
    pass


class CapabilityActivationConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class CapabilityVersionInput:
    capability_definition_id: str
    capability_version_id: str
    tenant_id: str
    semantic_identity: str
    owner_module: str
    version_no: int
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    risk_profile_ref: str
    source_ref: str
    license_ref: str
    dependency_refs: tuple[str, ...]
    runtime_requirement_refs: tuple[str, ...]
    signature_ref: str
    verification_ref: str
    verified: bool


class CapabilityUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "CapabilityRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return CapabilityRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class CapabilityRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def publish_capability_version(self, item: CapabilityVersionInput) -> None:
        if not item.verified:
            raise CapabilitySupplyChainConflict("unverified CapabilityVersion cannot be published")
        if not (
            item.source_ref
            and item.license_ref
            and item.dependency_refs
            and item.runtime_requirement_refs
            and item.signature_ref
            and item.verification_ref
        ):
            raise CapabilitySupplyChainConflict(
                "CapabilityVersion supply-chain verification requires source, license, "
                "dependencies, runtime requirements, signature, and verification refs"
            )
        dependency_refs_hash = canonical_sha256(tuple(item.dependency_refs))
        runtime_requirement_refs_hash = canonical_sha256(tuple(item.runtime_requirement_refs))
        supply_chain_hash = canonical_sha256(
            {
                "source_ref": item.source_ref,
                "license_ref": item.license_ref,
                "dependency_refs_hash": dependency_refs_hash,
                "runtime_requirement_refs_hash": runtime_requirement_refs_hash,
                "signature_ref": item.signature_ref,
                "verification_ref": item.verification_ref,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO capability_definitions (
                    capability_definition_id, tenant_id, semantic_identity,
                    owner_module, status
                )
                VALUES (
                    :capability_definition_id, :tenant_id, :semantic_identity,
                    :owner_module, 'ACTIVE'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "capability_definition_id": item.capability_definition_id,
                "tenant_id": item.tenant_id,
                "semantic_identity": item.semantic_identity,
                "owner_module": item.owner_module,
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO capability_versions (
                    capability_version_id, capability_definition_id, version_no,
                    input_schema_hash, output_schema_hash, risk_profile_ref,
                    source_ref, license_ref, dependency_refs_hash,
                    runtime_requirement_refs_hash, signature_ref, verification_ref,
                    supply_chain_hash, supply_chain_verified, status
                )
                VALUES (
                    :capability_version_id, :capability_definition_id, :version_no,
                    :input_schema_hash, :output_schema_hash, :risk_profile_ref,
                    :source_ref, :license_ref, :dependency_refs_hash,
                    :runtime_requirement_refs_hash, :signature_ref, :verification_ref,
                    :supply_chain_hash, true, 'ACTIVE'
                )
                """
            ),
            {
                "capability_version_id": item.capability_version_id,
                "capability_definition_id": item.capability_definition_id,
                "version_no": item.version_no,
                "input_schema_hash": canonical_sha256(item.input_schema),
                "output_schema_hash": canonical_sha256(item.output_schema),
                "risk_profile_ref": item.risk_profile_ref,
                "source_ref": item.source_ref,
                "license_ref": item.license_ref,
                "dependency_refs_hash": dependency_refs_hash,
                "runtime_requirement_refs_hash": runtime_requirement_refs_hash,
                "signature_ref": item.signature_ref,
                "verification_ref": item.verification_ref,
                "supply_chain_hash": supply_chain_hash,
            },
        )

    def publish_skill_version(
        self,
        *,
        skill_version_id: str,
        tenant_id: str,
        skill_identity: str,
        version_no: int,
        metadata: dict[str, Any],
        instruction: dict[str, Any],
        resource_manifest: dict[str, Any],
        signature_ref: str,
        verified: bool,
    ) -> None:
        if not verified:
            raise CapabilitySupplyChainConflict("unverified SkillVersion cannot be published")
        self.connection.execute(
            text(
                """
                INSERT INTO skill_versions (
                    skill_version_id, tenant_id, skill_identity, version_no,
                    metadata_hash, instruction_hash, resource_manifest_hash,
                    signature_ref, status
                )
                VALUES (
                    :skill_version_id, :tenant_id, :skill_identity, :version_no,
                    :metadata_hash, :instruction_hash, :resource_manifest_hash,
                    :signature_ref, 'VERIFIED'
                )
                """
            ),
            {
                "skill_version_id": skill_version_id,
                "tenant_id": tenant_id,
                "skill_identity": skill_identity,
                "version_no": version_no,
                "metadata_hash": canonical_sha256(metadata),
                "instruction_hash": canonical_sha256(instruction),
                "resource_manifest_hash": canonical_sha256(resource_manifest),
                "signature_ref": signature_ref,
            },
        )

    def propose_binding(
        self,
        *,
        binding_id: str,
        capability_version_id: str,
        provider_instance_ref: str,
        tool_definition_ref: str,
        mapping_payload: dict[str, Any],
        proposal_source: str,
    ) -> None:
        status = "CONFORMANCE_PENDING"
        if proposal_source == "MODEL_PROPOSED":
            status = "PROPOSED"
        self.connection.execute(
            text(
                """
                INSERT INTO capability_provider_bindings (
                    binding_id, capability_version_id, provider_instance_ref,
                    tool_definition_ref, binding_hash, proposal_source, status
                )
                VALUES (
                    :binding_id, :capability_version_id, :provider_instance_ref,
                    :tool_definition_ref, :binding_hash, :proposal_source, :status
                )
                """
            ),
            {
                "binding_id": binding_id,
                "capability_version_id": capability_version_id,
                "provider_instance_ref": provider_instance_ref,
                "tool_definition_ref": tool_definition_ref,
                "binding_hash": canonical_sha256(mapping_payload),
                "proposal_source": proposal_source,
                "status": status,
            },
        )

    def record_conformance(
        self,
        *,
        conformance_id: str,
        binding_id: str,
        report_payload: dict[str, Any],
        covers_input: bool,
        covers_output: bool,
        covers_idempotency: bool,
        covers_reconciliation: bool,
        covers_security: bool,
    ) -> None:
        passed = (
            covers_input
            and covers_output
            and covers_idempotency
            and covers_reconciliation
            and covers_security
        )
        self.connection.execute(
            text(
                """
                INSERT INTO capability_conformance_records (
                    conformance_id, binding_id, conformance_hash, covers_input,
                    covers_output, covers_idempotency, covers_reconciliation,
                    covers_security, passed
                )
                VALUES (
                    :conformance_id, :binding_id, :conformance_hash, :covers_input,
                    :covers_output, :covers_idempotency, :covers_reconciliation,
                    :covers_security, :passed
                )
                """
            ),
            {
                "conformance_id": conformance_id,
                "binding_id": binding_id,
                "conformance_hash": canonical_sha256(report_payload),
                "covers_input": covers_input,
                "covers_output": covers_output,
                "covers_idempotency": covers_idempotency,
                "covers_reconciliation": covers_reconciliation,
                "covers_security": covers_security,
                "passed": passed,
            },
        )
        if passed:
            self.connection.execute(
                text(
                    """
                    UPDATE capability_provider_bindings
                    SET status = 'ACTIVE'
                    WHERE binding_id = :binding_id
                      AND proposal_source <> 'MODEL_PROPOSED'
                    """
                ),
                {"binding_id": binding_id},
            )

    def install_capability(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        workspace_id: str,
        capability_version_id: str,
        policy_ref: str,
    ) -> None:
        active_binding = self.connection.execute(
            text(
                """
                SELECT b.binding_id
                FROM capability_provider_bindings b
                JOIN capability_versions v ON v.capability_version_id = b.capability_version_id
                JOIN capability_definitions d ON d.capability_definition_id = v.capability_definition_id
                WHERE b.capability_version_id = :capability_version_id
                  AND b.status = 'ACTIVE'
                  AND v.status = 'ACTIVE'
                  AND v.supply_chain_verified = true
                  AND d.status = 'ACTIVE'
                  AND d.tenant_id = :tenant_id
                LIMIT 1
                """
            ),
            {
                "capability_version_id": capability_version_id,
                "tenant_id": tenant_id,
            },
        ).scalar_one_or_none()
        if active_binding is None:
            raise CapabilitySupplyChainConflict("capability installation requires active verified binding")
        self.connection.execute(
            text(
                """
                INSERT INTO capability_installations (
                    installation_id, tenant_id, workspace_id, capability_version_id,
                    policy_ref, status
                )
                VALUES (
                    :installation_id, :tenant_id, :workspace_id, :capability_version_id,
                    :policy_ref, 'ACTIVE'
                )
                """
            ),
            {
                "installation_id": installation_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "capability_version_id": capability_version_id,
                "policy_ref": policy_ref,
            },
        )

    def create_availability_snapshot(
        self,
        *,
        snapshot_id: str,
        tenant_id: str,
        workspace_id: str,
        principal_id: str,
        security_epoch_ref: str,
        source_generation: int,
        visible_candidates: tuple[str, ...],
        ttl_expires_at: datetime,
        runtime_signals: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        eligible_candidates = self._eligible_snapshot_candidates(
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            visible_candidates=visible_candidates,
            runtime_signals=runtime_signals or {},
        )
        self.connection.execute(
            text(
                """
                INSERT INTO capability_availability_snapshots (
                    snapshot_id, tenant_id, workspace_id, principal_id,
                    security_epoch_ref, source_generation, snapshot_hash,
                    ttl_expires_at
                )
                VALUES (
                    :snapshot_id, :tenant_id, :workspace_id, :principal_id,
                    :security_epoch_ref, :source_generation, :snapshot_hash,
                    :ttl_expires_at
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "snapshot_id": snapshot_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "principal_id": principal_id,
                "security_epoch_ref": security_epoch_ref,
                "source_generation": source_generation,
                "snapshot_hash": canonical_sha256({"candidates": eligible_candidates}),
                "ttl_expires_at": ttl_expires_at,
            },
        )

    def record_selection(
        self,
        *,
        selection_id: str,
        snapshot_id: str,
        requirement: dict[str, Any],
        selected_binding_id: str | None,
        candidate_summary: dict[str, Any],
        rejection_reason_codes: list[str],
    ) -> None:
        inserted = self.connection.execute(
            text(
                """
                INSERT INTO capability_selection_results (
                    selection_id, snapshot_id, requirement_hash,
                    selected_binding_id, candidate_summary_hash,
                    rejection_reason_codes, selection_hash
                )
                VALUES (
                    :selection_id, :snapshot_id, :requirement_hash,
                    :selected_binding_id, :candidate_summary_hash,
                    CAST(:rejection_reason_codes AS jsonb), :selection_hash
                )
                ON CONFLICT DO NOTHING
                RETURNING selection_id
                """
            ),
            {
                "selection_id": selection_id,
                "snapshot_id": snapshot_id,
                "requirement_hash": canonical_sha256(requirement),
                "selected_binding_id": selected_binding_id,
                "candidate_summary_hash": canonical_sha256(candidate_summary),
                "rejection_reason_codes": canonical_json(rejection_reason_codes),
                "selection_hash": canonical_sha256(
                    {
                        "requirement": requirement,
                        "selected_binding_id": selected_binding_id,
                        "candidate_summary": candidate_summary,
                        "rejection_reason_codes": rejection_reason_codes,
                    }
                ),
            },
        ).scalar_one_or_none()
        if inserted is None:
            return

        tenant_id = self.connection.execute(
            text(
                """
                SELECT tenant_id
                FROM capability_availability_snapshots
                WHERE snapshot_id = :snapshot_id
                """
            ),
            {"snapshot_id": snapshot_id},
        ).scalar_one()
        InfrastructureRepository(self.connection).enqueue_outbox(
            event_id=f"outbox:{selection_id}",
            tenant_id=str(tenant_id),
            aggregate_id=selection_id,
            topic="capability.selection.committed",
            idempotency_key=selection_id,
            ordering_key=snapshot_id,
            payload={
                "contract_name": "CapabilitySelectionResult",
                "producer_module": "Capability / Skill",
                "consumer_module": "Agent Core",
                "snapshot_id": snapshot_id,
                "selection_id": selection_id,
                "selected_binding_id": selected_binding_id,
                "requirement_hash": canonical_sha256(requirement),
                "candidate_summary_hash": canonical_sha256(candidate_summary),
                "rejection_reason_codes": rejection_reason_codes,
            },
        )

    def append_transition_event(
        self,
        *,
        transition_id: str,
        tenant_id: str,
        aggregate_ref: str,
        expected_generation: int,
        event_payload: dict[str, Any],
        outbox_message_id: str,
    ) -> None:
        current_generation = self._current_transition_generation(
            tenant_id=tenant_id,
            aggregate_ref=aggregate_ref,
        )
        if current_generation != expected_generation:
            raise CapabilityActivationConflict(
                f"stale capability transition generation: expected {expected_generation}, current {current_generation}"
            )
        self.connection.execute(
            text(
                """
                INSERT INTO capability_transition_events (
                    transition_id, tenant_id, aggregate_ref, expected_generation,
                    committed_generation, event_hash, outbox_message_id
                )
                VALUES (
                    :transition_id, :tenant_id, :aggregate_ref, :expected_generation,
                    :committed_generation, :event_hash, :outbox_message_id
                )
                """
            ),
            {
                "transition_id": transition_id,
                "tenant_id": tenant_id,
                "aggregate_ref": aggregate_ref,
                "expected_generation": expected_generation,
                "committed_generation": expected_generation + 1,
                "event_hash": canonical_sha256(event_payload),
                "outbox_message_id": outbox_message_id,
            },
        )
        InfrastructureRepository(self.connection).enqueue_outbox(
            event_id=outbox_message_id,
            tenant_id=tenant_id,
            aggregate_id=aggregate_ref,
            topic="capability.transition.committed",
            idempotency_key=transition_id,
            ordering_key=aggregate_ref,
            payload={
                "contract_name": "CapabilityTransitionEvent",
                "producer_module": "Capability / Skill",
                "consumer_module": "Agent Core",
                "transition_id": transition_id,
                "aggregate_ref": aggregate_ref,
                "expected_generation": expected_generation,
                "committed_generation": expected_generation + 1,
                "event_hash": canonical_sha256(event_payload),
            },
        )

    def activate_installation(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        expected_generation: int,
        activation_ref: str,
        policy_epoch_ref: str,
        outbox_message_id: str,
    ) -> None:
        self._transition_installation(
            installation_id=installation_id,
            tenant_id=tenant_id,
            expected_generation=expected_generation,
            status="ACTIVE",
            transition_id=activation_ref,
            policy_epoch_ref=policy_epoch_ref,
            outbox_message_id=outbox_message_id,
        )

    def revoke_installation(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        expected_generation: int,
        revocation_ref: str,
        policy_epoch_ref: str,
        outbox_message_id: str,
    ) -> None:
        self._transition_installation(
            installation_id=installation_id,
            tenant_id=tenant_id,
            expected_generation=expected_generation,
            status="REVOKED",
            transition_id=revocation_ref,
            policy_epoch_ref=policy_epoch_ref,
            outbox_message_id=outbox_message_id,
        )

    def _transition_installation(
        self,
        *,
        installation_id: str,
        tenant_id: str,
        expected_generation: int,
        status: str,
        transition_id: str,
        policy_epoch_ref: str,
        outbox_message_id: str,
    ) -> None:
        existing = self.connection.execute(
            text(
                """
                SELECT installation_id
                FROM capability_installations
                WHERE installation_id = :installation_id
                  AND tenant_id = :tenant_id
                """
            ),
            {"installation_id": installation_id, "tenant_id": tenant_id},
        ).scalar_one_or_none()
        if existing is None:
            raise CapabilityActivationConflict("unknown capability installation")
        self.append_transition_event(
            transition_id=transition_id,
            tenant_id=tenant_id,
            aggregate_ref=installation_id,
            expected_generation=expected_generation,
            event_payload={
                "installation_id": installation_id,
                "status": status,
                "policy_epoch_ref": policy_epoch_ref,
            },
            outbox_message_id=outbox_message_id,
        )
        self.connection.execute(
            text(
                """
                UPDATE capability_installations
                SET status = :status,
                    policy_ref = :policy_epoch_ref
                WHERE installation_id = :installation_id
                  AND tenant_id = :tenant_id
                """
            ),
            {
                "status": status,
                "policy_epoch_ref": policy_epoch_ref,
                "installation_id": installation_id,
                "tenant_id": tenant_id,
            },
        )

    def _current_transition_generation(self, *, tenant_id: str, aggregate_ref: str) -> int:
        return int(
            self.connection.execute(
                text(
                    """
                    SELECT coalesce(max(committed_generation), 0)
                    FROM capability_transition_events
                    WHERE tenant_id = :tenant_id
                      AND aggregate_ref = :aggregate_ref
                    """
                ),
                {"tenant_id": tenant_id, "aggregate_ref": aggregate_ref},
            ).scalar_one()
        )

    def _eligible_snapshot_candidates(
        self,
        *,
        tenant_id: str,
        workspace_id: str,
        visible_candidates: tuple[str, ...],
        runtime_signals: dict[str, dict[str, Any]],
    ) -> tuple[str, ...]:
        if not visible_candidates:
            return ()
        rows = self.connection.execute(
            text(
                """
                SELECT b.binding_id
                FROM capability_provider_bindings b
                JOIN capability_versions v ON v.capability_version_id = b.capability_version_id
                JOIN capability_installations i ON i.capability_version_id = v.capability_version_id
                WHERE i.tenant_id = :tenant_id
                  AND i.workspace_id = :workspace_id
                  AND i.status = 'ACTIVE'
                  AND b.status = 'ACTIVE'
                  AND v.supply_chain_verified = true
                  AND b.binding_id = ANY(CAST(:visible_candidates AS text[]))
                ORDER BY b.binding_id
                """
            ),
            {
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "visible_candidates": list(visible_candidates),
            },
        ).scalars().all()
        return tuple(
            binding_id
            for binding_id in (str(row) for row in rows)
            if _runtime_signal_allows(runtime_signals.get(binding_id))
        )


def _runtime_signal_allows(signal: dict[str, Any] | None) -> bool:
    if signal is None:
        return True
    health = str(signal.get("health") or signal.get("status") or "healthy").lower()
    if health not in {"healthy", "ready", "ok", "available"}:
        return False
    quota_remaining = signal.get("quota_remaining")
    if quota_remaining is not None and int(quota_remaining) <= 0:
        return False
    capacity_remaining = signal.get("capacity_remaining")
    if capacity_remaining is not None and int(capacity_remaining) <= 0:
        return False
    return True


__all__ = [
    "CapabilityActivationConflict",
    "CapabilityRepository",
    "CapabilitySupplyChainConflict",
    "CapabilityUnitOfWork",
    "CapabilityVersionInput",
]
