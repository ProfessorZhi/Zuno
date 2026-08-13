from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from zuno.domain import (
    AllowAllMutationAuthorizer,
    CanonicalDomainMutationService,
    DomainMutationCommand,
    InMemoryCanonicalDomainStore,
    MutationResultStatus,
)


def _command(
    *,
    mutation_id: str,
    expected: int = 0,
    key: str | None = None,
    proposal: dict | None = None,
) -> DomainMutationCommand:
    return DomainMutationCommand(
        mutation_id=mutation_id,
        matter_id="matter-1",
        tenant_id="tenant-1",
        scope_ref="matter:matter-1",
        expected_domain_version=expected,
        proposal=proposal or {"object_type": "Fact", "value": mutation_id},
        mutation_type="FACT_PROPOSAL",
        principal_ref="principal:reviewer",
        idempotency_key=key or f"idem:{mutation_id}",
        correlation_id=f"trace:{mutation_id}",
        causation_ref="run:1",
        security_context_ref="security:epoch:1",
    )


def _service(store: InMemoryCanonicalDomainStore, audit: list[dict] | None = None):
    return CanonicalDomainMutationService(
        store,
        authorizer=AllowAllMutationAuthorizer(),
        audit_sink=audit.append if audit is not None else None,
    )


def test_expected_version_d10_commits_d11_and_emits_audit() -> None:
    store = InMemoryCanonicalDomainStore()
    audit: list[dict] = []

    result = _service(store, audit).submit(_command(mutation_id="m1"))

    assert result.status is MutationResultStatus.COMMITTED
    assert result.domain_version_before == 0
    assert result.domain_version_after == 1
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 1
    assert audit[0]["mutation_id"] == "m1"
    assert audit[0]["domain_version_after"] == 1


def test_stale_expected_version_is_typed_conflict_without_overwrite() -> None:
    store = InMemoryCanonicalDomainStore()
    service = _service(store)
    service.submit(_command(mutation_id="m1"))

    result = service.submit(_command(mutation_id="m2", expected=0))

    assert result.status is MutationResultStatus.VERSION_CONFLICT
    assert result.reason_code == "expected_domain_version_mismatch"
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 1


def test_same_key_same_input_replays_one_commit_and_different_input_rejects() -> None:
    store = InMemoryCanonicalDomainStore()
    service = _service(store)
    first = service.submit(_command(mutation_id="m1", key="idem:shared"))
    replay = service.submit(
        _command(mutation_id="retry-id", key="idem:shared", proposal={"object_type": "Fact", "value": "m1"})
    )
    conflict = service.submit(
        _command(
            mutation_id="different",
            key="idem:shared",
            proposal={"object_type": "Fact", "value": "different"},
        )
    )

    assert first.status is MutationResultStatus.COMMITTED
    assert replay.status is MutationResultStatus.ALREADY_APPLIED
    assert replay.replayed is True
    assert replay.result_ref == first.result_ref
    assert conflict.status is MutationResultStatus.REJECTED
    assert conflict.reason_code == "idempotency_key_reused_with_different_input"
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 1


def test_fault_before_transaction_commit_does_not_advance_domain_version() -> None:
    store = InMemoryCanonicalDomainStore()
    service = _service(store)

    with pytest.raises(RuntimeError, match="commit-before-fault"):
        service.submit(
            _command(mutation_id="m1"),
            before_commit=lambda: (_ for _ in ()).throw(RuntimeError("commit-before-fault")),
        )

    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 0
    assert store.committed_versions() == ()


def test_retry_after_lost_response_finds_the_committed_result() -> None:
    store = InMemoryCanonicalDomainStore()
    service = _service(store)
    command = _command(mutation_id="m1", key="idem:lost-response")
    committed = service.submit(command)
    recovered = service.submit(command)

    assert committed.status is MutationResultStatus.COMMITTED
    assert recovered.status is MutationResultStatus.ALREADY_APPLIED
    assert recovered.result_ref == committed.result_ref
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 1


def test_two_concurrent_mutations_against_same_version_have_one_commit() -> None:
    store = InMemoryCanonicalDomainStore()
    service = _service(store)

    def submit(number: int):
        return service.submit(_command(mutation_id=f"concurrent-{number}", key=f"idem:{number}"))

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(submit, (1, 2)))

    assert [result.status for result in results].count(MutationResultStatus.COMMITTED) == 1
    assert [result.status for result in results].count(MutationResultStatus.VERSION_CONFLICT) == 1
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 1


def test_missing_authorizer_and_review_gate_cannot_commit() -> None:
    store = InMemoryCanonicalDomainStore()
    missing_auth = CanonicalDomainMutationService(store, authorizer=None)
    denied = missing_auth.submit(_command(mutation_id="auth"))
    review = _service(store).submit(
        _command(mutation_id="review", proposal={"object_type": "Finding", "requires_review": True})
    )

    assert denied.status is MutationResultStatus.AUTHORIZATION_FAILED
    assert review.status is MutationResultStatus.REVIEW_REQUIRED
    assert store.current_version(tenant_id="tenant-1", matter_id="matter-1") == 0
    assert not hasattr(store, "write_fact")
