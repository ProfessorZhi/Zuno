from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pydantic import ValidationError

from zuno.platform.contracts import (
    DataServiceCapabilityV1,
    InfrastructureCapabilityProfileV1,
    UpgradeCompatibilityProfileV1,
    canonical_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)

SERVICE_STATUS = {
    "RELATIONAL": {
        "evidence_ref": "docs/evidence/phase04-postgres-session-runtime.md",
        "current_runtime_status": "PROVEN",
    },
    "QUEUE": {
        "evidence_ref": "docs/evidence/phase04-rabbitmq-transport.md",
        "current_runtime_status": "PROVEN",
    },
    "OBJECT": {
        "evidence_ref": "docs/evidence/phase04-minio-object-store.md",
        "current_runtime_status": "PROVEN",
    },
    "CHECKPOINT": {
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "BLOCKED",
    },
    "VECTOR": {
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "GRAPH": {
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "LEXICAL": {
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "CACHE": {
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "SECRET_KMS": {
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "TRACE_AUDIT": {
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


def _capabilities(
    profile: InfrastructureCapabilityProfileV1,
) -> dict[str, DataServiceCapabilityV1]:
    capabilities: dict[str, DataServiceCapabilityV1] = {}
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
            capabilities[capability.service_kind] = capability
    return capabilities


def _upgrade_profile(
    capability: DataServiceCapabilityV1,
) -> UpgradeCompatibilityProfileV1:
    status = SERVICE_STATUS[capability.service_kind]
    payload = {
        "profile_id": (
            f"phase04-upgrade-compatibility-{capability.service_kind.lower()}"
        ),
        "service_kind": capability.service_kind,
        "profile_version": "phase04.upgrade.v1",
        "current_adapter_version": capability.adapter_version,
        "current_schema_or_contract_version": capability.schema_or_contract_version,
        "read_compatible_adapter_versions": (capability.adapter_version,),
        "write_compatible_adapter_versions": (capability.adapter_version,),
        "rollback_compatible_adapter_versions": (capability.adapter_version,),
        "read_compatible_schema_or_contract_versions": (
            capability.schema_or_contract_version,
        ),
        "write_compatible_schema_or_contract_versions": (
            capability.schema_or_contract_version,
        ),
        "rollback_compatible_schema_or_contract_versions": (
            capability.schema_or_contract_version,
        ),
        "unsupported_adapter_versions": ("unknown-major",),
        "unsupported_schema_or_contract_versions": ("unknown-major",),
        "unknown_adapter_version_action": "FAIL_CLOSED",
        "unknown_schema_or_contract_version_action": "FAIL_CLOSED",
        **status,
    }
    return UpgradeCompatibilityProfileV1(
        **payload,
        content_hash=canonical_sha256(payload),
    )


def _version_is_compatible(
    profile: UpgradeCompatibilityProfileV1,
    *,
    adapter_version: str,
    schema_or_contract_version: str,
    mode: str,
) -> bool:
    adapter_versions = getattr(profile, f"{mode}_compatible_adapter_versions")
    schema_versions = getattr(profile, f"{mode}_compatible_schema_or_contract_versions")
    return (
        adapter_version in adapter_versions
        and schema_or_contract_version in schema_versions
    )


def verify_phase04_upgrade_compatibility_profiles() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    capabilities = _capabilities(server)

    missing_status = sorted(set(capabilities) - SERVICE_STATUS.keys())
    if missing_status:
        errors.append(f"missing upgrade compatibility status: {missing_status!r}")

    for service_kind, capability in sorted(capabilities.items()):
        try:
            profile = _upgrade_profile(capability)
        except ValidationError as exc:
            errors.append(
                f"{service_kind} upgrade compatibility profile failed validation: {exc}"
            )
            continue
        if profile.current_adapter_version != capability.adapter_version:
            errors.append(f"{service_kind} adapter version is not capability-derived")
        if (
            profile.current_schema_or_contract_version
            != capability.schema_or_contract_version
        ):
            errors.append(f"{service_kind} schema version is not capability-derived")
        for mode in ["read", "write", "rollback"]:
            if not _version_is_compatible(
                profile,
                adapter_version=capability.adapter_version,
                schema_or_contract_version=capability.schema_or_contract_version,
                mode=mode,
            ):
                errors.append(f"{service_kind} {mode} compatibility is not explicit")
        if _version_is_compatible(
            profile,
            adapter_version="phase05.unknown-major",
            schema_or_contract_version=capability.schema_or_contract_version,
            mode="read",
        ):
            errors.append(f"{service_kind} unknown adapter version did not fail closed")
        if _version_is_compatible(
            profile,
            adapter_version=capability.adapter_version,
            schema_or_contract_version="phase05.unknown-major",
            mode="read",
        ):
            errors.append(f"{service_kind} unknown schema version did not fail closed")
        if profile.content_hash != canonical_sha256(profile.hash_inputs()):
            errors.append(f"{service_kind} content hash is not canonical")
        if not (REPO_ROOT / profile.evidence_ref).exists():
            errors.append(f"{service_kind} evidence_ref does not exist")

    relational = _upgrade_profile(capabilities["RELATIONAL"])
    mutated = relational.hash_inputs()
    mutated["current_adapter_version"] = "phase04.v2"
    if canonical_sha256(mutated) == relational.content_hash:
        errors.append("adapter version change did not change profile hash")

    try:
        UpgradeCompatibilityProfileV1(**relational.hash_inputs(), content_hash="bad")
        errors.append("invalid upgrade compatibility content_hash was accepted")
    except ValidationError:
        pass

    try:
        UpgradeCompatibilityProfileV1(
            **{
                **relational.hash_inputs(),
                "profile_id": "bad-upgrade-profile",
                "read_compatible_adapter_versions": (),
            },
            content_hash=relational.content_hash,
        )
        errors.append("empty compatibility window was accepted")
    except ValidationError:
        pass

    return errors


def main() -> int:
    errors = verify_phase04_upgrade_compatibility_profiles()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 upgrade compatibility profile verification failed.")
        return 1
    print("PHASE04 upgrade compatibility profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
