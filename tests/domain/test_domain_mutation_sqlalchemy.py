from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import create_engine

from zuno.domain import (
    AllowAllMutationAuthorizer,
    CanonicalDomainMutationService,
    DomainMutationCommand,
    MutationResultStatus,
    SqlAlchemyCanonicalDomainStore,
)


def _command(
    mutation_id: str,
    *,
    expected: int = 0,
    key: str | None = None,
    matter_id: str = "matter-sql",
) -> DomainMutationCommand:
    return DomainMutationCommand(
        mutation_id=mutation_id,
        matter_id=matter_id,
        tenant_id="tenant-sql",
        scope_ref=f"matter:{matter_id}",
        expected_domain_version=expected,
        proposal={"object_type": "Fact", "value": mutation_id},
        mutation_type="FACT_PROPOSAL",
        principal_ref="principal:test",
        idempotency_key=key or f"idem:{mutation_id}",
        correlation_id=f"trace:{mutation_id}",
        security_context_ref="security:test",
    )


def _postgres_service() -> CanonicalDomainMutationService:
    engine = create_engine(os.environ["ZUNO_TEST_DATABASE_URL"])
    store = SqlAlchemyCanonicalDomainStore(engine)
    store.create_schema_for_test()
    return CanonicalDomainMutationService(store, authorizer=AllowAllMutationAuthorizer())


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
    service = _postgres_service()
    matter_id = "matter-pg-replay"
    command = _command("postgres-1", matter_id=matter_id)

    committed = service.submit(command)

    # Model the caller losing the successful response: recovery constructs a new
    # service instance and only has the stable idempotency identity + same input.
    recovered_service = _postgres_service()
    replay = recovered_service.submit(
        _command("postgres-retry", key=command.idempotency_key, matter_id=matter_id).model_copy(
            update={"proposal": command.proposal}
        )
    )

    assert committed.status is MutationResultStatus.COMMITTED
    assert committed.domain_version_before == 0
    assert committed.domain_version_after == 1
    assert replay.status is MutationResultStatus.ALREADY_APPLIED
    assert replay.result_ref == committed.result_ref
    assert replay.domain_version_after == 1


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PostgreSQL integration is BLOCKED",
)
def test_postgresql_two_admissions_based_on_d0_only_one_commits_d1() -> None:
    service = _postgres_service()
    matter_id = "matter-pg-concurrent-d0"
    gate = Barrier(2)
    commands = (
        _command("postgres-concurrent-a", matter_id=matter_id),
        _command("postgres-concurrent-b", matter_id=matter_id),
    )

    def submit(command: DomainMutationCommand):
        gate.wait(timeout=5)
        return service.submit(command)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(submit, commands))

    committed = [result for result in results if result.status is MutationResultStatus.COMMITTED]
    conflicts = [result for result in results if result.status is MutationResultStatus.VERSION_CONFLICT]

    assert len(committed) == 1
    assert len(conflicts) == 1
    assert committed[0].domain_version_before == 0
    assert committed[0].domain_version_after == 1
    assert conflicts[0].domain_version_before == 1
    assert conflicts[0].domain_version_after == 1


@pytest.mark.skipif(
    not os.environ.get("ZUNO_TEST_DATABASE_URL"),
    reason="ZUNO_TEST_DATABASE_URL is not configured; PostgreSQL integration is BLOCKED",
)
def test_postgresql_before_commit_failure_rolls_back_then_retries_from_d0() -> None:
    service = _postgres_service()
    command = _command("postgres-before-commit-fault", matter_id="matter-pg-before-commit-fault")

    with pytest.raises(RuntimeError, match="postgres-before-commit-fault"):
        service.submit(
            command,
            before_commit=lambda: (_ for _ in ()).throw(RuntimeError("postgres-before-commit-fault")),
        )

    recovered_service = _postgres_service()
    recovered = recovered_service.submit(command)

    assert recovered.status is MutationResultStatus.COMMITTED
    assert recovered.domain_version_before == 0
    assert recovered.domain_version_after == 1
