from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_json, canonical_sha256


class CapabilitySupplyChainConflict(RuntimeError):
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
                    input_schema_hash, output_schema_hash, risk_profile_ref, status
                )
                VALUES (
                    :capability_version_id, :capability_definition_id, :version_no,
                    :input_schema_hash, :output_schema_hash, :risk_profile_ref, 'ACTIVE'
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
    ) -> None:
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
                "snapshot_hash": canonical_sha256({"candidates": visible_candidates}),
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
        self.connection.execute(
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


__all__ = [
    "CapabilityRepository",
    "CapabilitySupplyChainConflict",
    "CapabilityUnitOfWork",
    "CapabilityVersionInput",
]
