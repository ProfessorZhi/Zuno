from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from threading import RLock
from typing import Any

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    insert,
    select,
    text,
    update,
)
from sqlalchemy.engine import Connection, Engine

from zuno.domain.mutation import (
    DomainMutationCommand,
    DomainMutationResult,
    MutationResultStatus,
)


DOMAIN_METADATA = MetaData()

DOMAIN_AGGREGATE_HEADS = Table(
    "domain_aggregate_heads",
    DOMAIN_METADATA,
    Column("tenant_id", String(180), primary_key=True),
    Column("matter_id", String(220), primary_key=True),
    Column("scope_ref", String(240), nullable=False),
    Column("domain_version", BigInteger, nullable=False, default=0),
    Column("last_mutation_id", String(220), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

DOMAIN_MUTATION_RECORDS = Table(
    "domain_mutation_records",
    DOMAIN_METADATA,
    Column("mutation_id", String(220), primary_key=True),
    Column("tenant_id", String(180), nullable=False),
    Column("matter_id", String(220), nullable=False),
    Column("scope_ref", String(240), nullable=False),
    Column("idempotency_key", String(240), nullable=False),
    Column("request_hash", String(64), nullable=False),
    Column("expected_domain_version", BigInteger, nullable=False),
    Column("mutation_type", String(160), nullable=False),
    Column("proposal_json", JSON, nullable=False),
    Column("proposal_reference", String(512), nullable=True),
    Column("principal_ref", String(220), nullable=False),
    Column("correlation_id", String(240), nullable=False),
    Column("causation_ref", String(512), nullable=True),
    Column("security_context_ref", String(512), nullable=False),
    Column("status", String(40), nullable=False),
    Column("reason_code", String(160), nullable=False),
    Column("domain_version_before", BigInteger, nullable=False),
    Column("domain_version_after", BigInteger, nullable=False),
    Column("committed_version_ref", String(300), nullable=True),
    Column("result_ref", String(300), nullable=False),
    Column("trace_ref", String(300), nullable=False),
    Column("audit_ref", String(300), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("tenant_id", "matter_id", "idempotency_key", name="uq_domain_mutation_idempotency"),
)

DOMAIN_STATE_VERSIONS = Table(
    "domain_state_versions",
    DOMAIN_METADATA,
    Column("version_id", String(300), primary_key=True),
    Column("tenant_id", String(180), nullable=False),
    Column("matter_id", String(220), nullable=False),
    Column("scope_ref", String(240), nullable=False),
    Column("domain_version", BigInteger, nullable=False),
    Column("mutation_id", String(220), nullable=False),
    Column("mutation_type", String(160), nullable=False),
    Column("proposal_json", JSON, nullable=False),
    Column("provenance_json", JSON, nullable=False),
    Column("principal_ref", String(220), nullable=False),
    Column("correlation_id", String(240), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("tenant_id", "matter_id", "domain_version", name="uq_domain_state_version"),
)


def create_domain_schema(engine: Engine) -> None:
    """Test/developer helper; production schema is owned by Alembic."""

    DOMAIN_METADATA.create_all(engine)


class InMemoryCanonicalDomainStore:
    """Deterministic unit-test store with the same CAS/idempotency semantics."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._heads: dict[tuple[str, str], int] = {}
        self._records: dict[tuple[str, str, str], tuple[str, DomainMutationResult]] = {}
        self._versions: list[DomainMutationResult] = []

    def commit_mutation(
        self,
        command: DomainMutationCommand,
        *,
        request_hash: str,
        before_commit: Callable[[], None] | None = None,
    ) -> DomainMutationResult:
        with self._lock:
            key = (command.tenant_id, command.matter_id, command.idempotency_key)
            existing = self._records.get(key)
            if existing is not None:
                known_hash, previous = existing
                if known_hash != request_hash:
                    return _result(
                        command,
                        status=MutationResultStatus.REJECTED,
                        reason_code="idempotency_key_reused_with_different_input",
                        before=previous.domain_version_before,
                        after=previous.domain_version_after,
                        replayed=True,
                    )
                replay_status = (
                    MutationResultStatus.ALREADY_APPLIED
                    if previous.status is MutationResultStatus.COMMITTED
                    else previous.status
                )
                return previous.model_copy(update={"status": replay_status, "replayed": True})

            current = self._heads.get((command.tenant_id, command.matter_id), 0)
            if command.expected_domain_version != current:
                result = _result(
                    command,
                    status=MutationResultStatus.VERSION_CONFLICT,
                    reason_code="expected_domain_version_mismatch",
                    before=current,
                    after=current,
                )
                self._records[key] = (request_hash, result)
                return result

            if command.proposal.get("requires_review") is True:
                result = _result(
                    command,
                    status=MutationResultStatus.REVIEW_REQUIRED,
                    reason_code="proposal_requires_review",
                    before=current,
                    after=current,
                )
                self._records[key] = (request_hash, result)
                return result

            next_version = current + 1
            result = _result(
                command,
                status=MutationResultStatus.COMMITTED,
                reason_code="canonical_domain_version_committed",
                before=current,
                after=next_version,
            )
            if before_commit is not None:
                before_commit()
            self._heads[(command.tenant_id, command.matter_id)] = next_version
            self._records[key] = (request_hash, result)
            self._versions.append(result)
            return result

    def current_version(self, *, tenant_id: str, matter_id: str) -> int:
        with self._lock:
            return self._heads.get((tenant_id, matter_id), 0)

    def committed_versions(self) -> tuple[DomainMutationResult, ...]:
        with self._lock:
            return tuple(self._versions)


class SqlAlchemyCanonicalDomainStore:
    """PostgreSQL-backed Domain Owner persistence adapter.

    The caller must run the Alembic migration first.  ``create_domain_schema``
    exists only for focused SQLite/integration tests and local contract probes.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def create_schema_for_test(self) -> None:
        create_domain_schema(self.engine)

    def commit_mutation(
        self,
        command: DomainMutationCommand,
        *,
        request_hash: str,
        before_commit: Callable[[], None] | None = None,
    ) -> DomainMutationResult:
        with self.engine.begin() as connection:
            if connection.dialect.name == "postgresql":
                connection.execute(
                    text("SELECT set_config('app.tenant_id', :tenant_id, true)"),
                    {"tenant_id": command.tenant_id},
                )
            return self._commit_on_connection(
                connection,
                command,
                request_hash=request_hash,
                before_commit=before_commit,
            )

    def _commit_on_connection(
        self,
        connection: Connection,
        command: DomainMutationCommand,
        *,
        request_hash: str,
        before_commit: Callable[[], None] | None,
    ) -> DomainMutationResult:
        now = datetime.now(UTC)
        self._ensure_head(connection, command, now=now)
        existing = connection.execute(
            select(DOMAIN_MUTATION_RECORDS).where(
                DOMAIN_MUTATION_RECORDS.c.tenant_id == command.tenant_id,
                DOMAIN_MUTATION_RECORDS.c.matter_id == command.matter_id,
                DOMAIN_MUTATION_RECORDS.c.idempotency_key == command.idempotency_key,
            )
        ).mappings().first()
        if existing is not None:
            if str(existing["request_hash"]) != request_hash:
                return _row_result(
                    existing,
                    status=MutationResultStatus.REJECTED,
                    reason_code="idempotency_key_reused_with_different_input",
                    replayed=True,
                )
            replay_status = (
                MutationResultStatus.ALREADY_APPLIED
                if str(existing["status"]) == MutationResultStatus.COMMITTED.value
                else MutationResultStatus(str(existing["status"]))
            )
            return _row_result(
                existing,
                status=replay_status,
                reason_code=str(existing["reason_code"]),
                replayed=True,
            )

        head_query = select(DOMAIN_AGGREGATE_HEADS).where(
            DOMAIN_AGGREGATE_HEADS.c.tenant_id == command.tenant_id,
            DOMAIN_AGGREGATE_HEADS.c.matter_id == command.matter_id,
        )
        if connection.dialect.name == "postgresql":
            head_query = head_query.with_for_update()
        head = connection.execute(head_query).mappings().one()
        current = int(head["domain_version"])
        if command.expected_domain_version != current:
            result = _result(
                command,
                status=MutationResultStatus.VERSION_CONFLICT,
                reason_code="expected_domain_version_mismatch",
                before=current,
                after=current,
            )
            self._insert_record(connection, command, request_hash=request_hash, result=result, now=now)
            return result

        if command.proposal.get("requires_review") is True:
            result = _result(
                command,
                status=MutationResultStatus.REVIEW_REQUIRED,
                reason_code="proposal_requires_review",
                before=current,
                after=current,
            )
            self._insert_record(connection, command, request_hash=request_hash, result=result, now=now)
            return result

        next_version = current + 1
        result = _result(
            command,
            status=MutationResultStatus.COMMITTED,
            reason_code="canonical_domain_version_committed",
            before=current,
            after=next_version,
        )
        connection.execute(
            DOMAIN_STATE_VERSIONS.insert().values(
                version_id=result.committed_version_ref,
                tenant_id=command.tenant_id,
                matter_id=command.matter_id,
                scope_ref=command.scope_ref,
                domain_version=next_version,
                mutation_id=command.mutation_id,
                mutation_type=command.mutation_type,
                proposal_json=command.proposal,
                provenance_json={"proposal_reference": command.proposal_reference},
                principal_ref=command.principal_ref,
                correlation_id=command.correlation_id,
                created_at=now,
            )
        )
        connection.execute(
            update(DOMAIN_AGGREGATE_HEADS)
            .where(
                DOMAIN_AGGREGATE_HEADS.c.tenant_id == command.tenant_id,
                DOMAIN_AGGREGATE_HEADS.c.matter_id == command.matter_id,
                DOMAIN_AGGREGATE_HEADS.c.domain_version == current,
            )
            .values(
                domain_version=next_version,
                last_mutation_id=command.mutation_id,
                updated_at=now,
            )
        )
        self._insert_record(connection, command, request_hash=request_hash, result=result, now=now)
        if before_commit is not None:
            before_commit()
        return result

    @staticmethod
    def _ensure_head(connection: Connection, command: DomainMutationCommand, *, now: datetime) -> None:
        values = {
            "tenant_id": command.tenant_id,
            "matter_id": command.matter_id,
            "scope_ref": command.scope_ref,
            "domain_version": 0,
            "updated_at": now,
        }
        if connection.dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as dialect_insert

            statement = dialect_insert(DOMAIN_AGGREGATE_HEADS).values(**values).on_conflict_do_nothing(
                index_elements=["tenant_id", "matter_id"]
            )
        elif connection.dialect.name == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as dialect_insert

            statement = dialect_insert(DOMAIN_AGGREGATE_HEADS).values(**values).on_conflict_do_nothing(
                index_elements=["tenant_id", "matter_id"]
            )
        else:
            statement = insert(DOMAIN_AGGREGATE_HEADS).values(**values)
        connection.execute(statement)

    @staticmethod
    def _insert_record(
        connection: Connection,
        command: DomainMutationCommand,
        *,
        request_hash: str,
        result: DomainMutationResult,
        now: datetime,
    ) -> None:
        connection.execute(
            DOMAIN_MUTATION_RECORDS.insert().values(
                mutation_id=command.mutation_id,
                tenant_id=command.tenant_id,
                matter_id=command.matter_id,
                scope_ref=command.scope_ref,
                idempotency_key=command.idempotency_key,
                request_hash=request_hash,
                expected_domain_version=command.expected_domain_version,
                mutation_type=command.mutation_type,
                proposal_json=command.proposal,
                proposal_reference=command.proposal_reference,
                principal_ref=command.principal_ref,
                correlation_id=command.correlation_id,
                causation_ref=command.causation_ref,
                security_context_ref=command.security_context_ref,
                status=result.status.value,
                reason_code=result.reason_code,
                domain_version_before=result.domain_version_before,
                domain_version_after=result.domain_version_after,
                committed_version_ref=result.committed_version_ref,
                result_ref=result.result_ref,
                trace_ref=result.trace_ref,
                audit_ref=result.audit_ref,
                created_at=now,
            )
        )


def _result(
    command: DomainMutationCommand,
    *,
    status: MutationResultStatus,
    reason_code: str,
    before: int,
    after: int,
    replayed: bool = False,
) -> DomainMutationResult:
    version_ref = (
        f"domain-version:{command.tenant_id}:{command.matter_id}:{after}"
        if status is MutationResultStatus.COMMITTED
        else None
    )
    return DomainMutationResult(
        mutation_id=command.mutation_id,
        matter_id=command.matter_id,
        tenant_id=command.tenant_id,
        status=status,
        result_ref=f"domain-mutation-result:{command.mutation_id}:{status.value}",
        reason_code=reason_code,
        domain_version_before=before,
        domain_version_after=after,
        committed_version_ref=version_ref,
        trace_ref=f"trace:domain-mutation:{command.correlation_id}",
        audit_ref=f"audit:domain-mutation:{command.mutation_id}",
        replayed=replayed,
    )


def _row_result(
    row: Any,
    *,
    status: MutationResultStatus,
    reason_code: str,
    replayed: bool,
) -> DomainMutationResult:
    return DomainMutationResult(
        mutation_id=str(row["mutation_id"]),
        matter_id=str(row["matter_id"]),
        tenant_id=str(row["tenant_id"]),
        status=status,
        result_ref=str(row["result_ref"]),
        reason_code=reason_code,
        domain_version_before=int(row["domain_version_before"]),
        domain_version_after=int(row["domain_version_after"]),
        committed_version_ref=row["committed_version_ref"],
        trace_ref=str(row["trace_ref"]),
        audit_ref=str(row["audit_ref"]),
        replayed=replayed,
    )


__all__ = [
    "DOMAIN_AGGREGATE_HEADS",
    "DOMAIN_METADATA",
    "DOMAIN_MUTATION_RECORDS",
    "DOMAIN_STATE_VERSIONS",
    "InMemoryCanonicalDomainStore",
    "SqlAlchemyCanonicalDomainStore",
    "create_domain_schema",
]
