from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine

from zuno.domain import (
    AllowAllMutationAuthorizer,
    CanonicalDomainMutationService,
    DomainMutationCommand,
    MutationResultStatus,
    SqlAlchemyCanonicalDomainStore,
)


def _command(mutation_id: str, *, expected: int = 0, key: str | None = None) -> DomainMutationCommand:
    return DomainMutationCommand(
        mutation_id=mutation_id,
        matter_id="matter-sql",
        tenant_id="tenant-sql",
        scope_ref="matter:matter-sql",
        expected_domain_version=expected,
        proposal={"object_type": "Fact", "value": mutation_id},
        mutation_type="FACT_PROPOSAL",
        principal_ref="principal:test",
        idempotency_key=key or f"idem:{mutation_id}",
        correlation_id=f"trace:{mutation_id}",
        security_context_ref="security:test",
    )


def test_sqlalchemy_store_exercises_transactional_version_and_replay_semantics() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    store = SqlAlchemyCanonicalDomainStore(engine)
    store.create_schema_for_test()
    service = CanonicalDomainMutationService(store, authorizer=AllowAllMutationAuthorizer())

    committed = service.submit(_command("sql-1"))
    conflict = service.submit(_command("sql-2", expected=0))
    replay = service.submit(
        _command("retry", key="idem:sql-1")
        .model_copy(update={"proposal": {"object_type": "Fact", "value": "sql-1"}})
    )

    assert committed.status is MutationResultStatus.COMMITTED
    assert conflict.status is MutationResultStatus.VERSION_CONFLICT
    assert replay.status is MutationResultStatus.ALREADY_APPLIED
    assert replay.result_ref == committed.result_ref


def test_sqlalchemy_store_rolls_back_domain_version_when_commit_hook_fails() -> None:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    store = SqlAlchemyCanonicalDomainStore(engine)
    store.create_schema_for_test()
    service = CanonicalDomainMutationService(store, authorizer=AllowAllMutationAuthorizer())
    command = _command("sql-fault")

    with pytest.raises(RuntimeError, match="sql-commit-before-fault"):
        service.submit(
            command,
            before_commit=lambda: (_ for _ in ()).throw(RuntimeError("sql-commit-before-fault")),
        )

    recovered = service.submit(command)
    assert recovered.status is MutationResultStatus.COMMITTED
    assert recovered.domain_version_before == 0
    assert recovered.domain_version_after == 1


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PostgreSQL integration is BLOCKED",
)
def test_postgresql_store_transaction_contract() -> None:
    engine = create_engine(os.environ["ZUNO_TEST_DATABASE_URL"])
    store = SqlAlchemyCanonicalDomainStore(engine)
    store.create_schema_for_test()
    service = CanonicalDomainMutationService(store, authorizer=AllowAllMutationAuthorizer())

    committed = service.submit(_command("postgres-1"))
    replay = service.submit(_command("retry", key="idem:postgres-1"))

    assert committed.status is MutationResultStatus.COMMITTED
    assert replay.status is MutationResultStatus.ALREADY_APPLIED
