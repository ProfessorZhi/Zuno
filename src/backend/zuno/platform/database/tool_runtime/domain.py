from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, Engine, text

from zuno.platform.contracts import canonical_json, canonical_sha256


class ToolRuntimeConflict(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ToolVersionInput:
    tool_definition_id: str
    tool_version_id: str
    tenant_id: str
    version_no: int
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    adapter_kind: str
    effect_level: str


@dataclass(frozen=True, slots=True)
class PreparedToolActionInput:
    prepared_tool_action_id: str
    tenant_id: str
    workspace_id: str
    tool_operation_id: str
    canonical_args: dict[str, Any]
    target_resources: tuple[str, ...]
    effect_level: str
    approval_required: bool
    idempotency_key: str
    security_epoch_ref: str
    effect_policy_version: str = ""
    effect_policy_hash: str = ""
    target_resource_set_ref: str = ""
    target_conflict_keys: tuple[str, ...] = ()
    action_proposal_ref: str = ""
    status: str = "PREPARED"


@dataclass(frozen=True, slots=True)
class ToolAttemptInput:
    attempt_id: str
    tenant_id: str
    prepared_tool_action_id: str
    status: str
    dispatch_certainty: str
    adapter_family: str
    hidden_retry_count: int
    state_history: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ToolObservationInput:
    observation_id: str
    tenant_id: str
    attempt_id: str
    owner_module: str
    normalized_projection_owner: str
    output_trusted: bool
    schema_valid: bool
    memory_write_allowed: bool
    evidence_write_allowed: bool
    payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolExecutionReceiptInput:
    receipt_id: str
    tenant_id: str
    prepared_tool_action_id: str
    attempt_id: str
    status: str
    dispatch_certainty: str
    effect_certainty: str
    append_only_generation: int
    receipt_payload: dict[str, Any]


class ToolUnitOfWork:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def __enter__(self) -> "ToolRepository":
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        return ToolRepository(self._connection)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            self._connection.close()


class ToolRepository:
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def publish_provider(
        self,
        *,
        provider_id: str,
        tenant_id: str,
        owner_module: str,
        provider_name: str,
        status: str,
        provider_payload: dict[str, Any],
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_providers (
                    provider_id, tenant_id, owner_module, provider_name, status, schema_hash
                )
                VALUES (
                    :provider_id, :tenant_id, :owner_module, :provider_name, :status, :schema_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "provider_id": provider_id,
                "tenant_id": tenant_id,
                "owner_module": owner_module,
                "provider_name": provider_name,
                "status": status,
                "schema_hash": canonical_sha256(provider_payload),
            },
        )

    def publish_tool_version(self, version: ToolVersionInput) -> None:
        provider_id = version.tool_definition_id
        tool_id = version.tool_definition_id
        operation_id = f"{version.tool_version_id}:operation:default"
        operation_name = "default"

        self.publish_provider(
            provider_id=provider_id,
            tenant_id=version.tenant_id,
            owner_module="08 Tool Runtime",
            provider_name=version.tool_definition_id,
            status="ACTIVE",
            provider_payload={
                "tool_definition_id": version.tool_definition_id,
                "tool_version_id": version.tool_version_id,
                "adapter_kind": version.adapter_kind,
                "effect_level": version.effect_level,
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO tool_definitions (
                    tool_definition_id, tenant_id, provider_id, tool_id,
                    semantic_identity, owner_module, effect_class, input_schema_hash,
                    output_schema_hash, status, generation
                )
                VALUES (
                    :tool_definition_id, :tenant_id, :provider_id, :tool_id,
                    :semantic_identity, :owner_module, :effect_class, :input_schema_hash,
                    :output_schema_hash, 'ACTIVE', 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "tool_definition_id": version.tool_definition_id,
                "tenant_id": version.tenant_id,
                "provider_id": provider_id,
                "tool_id": tool_id,
                "semantic_identity": version.tool_definition_id,
                "owner_module": "08 Tool Runtime",
                "effect_class": version.effect_level,
                "input_schema_hash": canonical_sha256(version.input_schema),
                "output_schema_hash": canonical_sha256(version.output_schema),
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO tool_versions (
                    tool_version_id, tenant_id, tool_definition_id, version_no,
                    input_schema_hash, output_schema_hash, adapter_kind, effect_level,
                    status, generation
                )
                VALUES (
                    :tool_version_id, :tenant_id, :tool_definition_id, :version_no,
                    :input_schema_hash, :output_schema_hash, :adapter_kind, :effect_level,
                    'ACTIVE', 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "tool_version_id": version.tool_version_id,
                "tenant_id": version.tenant_id,
                "tool_definition_id": version.tool_definition_id,
                "version_no": version.version_no,
                "input_schema_hash": canonical_sha256(version.input_schema),
                "output_schema_hash": canonical_sha256(version.output_schema),
                "adapter_kind": version.adapter_kind,
                "effect_level": version.effect_level,
            },
        )
        self.connection.execute(
            text(
                """
                INSERT INTO tool_operations (
                    tool_operation_id, tenant_id, tool_version_id, operation_name,
                    input_schema_hash, output_schema_hash, effect_level, status
                )
                VALUES (
                    :tool_operation_id, :tenant_id, :tool_version_id, :operation_name,
                    :input_schema_hash, :output_schema_hash, :effect_level, 'ACTIVE'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "tool_operation_id": operation_id,
                "tenant_id": version.tenant_id,
                "tool_version_id": version.tool_version_id,
                "operation_name": operation_name,
                "input_schema_hash": canonical_sha256(version.input_schema),
                "output_schema_hash": canonical_sha256(version.output_schema),
                "effect_level": version.effect_level,
            },
        )

    def install_tool(
        self,
        *,
        tool_installation_id: str,
        tenant_id: str,
        workspace_id: str,
        tool_version_id: str,
        policy_ref: str,
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_installations (
                    tool_installation_id, tenant_id, workspace_id, tool_version_id,
                    policy_ref, status, generation
                )
                VALUES (
                    :tool_installation_id, :tenant_id, :workspace_id, :tool_version_id,
                    :policy_ref, 'INSTALLED', 1
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "tool_installation_id": tool_installation_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "tool_version_id": tool_version_id,
                "policy_ref": policy_ref,
            },
        )

    def record_adapter_binding(
        self,
        *,
        adapter_binding_id: str,
        tenant_id: str,
        tool_version_id: str,
        adapter_kind: str,
        adapter_version: str,
        conformance_payload: dict[str, Any],
        status: str = "ACTIVE",
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_adapter_bindings (
                    adapter_binding_id, tenant_id, tool_version_id, adapter_kind,
                    adapter_version, conformance_hash, status
                )
                VALUES (
                    :adapter_binding_id, :tenant_id, :tool_version_id, :adapter_kind,
                    :adapter_version, :conformance_hash, :status
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "adapter_binding_id": adapter_binding_id,
                "tenant_id": tenant_id,
                "tool_version_id": tool_version_id,
                "adapter_kind": adapter_kind,
                "adapter_version": adapter_version,
                "conformance_hash": canonical_sha256(conformance_payload),
                "status": status,
            },
        )

    def activate_tool(
        self,
        *,
        tool_activation_id: str,
        tenant_id: str,
        workspace_id: str,
        tool_installation_id: str,
        expected_generation: int,
        activation_payload: dict[str, Any],
    ) -> None:
        row = self.connection.execute(
            text(
                """
                SELECT status, generation
                FROM tool_installations
                WHERE tool_installation_id = :tool_installation_id
                FOR UPDATE
                """
            ),
            {"tool_installation_id": tool_installation_id},
        ).one()
        if row.status not in {"INSTALLED", "ACTIVE"}:
            raise ToolRuntimeConflict("only installed tool can activate")
        self.connection.execute(
            text(
                """
                INSERT INTO tool_activations (
                    tool_activation_id, tenant_id, workspace_id, tool_installation_id,
                    expected_generation, committed_generation, activation_hash, status
                )
                VALUES (
                    :tool_activation_id, :tenant_id, :workspace_id, :tool_installation_id,
                    :expected_generation, :committed_generation, :activation_hash, 'ACTIVE'
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "tool_activation_id": tool_activation_id,
                "tenant_id": tenant_id,
                "workspace_id": workspace_id,
                "tool_installation_id": tool_installation_id,
                "expected_generation": expected_generation,
                "committed_generation": expected_generation + 1,
                "activation_hash": canonical_sha256(activation_payload),
            },
        )

    def prepare_action(self, prepared: PreparedToolActionInput) -> None:
        canonical_args_hash = canonical_sha256(prepared.canonical_args)
        target_resources_hash = canonical_sha256(list(prepared.target_resources))
        prepared_hash = canonical_sha256(
            {
                "action_proposal_ref": prepared.action_proposal_ref,
                "tool_operation_id": prepared.tool_operation_id,
                "canonical_args": prepared.canonical_args,
                "target_resources": list(prepared.target_resources),
                "target_resource_set_ref": prepared.target_resource_set_ref,
                "target_conflict_keys": list(prepared.target_conflict_keys),
                "effect_level": prepared.effect_level,
                "effect_policy_version": prepared.effect_policy_version,
                "effect_policy_hash": prepared.effect_policy_hash,
                "approval_required": prepared.approval_required,
                "security_epoch_ref": prepared.security_epoch_ref,
                "idempotency_key": prepared.idempotency_key,
            }
        )
        self.connection.execute(
            text(
                """
                INSERT INTO prepared_tool_actions (
                    prepared_tool_action_id, tenant_id, workspace_id, tool_operation_id,
                    canonical_args_hash, target_resources_hash, prepared_action_hash,
                    effect_level, status, approval_required, idempotency_key,
                    security_epoch_ref
                )
                VALUES (
                    :prepared_tool_action_id, :tenant_id, :workspace_id, :tool_operation_id,
                    :canonical_args_hash, :target_resources_hash, :prepared_action_hash,
                    :effect_level, :status, :approval_required, :idempotency_key,
                    :security_epoch_ref
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "prepared_tool_action_id": prepared.prepared_tool_action_id,
                "tenant_id": prepared.tenant_id,
                "workspace_id": prepared.workspace_id,
                "tool_operation_id": prepared.tool_operation_id,
                "canonical_args_hash": canonical_args_hash,
                "target_resources_hash": target_resources_hash,
                "prepared_action_hash": prepared_hash,
                "effect_level": prepared.effect_level,
                "status": prepared.status,
                "approval_required": prepared.approval_required,
                "idempotency_key": prepared.idempotency_key,
                "security_epoch_ref": prepared.security_epoch_ref,
            },
        )

    def record_attempt(self, attempt: ToolAttemptInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_attempts (
                    attempt_id, tenant_id, prepared_tool_action_id, status,
                    dispatch_certainty, adapter_family, hidden_retry_count,
                    state_history
                )
                VALUES (
                    :attempt_id, :tenant_id, :prepared_tool_action_id, :status,
                    :dispatch_certainty, :adapter_family, :hidden_retry_count,
                    CAST(:state_history AS jsonb)
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "attempt_id": attempt.attempt_id,
                "tenant_id": attempt.tenant_id,
                "prepared_tool_action_id": attempt.prepared_tool_action_id,
                "status": attempt.status,
                "dispatch_certainty": attempt.dispatch_certainty,
                "adapter_family": attempt.adapter_family,
                "hidden_retry_count": attempt.hidden_retry_count,
                "state_history": canonical_json(list(attempt.state_history)),
            },
        )

    def record_observation(self, observation: ToolObservationInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_observations (
                    observation_id, tenant_id, attempt_id, owner_module,
                    normalized_projection_owner, output_trusted, schema_valid,
                    memory_write_allowed, evidence_write_allowed, redacted_payload_hash
                )
                VALUES (
                    :observation_id, :tenant_id, :attempt_id, :owner_module,
                    :normalized_projection_owner, :output_trusted, :schema_valid,
                    :memory_write_allowed, :evidence_write_allowed, :redacted_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "observation_id": observation.observation_id,
                "tenant_id": observation.tenant_id,
                "attempt_id": observation.attempt_id,
                "owner_module": observation.owner_module,
                "normalized_projection_owner": observation.normalized_projection_owner,
                "output_trusted": observation.output_trusted,
                "schema_valid": observation.schema_valid,
                "memory_write_allowed": observation.memory_write_allowed,
                "evidence_write_allowed": observation.evidence_write_allowed,
                "redacted_payload_hash": canonical_sha256(observation.payload),
            },
        )

    def record_execution_receipt(self, receipt: ToolExecutionReceiptInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_execution_receipts (
                    receipt_id, tenant_id, prepared_tool_action_id, attempt_id, status,
                    dispatch_certainty, effect_certainty, append_only_generation,
                    receipt_hash
                )
                VALUES (
                    :receipt_id, :tenant_id, :prepared_tool_action_id, :attempt_id, :status,
                    :dispatch_certainty, :effect_certainty, :append_only_generation,
                    :receipt_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "receipt_id": receipt.receipt_id,
                "tenant_id": receipt.tenant_id,
                "prepared_tool_action_id": receipt.prepared_tool_action_id,
                "attempt_id": receipt.attempt_id,
                "status": receipt.status,
                "dispatch_certainty": receipt.dispatch_certainty,
                "effect_certainty": receipt.effect_certainty,
                "append_only_generation": receipt.append_only_generation,
                "receipt_hash": canonical_sha256(receipt.receipt_payload),
            },
        )

    def record_bypass_guard(
        self,
        *,
        receipt_id: str,
        tenant_id: str,
        scope: str,
        allowlist_count: int,
        guard_payload: dict[str, Any],
    ) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_bypass_guard_receipts (
                    receipt_id, tenant_id, scope, allowlist_count, guard_hash
                )
                VALUES (
                    :receipt_id, :tenant_id, :scope, :allowlist_count, :guard_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "receipt_id": receipt_id,
                "tenant_id": tenant_id,
                "scope": scope,
                "allowlist_count": allowlist_count,
                "guard_hash": canonical_sha256(guard_payload),
            },
        )


__all__ = [
    "PreparedToolActionInput",
    "ToolAttemptInput",
    "ToolExecutionReceiptInput",
    "ToolObservationInput",
    "ToolRepository",
    "ToolRuntimeConflict",
    "ToolUnitOfWork",
    "ToolVersionInput",
]
