from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pydantic import ValidationError

from zuno.platform.contracts import (
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

SERVICE_PROFILES = {
    "RELATIONAL": {
        "isolation_mode": "Tenant/Workspace Scope; high-security RLS compatible",
        "strong_isolation_option": "Schema/Database per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "FAIL_CLOSED",
        "evidence_ref": "docs/evidence/phase04-postgres-session-runtime.md",
        "current_runtime_status": "PROVEN",
    },
    "QUEUE": {
        "isolation_mode": "Scoped Envelope, Routing, Queue",
        "strong_isolation_option": "VHost per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "FAIL_CLOSED",
        "evidence_ref": "docs/evidence/phase04-rabbitmq-transport.md",
        "current_runtime_status": "PROVEN",
    },
    "OBJECT": {
        "isolation_mode": "Prefix + Bucket Policy + Encryption Context",
        "strong_isolation_option": "Bucket/Account per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "QUARANTINE",
        "evidence_ref": "docs/evidence/phase04-minio-object-store.md",
        "current_runtime_status": "PROVEN",
    },
    "CHECKPOINT": {
        "isolation_mode": "Thread/Namespace + Tenant Binding",
        "strong_isolation_option": "Schema/Database per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "FAIL_CLOSED",
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "BLOCKED",
    },
    "VECTOR": {
        "isolation_mode": "Database/Collection/Partition + Mandatory Filter",
        "strong_isolation_option": "Dedicated Database/Deployment",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "QUARANTINE",
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "GRAPH": {
        "isolation_mode": "Database or Tenant Property/Label Scope",
        "strong_isolation_option": "Dedicated Database/Deployment",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "QUARANTINE",
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "LEXICAL": {
        "isolation_mode": "Index/Alias or Mandatory Filter",
        "strong_isolation_option": "Dedicated Index/Deployment",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "QUARANTINE",
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "CACHE": {
        "isolation_mode": "Tenant Namespace + ACL",
        "strong_isolation_option": "Dedicated Instance",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "FAIL_CLOSED",
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "SECRET_KMS": {
        "isolation_mode": "Tenant SecretRef + Scope Boundary",
        "strong_isolation_option": "Dedicated KMS Key/Account per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "FAIL_CLOSED",
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "TRACE_AUDIT": {
        "isolation_mode": "Tenant/Workspace Trace Scope",
        "strong_isolation_option": "Dedicated Audit Sink per Tenant",
        "mandatory_filter_required": True,
        "cross_tenant_hit_action": "MANDATORY_AUDIT",
        "evidence_ref": "docs/evidence/phase04-operator-readiness.md",
        "current_runtime_status": "PROVEN",
    },
}


def _profile(
    *, deployment_class: str, profile_version: str
) -> InfrastructureCapabilityProfileV1:
    spec = spec_from_file_location(
        "verify_phase04_infrastructure_capability_profile",
        CAPABILITY_PROFILE_VERIFIER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load infrastructure capability profile verifier")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module._profile(
        deployment_class=deployment_class,
        profile_version=profile_version,
    )


def _service_kinds(profile: InfrastructureCapabilityProfileV1) -> set[str]:
    kinds: set[str] = set()
    for field_name in [
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
        capability = getattr(profile, field_name)
        if capability is not None:
            kinds.add(capability.service_kind)
    return kinds


def _tenant_profile(service_kind: str) -> TenantIsolationProfileV1:
    spec = SERVICE_PROFILES[service_kind]
    return TenantIsolationProfileV1(
        profile_id=f"phase04-tenant-isolation-{service_kind.lower()}",
        service_kind=service_kind,  # type: ignore[arg-type]
        scope_fields=("tenant_id", "workspace_id"),
        application_end_filter_only_allowed=False,
        **spec,
    )


def verify_phase04_tenant_isolation_profiles() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    required_kinds = _service_kinds(server)

    missing = sorted(required_kinds - SERVICE_PROFILES.keys())
    if missing:
        errors.append(f"missing tenant isolation profile(s): {missing!r}")

    for service_kind in sorted(required_kinds):
        try:
            profile = _tenant_profile(service_kind)
        except ValidationError as exc:
            errors.append(
                f"{service_kind} tenant isolation profile failed validation: {exc}"
            )
            continue
        if "tenant_id" not in profile.scope_fields:
            errors.append(f"{service_kind} profile does not include tenant_id scope")
        if profile.application_end_filter_only_allowed:
            errors.append(f"{service_kind} allows application-only tenant filtering")
        if profile.cross_tenant_hit_action not in {
            "QUARANTINE",
            "FAIL_CLOSED",
            "MANDATORY_AUDIT",
        }:
            errors.append(f"{service_kind} has unsafe cross-tenant hit action")
        if not (REPO_ROOT / profile.evidence_ref).exists():
            errors.append(f"{service_kind} evidence_ref does not exist")

    try:
        TenantIsolationProfileV1(
            profile_id="bad-profile",
            service_kind="RELATIONAL",
            isolation_mode="application filter only",
            scope_fields=("workspace_id",),
            strong_isolation_option="none",
            mandatory_filter_required=True,
            application_end_filter_only_allowed=True,
            cross_tenant_hit_action="FAIL_CLOSED",
            evidence_ref="docs/evidence/phase04-postgres-session-runtime.md",
            current_runtime_status="PROFILE_ONLY",
        )
        errors.append("invalid tenant isolation profile was accepted")
    except ValidationError:
        pass

    return errors


def main() -> int:
    errors = verify_phase04_tenant_isolation_profiles()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 tenant isolation profile verification failed.")
        return 1
    print("PHASE04 tenant isolation profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
