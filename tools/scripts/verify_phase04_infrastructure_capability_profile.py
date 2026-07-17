from __future__ import annotations

from pydantic import ValidationError

from zuno.platform.contracts import (
    DataServiceCapabilityV1,
    InfrastructureCapabilityProfileV1,
    canonical_sha256,
)


def _capability(
    *,
    service_kind: str,
    adapter_name: str,
    authoritative: bool,
    rebuildable: bool,
    semantics: tuple[str, ...],
    unsupported: tuple[str, ...] = (),
) -> DataServiceCapabilityV1:
    return DataServiceCapabilityV1(
        service_kind=service_kind,
        adapter_name=adapter_name,
        adapter_version="phase04.v1",
        deployment_profile="phase04-local-real-services",
        authoritative=authoritative,
        rebuildable=rebuildable,
        consistency_model="transactional" if authoritative else "rebuildable",
        tenant_isolation_mode="tenant-scoped-physical-boundary",
        backup_restore_class=(
            "authoritative" if authoritative else "rebuild-from-source"
        ),
        schema_or_contract_version="phase04.contract.v1",
        config_hash=canonical_sha256(
            {
                "service_kind": service_kind,
                "adapter_name": adapter_name,
                "adapter_version": "phase04.v1",
            }
        ),
        supported_semantics=semantics,
        unsupported_semantics=unsupported,
    )


def _profile(
    *, deployment_class: str, profile_version: str
) -> InfrastructureCapabilityProfileV1:
    payload = {
        "profile_id": f"zuno-{deployment_class.lower().replace('_', '-')}-infra-profile",
        "profile_version": profile_version,
        "deployment_class": deployment_class,
        "database": _capability(
            service_kind="RELATIONAL",
            adapter_name="postgresql",
            authoritative=True,
            rebuildable=False,
            semantics=("uow", "transaction", "tenant_context", "alembic"),
        ),
        "object_store": _capability(
            service_kind="OBJECT",
            adapter_name="minio-s3",
            authoritative=False,
            rebuildable=True,
            semantics=("stage", "commit", "manifest", "restore"),
        ),
        "checkpoint_store": _capability(
            service_kind="CHECKPOINT",
            adapter_name="official-langgraph-postgres-checkpointer",
            authoritative=False,
            rebuildable=False,
            semantics=("thread_isolation", "resume"),
            unsupported=("official_adapter_not_yet_installed",),
        ),
        "queue": _capability(
            service_kind="QUEUE",
            adapter_name="rabbitmq",
            authoritative=False,
            rebuildable=False,
            semantics=("publisher_confirm", "ack_nack", "dlq", "redelivery"),
        ),
        "vector_index": _capability(
            service_kind="VECTOR",
            adapter_name="milvus-target",
            authoritative=False,
            rebuildable=True,
            semantics=("versioned_index",),
            unsupported=("server_adapter_not_current",),
        ),
        "graph_index": _capability(
            service_kind="GRAPH",
            adapter_name="neo4j-target",
            authoritative=False,
            rebuildable=True,
            semantics=("versioned_graph",),
            unsupported=("server_adapter_not_current",),
        ),
        "lexical_index": _capability(
            service_kind="LEXICAL",
            adapter_name="bm25-target",
            authoritative=False,
            rebuildable=True,
            semantics=("versioned_lexical_index",),
            unsupported=("server_adapter_not_current",),
        ),
        "cache": _capability(
            service_kind="CACHE",
            adapter_name="redis-optional-cache",
            authoritative=False,
            rebuildable=True,
            semantics=("optional_acceleration",),
            unsupported=("not_authoritative",),
        ),
        "secret_delivery": _capability(
            service_kind="SECRET_KMS",
            adapter_name="phase05-secret-delivery-target",
            authoritative=False,
            rebuildable=False,
            semantics=("secret_ref",),
            unsupported=("secret_rotation_not_current",),
        ),
        "telemetry": _capability(
            service_kind="TRACE_AUDIT",
            adapter_name="phase04-operator-telemetry",
            authoritative=False,
            rebuildable=False,
            semantics=("health", "readiness", "failure_owner", "evidence_ref"),
        ),
        "limits": {
            "pool_size": 2,
            "max_overflow": 1,
            "statement_timeout_ms": 5000,
            "profile_fixed_at_startup": True,
        },
    }
    return InfrastructureCapabilityProfileV1(
        **payload,
        content_hash=canonical_sha256(payload),
    )


def verify_phase04_infrastructure_capability_profile() -> list[str]:
    errors: list[str] = []

    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    developer = _profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")

    if server.content_hash != canonical_sha256(server.hash_inputs()):
        errors.append("server profile content hash is not canonical")
    if developer.content_hash != canonical_sha256(developer.hash_inputs()):
        errors.append("developer profile content hash is not canonical")
    if server.content_hash == developer.content_hash:
        errors.append("deployment_class must participate in the profile hash")
    if (
        type(server).model_fields["database"].annotation
        != type(developer).model_fields["database"].annotation
    ):
        errors.append("developer and server profiles do not share the typed port")

    try:
        server.profile_version = "phase04.mutated"  # type: ignore[misc]
        errors.append("profile mutation was not rejected")
    except (TypeError, ValidationError):
        pass

    mutated_payload = server.hash_inputs()
    mutated_payload["profile_version"] = "phase04.2"
    if canonical_sha256(mutated_payload) == server.content_hash:
        errors.append("profile version change did not change the content hash")

    try:
        InfrastructureCapabilityProfileV1(**server.hash_inputs(), content_hash="bad")
        errors.append("profile accepted an invalid content_hash")
    except ValidationError:
        pass

    for capability_name in [
        "database",
        "object_store",
        "checkpoint_store",
        "queue",
        "vector_index",
        "graph_index",
        "lexical_index",
        "cache",
        "secret_delivery",
        "telemetry",
    ]:
        capability = getattr(server, capability_name)
        if capability is None:
            errors.append(f"{capability_name} capability is missing")
            continue
        if not capability.schema_or_contract_version:
            errors.append(f"{capability_name} schema_or_contract_version is missing")
        if not capability.config_hash:
            errors.append(f"{capability_name} config_hash is missing")
        if (
            capability.service_kind in {"VECTOR", "GRAPH", "LEXICAL", "CACHE"}
            and capability.authoritative
        ):
            errors.append(f"{capability_name} incorrectly claims authoritative status")

    return errors


def main() -> int:
    errors = verify_phase04_infrastructure_capability_profile()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 infrastructure capability profile verification failed.")
        return 1
    print("PHASE04 infrastructure capability profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
