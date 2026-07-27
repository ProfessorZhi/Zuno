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

@dataclass(frozen=True, slots=True)
class ToolEffectReceiptInput:
    effect_receipt_id: str
    tenant_id: str
    prepared_tool_action_id: str
    attempt_id: str
    execution_receipt_id: str
    provider_effect_id: str
    effect_status: str
    effect_certainty: str
    idempotency_scope: str
    idempotency_key: str
    idempotency_generation: int
    fencing_resource_id: str
    fencing_lease_id: str
    fencing_epoch: int
    secret_lease_id: str | None
    native_result: dict[str, Any]
    effect_payload: dict[str, Any]
    append_only_generation: int

@dataclass(frozen=True, slots=True)
class ToolEffectReconciliationInput:
    reconciliation_id: str
    tenant_id: str
    prepared_tool_action_id: str
    attempt_id: str
    execution_receipt_id: str
    provider_effect_id: str
    status: str
    next_action: str
    reconciliation_query: dict[str, Any]
    manual_assessment_required: bool
    age_escalation_after_seconds: int
    idempotency_scope: str
    idempotency_key: str
    idempotency_generation: int
    fencing_resource_id: str
    fencing_lease_id: str
    fencing_epoch: int
    secret_lease_id: str | None
    reconciliation_payload: dict[str, Any]

@dataclass(frozen=True, slots=True)
class ToolAsyncJobInput:
    async_job_id: str
    tenant_id: str
    prepared_tool_action_id: str
    attempt_id: str
    execution_receipt_id: str
    provider_job_id: str
    status: str
    callback_binding_ref: str
    callback_order: int
    deadline_at: Any
    idempotency_scope: str
    idempotency_key: str
    idempotency_generation: int
    fencing_resource_id: str
    fencing_lease_id: str
    fencing_epoch: int
    secret_lease_id: str | None
    job_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolAsyncCallbackInput:
    callback_id: str
    tenant_id: str
    async_job_id: str
    provider_job_id: str
    callback_order: int
    authenticity_status: str
    accepted: bool
    callback_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCancellationReceiptInput:
    cancellation_receipt_id: str
    tenant_id: str
    prepared_tool_action_id: str
    attempt_id: str
    async_job_id: str | None
    provider_job_id: str
    status: str
    external_effect_revoked: bool
    requested_by_principal_id: str
    audit_requirement_id: str
    cancellation_payload: dict[str, Any]

