from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from zuno.platform.contracts import (
    DataServiceCapabilityV1,
    InfrastructureCapabilityProfileV1,
    TenantIsolationProfileV1,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
TENANT_PROFILE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_tenant_isolation_profiles.py"
)

PROVEN_PHYSICAL_SCOPES = {
    "RELATIONAL": {
        "capability_field": "database",
        "source_refs": {
            "src/backend/zuno/platform/database/foundation.py": [
                "SELECT set_config('app.tenant_id', :tenant_id, true)",
                "ON CONFLICT (tenant_id, scope, idempotency_key) DO NOTHING",
                "WHERE tenant_id = :tenant_id AND scope = :scope AND idempotency_key = :key",
                "ON CONFLICT (tenant_id, ordering_key) DO UPDATE",
                "WHERE tenant_id = :tenant_id",
            ],
            "infra/db/alembic/versions/20260716_05_idempotency_tenant_isolation.py": [
                "uq_infra_idempotency_claims_tenant_scope_key",
                '["tenant_id", "scope", "idempotency_key"]',
            ],
            "infra/db/alembic/versions/20260717_06_delivery_ordering.py": [
                "pk_infra_outbox_sequences",
                "uq_infra_inbox_messages_tenant_consumer_ordering_sequence",
                "pk_infra_delivery_watermarks",
            ],
        },
        "evidence_refs": {
            "docs/evidence/phase04-postgres-session-runtime.md": [
                "tenant_concurrency_isolation: passed",
                "tenant_context_no_leak: passed",
            ],
            "docs/evidence/phase04-idempotency-claim.md": [
                "tenant_isolation: passed",
                "transaction-local tenant",
                "不同 tenant 可以安全复用 scope/key",
            ],
        },
    },
    "QUEUE": {
        "capability_field": "queue",
        "source_refs": {
            "src/backend/zuno/platform/queue/rabbitmq.py": [
                "tenant_id: str",
                '"tenant_id": tenant_id',
                "headers = dict(delivery.headers)",
                'headers["replayed_from_dlq"] = True',
            ],
            "tests/integration/test_phase04_rabbitmq_transport.py": [
                'assert first.headers["tenant_id"] == "tenant-a"',
                'assert replayed.headers["trace_id"] == "trace-dlq-replay"',
            ],
            "tests/integration/test_phase04_outbox_rabbitmq_publisher.py": [
                'assert delivery.headers["tenant_id"] == "tenant-phase04"',
            ],
        },
        "evidence_refs": {
            "docs/evidence/phase04-rabbitmq-transport.md": [
                "Preserves `tenant_id`, `trace_id` and `message_version` headers.",
                "preserving tenant context",
            ],
            "docs/evidence/phase04-outbox-rabbitmq-publisher.md": [
                "rabbitmq_publish_confirm: passed",
                "tenant header",
            ],
        },
    },
    "OBJECT": {
        "capability_field": "object_store",
        "source_refs": {
            "src/backend/zuno/platform/contracts/shared.py": [
                "class SourceObjectRefV1",
                "tenant_id: str",
                "object_uri: str",
            ],
            "src/backend/zuno/platform/storage/object_store.py": [
                "authorization_hook",
                "ObjectAuthorizationError",
                'Filter(prefix="_staging/")',
            ],
            "tests/integration/test_phase04_minio_object_store.py": [
                "authorization_hook=lambda action, _bucket, _object_name",
                "with pytest.raises(ObjectAuthorizationError)",
            ],
        },
        "evidence_refs": {
            "docs/evidence/phase04-minio-object-store.md": [
                "Creates an isolated real MinIO bucket for each run.",
                "authorization_hook: passed_fail_closed",
                "Infrastructure authorization hook 的 fail-closed 执行边界",
            ],
        },
    },
    "TRACE_AUDIT": {
        "capability_field": "telemetry",
        "source_refs": {
            "tools/scripts/verify_phase04_operator_readiness.py": [
                '"tenant_id"',
                '"trace_id"',
                '"failure_owner"',
                '"recovery_owner"',
            ],
        },
        "evidence_refs": {
            "docs/evidence/phase04-operator-readiness.md": [
                "Operator snapshot 包含",
                "`tenant_id`",
                "failure owner",
            ],
        },
    },
}