@dataclass(frozen=True, slots=True)
class ToolCompensationDefinitionInput:
    compensation_definition_id: str
    tenant_id: str
    source_effect_receipt_id: str | None
    source_reconciliation_id: str | None
    compensation_capability: str
    operation_ref: str
    new_action_proposal_ref: str
    requires_approval: bool
    window_deadline_at: Any
    residual_impact: str
    policy_ref: str
    definition_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCompensationAttemptInput:
    compensation_attempt_id: str
    tenant_id: str
    compensation_definition_id: str
    prepared_tool_action_id: str
    attempt_id: str
    execution_receipt_id: str
    status: str
    hidden_rollback: bool
    idempotency_scope: str
    idempotency_key: str
    idempotency_generation: int
    audit_requirement_id: str
    attempt_payload: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolManualEffectAssessmentInput:
    manual_assessment_id: str
    tenant_id: str
    reconciliation_id: str
    provider_effect_id: str
    conclusion: str
    confidence: float
    assessor_principal_id: str
    residual_uncertainty: str
    evidence_payload: dict[str, Any]
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

    def prepare_action(self, prepared: PreparedToolActionInput) -> str:
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
        return prepared_hash

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

    def record_effect_receipt(self, receipt: ToolEffectReceiptInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_effect_receipts (
                    effect_receipt_id, tenant_id, prepared_tool_action_id, attempt_id,
                    execution_receipt_id, provider_effect_id, effect_status,
                    effect_certainty, idempotency_scope, idempotency_key,
                    idempotency_generation, fencing_resource_id, fencing_lease_id,
                    fencing_epoch, secret_lease_id, native_result_hash,
                    effect_payload_hash, append_only_generation
                )
                VALUES (
                    :effect_receipt_id, :tenant_id, :prepared_tool_action_id, :attempt_id,
                    :execution_receipt_id, :provider_effect_id, :effect_status,
                    :effect_certainty, :idempotency_scope, :idempotency_key,
                    :idempotency_generation, :fencing_resource_id, :fencing_lease_id,
                    :fencing_epoch, :secret_lease_id, :native_result_hash,
                    :effect_payload_hash, :append_only_generation
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "effect_receipt_id": receipt.effect_receipt_id,
                "tenant_id": receipt.tenant_id,
                "prepared_tool_action_id": receipt.prepared_tool_action_id,
                "attempt_id": receipt.attempt_id,
                "execution_receipt_id": receipt.execution_receipt_id,
                "provider_effect_id": receipt.provider_effect_id,
                "effect_status": receipt.effect_status,
                "effect_certainty": receipt.effect_certainty,
                "idempotency_scope": receipt.idempotency_scope,
                "idempotency_key": receipt.idempotency_key,
                "idempotency_generation": receipt.idempotency_generation,
                "fencing_resource_id": receipt.fencing_resource_id,
                "fencing_lease_id": receipt.fencing_lease_id,
                "fencing_epoch": receipt.fencing_epoch,
                "secret_lease_id": receipt.secret_lease_id,
                "native_result_hash": canonical_sha256(receipt.native_result),
                "effect_payload_hash": canonical_sha256(receipt.effect_payload),
                "append_only_generation": receipt.append_only_generation,
            },
        )


    def record_effect_reconciliation(self, reconciliation: ToolEffectReconciliationInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_effect_reconciliations (
                    reconciliation_id, tenant_id, prepared_tool_action_id, attempt_id,
                    execution_receipt_id, provider_effect_id, status, next_action,
                    reconciliation_query_hash, manual_assessment_required,
                    age_escalation_after_seconds, idempotency_scope, idempotency_key,
                    idempotency_generation, fencing_resource_id, fencing_lease_id,
                    fencing_epoch, secret_lease_id, reconciliation_payload_hash
                )
                VALUES (
                    :reconciliation_id, :tenant_id, :prepared_tool_action_id, :attempt_id,
                    :execution_receipt_id, :provider_effect_id, :status, :next_action,
                    :reconciliation_query_hash, :manual_assessment_required,
                    :age_escalation_after_seconds, :idempotency_scope, :idempotency_key,
                    :idempotency_generation, :fencing_resource_id, :fencing_lease_id,
                    :fencing_epoch, :secret_lease_id, :reconciliation_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "reconciliation_id": reconciliation.reconciliation_id,
                "tenant_id": reconciliation.tenant_id,
                "prepared_tool_action_id": reconciliation.prepared_tool_action_id,
                "attempt_id": reconciliation.attempt_id,
                "execution_receipt_id": reconciliation.execution_receipt_id,
                "provider_effect_id": reconciliation.provider_effect_id,
                "status": reconciliation.status,
                "next_action": reconciliation.next_action,
                "reconciliation_query_hash": canonical_sha256(reconciliation.reconciliation_query),
                "manual_assessment_required": reconciliation.manual_assessment_required,
                "age_escalation_after_seconds": reconciliation.age_escalation_after_seconds,
                "idempotency_scope": reconciliation.idempotency_scope,
                "idempotency_key": reconciliation.idempotency_key,
                "idempotency_generation": reconciliation.idempotency_generation,
                "fencing_resource_id": reconciliation.fencing_resource_id,
                "fencing_lease_id": reconciliation.fencing_lease_id,
                "fencing_epoch": reconciliation.fencing_epoch,
                "secret_lease_id": reconciliation.secret_lease_id,
                "reconciliation_payload_hash": canonical_sha256(reconciliation.reconciliation_payload),
            },
        )

    def existing_side_effect_result_ref(self, *, tenant_id: str, call_id: str) -> str:
        effect_receipt_id = f"tool-effect-receipt:{call_id}"
        reconciliation_id = f"tool-effect-reconciliation:{call_id}"
        async_job_id = f"tool-async-job:{call_id}"
        row = self.connection.execute(
            text(
                """
                SELECT result_ref
                FROM (
                    SELECT effect_receipt_id AS result_ref, 1 AS priority
                    FROM tool_effect_receipts
                    WHERE tenant_id = :tenant_id AND effect_receipt_id = :effect_receipt_id
                    UNION ALL
                    SELECT reconciliation_id AS result_ref, 2 AS priority
                    FROM tool_effect_reconciliations
                    WHERE tenant_id = :tenant_id AND reconciliation_id = :reconciliation_id
                    UNION ALL
                    SELECT async_job_id AS result_ref, 3 AS priority
                    FROM tool_async_jobs
                    WHERE tenant_id = :tenant_id AND async_job_id = :async_job_id
                ) existing_results
                ORDER BY priority
                LIMIT 1
                """
            ),
            {
                "tenant_id": tenant_id,
                "effect_receipt_id": effect_receipt_id,
                "reconciliation_id": reconciliation_id,
                "async_job_id": async_job_id,
            },
        ).first()
        return "" if row is None else str(row.result_ref)


    def escalate_due_reconciliations(self, *, tenant_id: str, now: Any) -> int:
        result = self.connection.execute(
            text(
                """
                UPDATE tool_effect_reconciliations
                SET status = 'ESCALATED',
                    next_action = 'MANUAL_ASSESSMENT',
                    manual_assessment_required = true,
                    updated_at = :now
                WHERE tenant_id = :tenant_id
                  AND status in ('OPEN', 'WAITING_PROVIDER')
                  AND created_at + make_interval(secs => age_escalation_after_seconds) <= :now
                """
            ),
            {"tenant_id": tenant_id, "now": now},
        )
        return int(result.rowcount or 0)

    def timeout_due_async_jobs(self, *, tenant_id: str, now: Any) -> int:
        result = self.connection.execute(
            text(
                """
                UPDATE tool_async_jobs
                SET status = 'TIMEOUT',
                    updated_at = :now
                WHERE tenant_id = :tenant_id
                  AND status = 'WAITING_CALLBACK'
                  AND deadline_at <= :now
                """
            ),
            {"tenant_id": tenant_id, "now": now},
        )
        return int(result.rowcount or 0)

    def record_async_job(self, job: ToolAsyncJobInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_async_jobs (
                    async_job_id, tenant_id, prepared_tool_action_id, attempt_id,
                    execution_receipt_id, provider_job_id, status, callback_binding_ref,
                    callback_order, deadline_at, idempotency_scope, idempotency_key,
                    idempotency_generation, fencing_resource_id, fencing_lease_id,
                    fencing_epoch, secret_lease_id, job_payload_hash
                )
                VALUES (
                    :async_job_id, :tenant_id, :prepared_tool_action_id, :attempt_id,
                    :execution_receipt_id, :provider_job_id, :status, :callback_binding_ref,
                    :callback_order, :deadline_at, :idempotency_scope, :idempotency_key,
                    :idempotency_generation, :fencing_resource_id, :fencing_lease_id,
                    :fencing_epoch, :secret_lease_id, :job_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "async_job_id": job.async_job_id,
                "tenant_id": job.tenant_id,
                "prepared_tool_action_id": job.prepared_tool_action_id,
                "attempt_id": job.attempt_id,
                "execution_receipt_id": job.execution_receipt_id,
                "provider_job_id": job.provider_job_id,
                "status": job.status,
                "callback_binding_ref": job.callback_binding_ref,
                "callback_order": job.callback_order,
                "deadline_at": job.deadline_at,
                "idempotency_scope": job.idempotency_scope,
                "idempotency_key": job.idempotency_key,
                "idempotency_generation": job.idempotency_generation,
                "fencing_resource_id": job.fencing_resource_id,
                "fencing_lease_id": job.fencing_lease_id,
                "fencing_epoch": job.fencing_epoch,
                "secret_lease_id": job.secret_lease_id,
                "job_payload_hash": canonical_sha256(job.job_payload),
            },
        )


    def latest_async_callback_order(self, *, async_job_id: str) -> int:
        value = self.connection.execute(
            text(
                """
                SELECT COALESCE(MAX(callback_order), 0)
                FROM tool_async_callbacks
                WHERE async_job_id = :async_job_id
                  AND accepted = true
                """
            ),
            {"async_job_id": async_job_id},
        ).scalar_one()
        return int(value or 0)
    def record_async_callback(self, callback: ToolAsyncCallbackInput) -> bool:
        row = self.connection.execute(
            text(
                """
                INSERT INTO tool_async_callbacks (
                    callback_id, tenant_id, async_job_id, provider_job_id,
                    callback_order, authenticity_status, accepted, callback_payload_hash
                )
                VALUES (
                    :callback_id, :tenant_id, :async_job_id, :provider_job_id,
                    :callback_order, :authenticity_status, :accepted, :callback_payload_hash
                )
                ON CONFLICT (callback_id) DO UPDATE
                SET authenticity_status = CASE
                        WHEN tool_async_callbacks.accepted = false
                         AND EXCLUDED.authenticity_status = 'VERIFIED'
                        THEN 'VERIFIED'
                        ELSE tool_async_callbacks.authenticity_status
                    END,
                    accepted = CASE
                        WHEN tool_async_callbacks.accepted = false
                         AND EXCLUDED.authenticity_status = 'VERIFIED'
                        THEN true
                        ELSE tool_async_callbacks.accepted
                    END,
                    callback_payload_hash = CASE
                        WHEN tool_async_callbacks.accepted = false
                         AND EXCLUDED.authenticity_status = 'VERIFIED'
                        THEN EXCLUDED.callback_payload_hash
                        ELSE tool_async_callbacks.callback_payload_hash
                    END
                RETURNING accepted
                """
            ),
            {
                "callback_id": callback.callback_id,
                "tenant_id": callback.tenant_id,
                "async_job_id": callback.async_job_id,
                "provider_job_id": callback.provider_job_id,
                "callback_order": callback.callback_order,
                "authenticity_status": callback.authenticity_status,
                "accepted": callback.accepted,
                "callback_payload_hash": canonical_sha256(callback.callback_payload),
            },
        ).one()
        return bool(row.accepted)

    def advance_async_job_after_callback(
        self,
        *,
        async_job_id: str,
        callback_order: int,
        completed: bool,
    ) -> None:
        self.connection.execute(
            text(
                """
                UPDATE tool_async_jobs
                SET callback_order = :callback_order,
                    status = CASE WHEN :completed THEN 'COMPLETED' ELSE status END,
                    updated_at = now()
                WHERE async_job_id = :async_job_id
                  AND status = 'WAITING_CALLBACK'
                  AND callback_order < :callback_order
                """
            ),
            {
                "async_job_id": async_job_id,
                "callback_order": callback_order,
                "completed": completed,
            },
        )

    def record_cancellation_receipt(self, cancellation: ToolCancellationReceiptInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_cancellation_receipts (
                    cancellation_receipt_id, tenant_id, prepared_tool_action_id, attempt_id,
                    async_job_id, provider_job_id, status, external_effect_revoked,
                    requested_by_principal_id, audit_requirement_id, cancellation_payload_hash
                )
                VALUES (
                    :cancellation_receipt_id, :tenant_id, :prepared_tool_action_id, :attempt_id,
                    :async_job_id, :provider_job_id, :status, :external_effect_revoked,
                    :requested_by_principal_id, :audit_requirement_id, :cancellation_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "cancellation_receipt_id": cancellation.cancellation_receipt_id,
                "tenant_id": cancellation.tenant_id,
                "prepared_tool_action_id": cancellation.prepared_tool_action_id,
                "attempt_id": cancellation.attempt_id,
                "async_job_id": cancellation.async_job_id,
                "provider_job_id": cancellation.provider_job_id,
                "status": cancellation.status,
                "external_effect_revoked": cancellation.external_effect_revoked,
                "requested_by_principal_id": cancellation.requested_by_principal_id,
                "audit_requirement_id": cancellation.audit_requirement_id,
                "cancellation_payload_hash": canonical_sha256(cancellation.cancellation_payload),
            },
        )
        if cancellation.async_job_id:
            self.connection.execute(
                text(
                    """
                    UPDATE tool_async_jobs
                    SET status = 'CANCEL_REQUESTED',
                        updated_at = now()
                    WHERE async_job_id = :async_job_id
                      AND status = 'WAITING_CALLBACK'
                    """
                ),
                {"async_job_id": cancellation.async_job_id},
            )

    def record_compensation_definition(self, definition: ToolCompensationDefinitionInput) -> None:
        if definition.source_reconciliation_id is not None:
            row = self.connection.execute(
                text(
                    """
                    SELECT manual_assessment_required
                    FROM tool_effect_reconciliations
                    WHERE reconciliation_id = :reconciliation_id
                      AND tenant_id = :tenant_id
                    """
                ),
                {
                    "reconciliation_id": definition.source_reconciliation_id,
                    "tenant_id": definition.tenant_id,
                },
            ).mappings().first()
            if row is None:
                raise ToolRuntimeConflict("compensation requires existing source reconciliation")
            if not bool(row["manual_assessment_required"]):
                raise ToolRuntimeConflict("compensation requires escalated source reconciliation")
        self.connection.execute(
            text(
                """
                INSERT INTO tool_compensation_definitions (
                    compensation_definition_id, tenant_id, source_effect_receipt_id,
                    source_reconciliation_id, compensation_capability, operation_ref,
                    new_action_proposal_ref, requires_approval, window_deadline_at,
                    residual_impact, policy_ref, definition_payload_hash
                )
                VALUES (
                    :compensation_definition_id, :tenant_id, :source_effect_receipt_id,
                    :source_reconciliation_id, :compensation_capability, :operation_ref,
                    :new_action_proposal_ref, :requires_approval, :window_deadline_at,
                    :residual_impact, :policy_ref, :definition_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "compensation_definition_id": definition.compensation_definition_id,
                "tenant_id": definition.tenant_id,
                "source_effect_receipt_id": definition.source_effect_receipt_id,
                "source_reconciliation_id": definition.source_reconciliation_id,
                "compensation_capability": definition.compensation_capability,
                "operation_ref": definition.operation_ref,
                "new_action_proposal_ref": definition.new_action_proposal_ref,
                "requires_approval": definition.requires_approval,
                "window_deadline_at": definition.window_deadline_at,
                "residual_impact": definition.residual_impact,
                "policy_ref": definition.policy_ref,
                "definition_payload_hash": canonical_sha256(definition.definition_payload),
            },
        )

    def record_compensation_attempt(self, attempt: ToolCompensationAttemptInput) -> None:
        self.connection.execute(
            text(
                """
                INSERT INTO tool_compensation_attempts (
                    compensation_attempt_id, tenant_id, compensation_definition_id,
                    prepared_tool_action_id, attempt_id, execution_receipt_id, status,
                    hidden_rollback, idempotency_scope, idempotency_key,
                    idempotency_generation, audit_requirement_id, attempt_payload_hash
                )
                VALUES (
                    :compensation_attempt_id, :tenant_id, :compensation_definition_id,
                    :prepared_tool_action_id, :attempt_id, :execution_receipt_id, :status,
                    :hidden_rollback, :idempotency_scope, :idempotency_key,
                    :idempotency_generation, :audit_requirement_id, :attempt_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "compensation_attempt_id": attempt.compensation_attempt_id,
                "tenant_id": attempt.tenant_id,
                "compensation_definition_id": attempt.compensation_definition_id,
                "prepared_tool_action_id": attempt.prepared_tool_action_id,
                "attempt_id": attempt.attempt_id,
                "execution_receipt_id": attempt.execution_receipt_id,
                "status": attempt.status,
                "hidden_rollback": attempt.hidden_rollback,
                "idempotency_scope": attempt.idempotency_scope,
                "idempotency_key": attempt.idempotency_key,
                "idempotency_generation": attempt.idempotency_generation,
                "audit_requirement_id": attempt.audit_requirement_id,
                "attempt_payload_hash": canonical_sha256(attempt.attempt_payload),
            },
        )

    def record_manual_effect_assessment(self, assessment: ToolManualEffectAssessmentInput) -> None:
        if not assessment.assessor_principal_id.startswith("workspace-user:manual-reviewer"):
            raise ToolRuntimeConflict("manual effect assessment requires authorized manual reviewer")
        row = self.connection.execute(
            text(
                """
                SELECT manual_assessment_required
                FROM tool_effect_reconciliations
                WHERE reconciliation_id = :reconciliation_id
                  AND tenant_id = :tenant_id
                """
            ),
            {
                "reconciliation_id": assessment.reconciliation_id,
                "tenant_id": assessment.tenant_id,
            },
        ).mappings().first()
        if row is None:
            raise ToolRuntimeConflict("manual effect assessment requires existing reconciliation")
        if not bool(row["manual_assessment_required"]):
            raise ToolRuntimeConflict("manual effect assessment requires escalated reconciliation")
        self.connection.execute(
            text(
                """
                INSERT INTO tool_manual_effect_assessments (
                    manual_assessment_id, tenant_id, reconciliation_id, provider_effect_id,
                    conclusion, confidence, assessor_principal_id, residual_uncertainty,
                    evidence_payload_hash
                )
                VALUES (
                    :manual_assessment_id, :tenant_id, :reconciliation_id, :provider_effect_id,
                    :conclusion, :confidence, :assessor_principal_id, :residual_uncertainty,
                    :evidence_payload_hash
                )
                ON CONFLICT DO NOTHING
                """
            ),
            {
                "manual_assessment_id": assessment.manual_assessment_id,
                "tenant_id": assessment.tenant_id,
                "reconciliation_id": assessment.reconciliation_id,
                "provider_effect_id": assessment.provider_effect_id,
                "conclusion": assessment.conclusion,
                "confidence": assessment.confidence,
                "assessor_principal_id": assessment.assessor_principal_id,
                "residual_uncertainty": assessment.residual_uncertainty,
                "evidence_payload_hash": canonical_sha256(assessment.evidence_payload),
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
    "ToolCancellationReceiptInput",
    "ToolManualEffectAssessmentInput",
    "ToolCompensationAttemptInput",
    "ToolCompensationDefinitionInput",
    "ToolAsyncCallbackInput",
    "ToolAsyncJobInput",
    "ToolAttemptInput",
    "ToolEffectReceiptInput",
    "ToolEffectReconciliationInput",
    "ToolExecutionReceiptInput",
    "ToolObservationInput",
    "ToolRepository",
    "ToolRuntimeConflict",
    "ToolUnitOfWork",
    "ToolVersionInput",
]