def _load_module(path: Path, module_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {module_name}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _profile(
    *, deployment_class: str, profile_version: str
) -> InfrastructureCapabilityProfileV1:
    module = _load_module(
        CAPABILITY_PROFILE_VERIFIER,
        "verify_phase04_infrastructure_capability_profile",
    )
    return module._profile(
        deployment_class=deployment_class,
        profile_version=profile_version,
    )


def _tenant_profile(service_kind: str) -> TenantIsolationProfileV1:
    module = _load_module(
        TENANT_PROFILE_VERIFIER,
        "verify_phase04_tenant_isolation_profiles",
    )
    return module._tenant_profile(service_kind)


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _require_phrases(
    errors: list[str], *, label: str, refs: dict[str, list[str]]
) -> None:
    for ref, phrases in refs.items():
        path = REPO_ROOT / ref
        if not path.exists():
            errors.append(f"{label} missing ref: {ref}")
            continue
        text = _read(ref)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label} ref {ref} missing phrase: {phrase}")


def _capability(
    profile: InfrastructureCapabilityProfileV1, service_kind: str
) -> DataServiceCapabilityV1:
    field_name = PROVEN_PHYSICAL_SCOPES[service_kind]["capability_field"]
    capability = getattr(profile, field_name)
    if capability is None:
        raise RuntimeError(f"{field_name} capability is missing")
    return capability


def verify_phase04_tenant_physical_constraints() -> list[str]:
    errors: list[str] = []

    capability_module = _load_module(
        CAPABILITY_PROFILE_VERIFIER,
        "verify_phase04_infrastructure_capability_profile",
    )
    for error in capability_module.verify_phase04_infrastructure_capability_profile():
        errors.append(f"capability profile failed: {error}")

    tenant_module = _load_module(
        TENANT_PROFILE_VERIFIER,
        "verify_phase04_tenant_isolation_profiles",
    )
    for error in tenant_module.verify_phase04_tenant_isolation_profiles():
        errors.append(f"tenant isolation profile failed: {error}")

    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    for service_kind, spec in PROVEN_PHYSICAL_SCOPES.items():
        capability = _capability(server, service_kind)
        tenant_profile = _tenant_profile(service_kind)

        if capability.service_kind != service_kind:
            errors.append(f"{service_kind} capability service_kind mismatch")
        if capability.tenant_isolation_mode != "tenant-scoped-physical-boundary":
            errors.append(
                f"{service_kind} capability does not declare a physical tenant boundary"
            )
        if tenant_profile.current_runtime_status != "PROVEN":
            errors.append(f"{service_kind} tenant physical scope is not proven")
        if "tenant_id" not in tenant_profile.scope_fields:
            errors.append(f"{service_kind} tenant_id is missing from scope fields")
        if tenant_profile.application_end_filter_only_allowed:
            errors.append(f"{service_kind} allows application-only tenant filtering")
        if not tenant_profile.mandatory_filter_required:
            errors.append(f"{service_kind} does not require mandatory tenant filtering")
        if tenant_profile.strong_isolation_option.lower() in {"", "none", "n/a"}:
            errors.append(f"{service_kind} lacks a strong isolation option")

        _require_phrases(
            errors,
            label=f"{service_kind} source",
            refs=spec["source_refs"],
        )
        _require_phrases(
            errors,
            label=f"{service_kind} evidence",
            refs=spec["evidence_refs"],
        )

    for service_kind in {
        "CHECKPOINT",
        "VECTOR",
        "GRAPH",
        "LEXICAL",
        "CACHE",
        "SECRET_KMS",
    }:
        tenant_profile = _tenant_profile(service_kind)
        if tenant_profile.current_runtime_status == "PROVEN":
            errors.append(f"{service_kind} was incorrectly promoted to proven")

    return errors


def main() -> int:
    errors = verify_phase04_tenant_physical_constraints()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 tenant physical constraints verification failed.")
        return 1
    print("PHASE04 tenant physical constraints verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
