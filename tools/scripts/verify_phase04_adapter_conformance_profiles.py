from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pydantic import ValidationError

from zuno.platform.contracts import (
    AdapterConformanceProfileV1,
    DataServiceCapabilityV1,
    InfrastructureCapabilityProfileV1,
    canonical_sha256,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
CONFORMANCE_SUITE_VERSION = "phase04.infrastructure.conformance.v1"

SERVICE_EVIDENCE = {
    "RELATIONAL": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_postgres_session_runtime.py",
            "tests/integration/test_phase04_postgres_foundation.py",
        ),
        "evidence_ref": "docs/evidence/phase04-postgres-session-runtime.md",
        "current_runtime_status": "PROVEN",
    },
    "QUEUE": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_rabbitmq_transport.py",
            "tests/integration/test_phase04_rabbitmq_transport.py",
        ),
        "evidence_ref": "docs/evidence/phase04-rabbitmq-transport.md",
        "current_runtime_status": "PROVEN",
    },
    "OBJECT": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_minio_object_store.py",
            "tests/integration/test_phase04_minio_object_store.py",
        ),
        "evidence_ref": "docs/evidence/phase04-minio-object-store.md",
        "current_runtime_status": "PROVEN",
    },
    "CHECKPOINT": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_complete_infrastructure.py",
        ),
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "BLOCKED",
    },
    "VECTOR": {
        "required_test_refs": (
            "tests/repo/test_phase04_infrastructure_capability_profile.py",
        ),
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "GRAPH": {
        "required_test_refs": (
            "tests/repo/test_phase04_infrastructure_capability_profile.py",
        ),
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "LEXICAL": {
        "required_test_refs": (
            "tests/repo/test_phase04_infrastructure_capability_profile.py",
        ),
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "CACHE": {
        "required_test_refs": (
            "tests/repo/test_phase04_infrastructure_capability_profile.py",
        ),
        "evidence_ref": "docs/evidence/phase04-infrastructure-capability-profile.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "SECRET_KMS": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_complete_infrastructure.py",
        ),
        "evidence_ref": "docs/evidence/phase04-complete-infrastructure-blocker.md",
        "current_runtime_status": "PROFILE_ONLY",
    },
    "TRACE_AUDIT": {
        "required_test_refs": (
            "tools/scripts/verify_phase04_operator_readiness.py",
            "tests/integration/test_phase04_operator_readiness.py",
        ),
        "evidence_ref": "docs/evidence/phase04-operator-readiness.md",
        "current_runtime_status": "PROVEN",
    },
}


class UnsupportedSemanticError(RuntimeError):
    pass


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


def _conformance_profile(
    *,
    deployment_class: str,
    capability: DataServiceCapabilityV1,
) -> AdapterConformanceProfileV1:
    evidence = SERVICE_EVIDENCE[capability.service_kind]
    payload = {
        "profile_id": (
            "phase04-conformance-"
            f"{deployment_class.lower()}-{capability.service_kind.lower()}"
        ),
        "adapter_name": capability.adapter_name,
        "service_kind": capability.service_kind,
        "deployment_class": deployment_class,
        "supported_semantics": capability.supported_semantics,
        "unsupported_semantics": capability.unsupported_semantics,
        "fail_fast_on_unsupported": True,
        "conformance_suite_version": CONFORMANCE_SUITE_VERSION,
        **evidence,
    }
    return AdapterConformanceProfileV1(
        **payload,
        content_hash=canonical_sha256(payload),
    )


def _require_supported_semantic(
    profile: AdapterConformanceProfileV1,
    semantic: str,
) -> None:
    if semantic in profile.supported_semantics:
        return
    if profile.fail_fast_on_unsupported:
        raise UnsupportedSemanticError(
            f"{profile.adapter_name} does not support semantic {semantic}"
        )
    raise RuntimeError("unsupported semantic did not fail fast")


def verify_phase04_adapter_conformance_profiles() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    developer = _profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")
    server_capabilities = _capabilities(server)
    developer_capabilities = _capabilities(developer)

    if set(server_capabilities) != set(developer_capabilities):
        errors.append("developer and server service kind coverage differs")

    missing_evidence = sorted(set(server_capabilities) - SERVICE_EVIDENCE.keys())
    if missing_evidence:
        errors.append(f"missing conformance evidence mapping: {missing_evidence!r}")

    for service_kind in sorted(server_capabilities):
        try:
            server_profile = _conformance_profile(
                deployment_class="SERVER_PRODUCT",
                capability=server_capabilities[service_kind],
            )
            developer_profile = _conformance_profile(
                deployment_class="DEVELOPER_CI",
                capability=developer_capabilities[service_kind],
            )
        except ValidationError as exc:
            errors.append(
                f"{service_kind} conformance profile validation failed: {exc}"
            )
            continue

        if (
            server_profile.conformance_suite_version
            != developer_profile.conformance_suite_version
        ):
            errors.append(f"{service_kind} conformance suite version differs")
        if server_profile.supported_semantics != developer_profile.supported_semantics:
            errors.append(f"{service_kind} supported semantics differ")
        if (
            server_profile.unsupported_semantics
            != developer_profile.unsupported_semantics
        ):
            errors.append(f"{service_kind} unsupported semantics differ")
        if not server_profile.fail_fast_on_unsupported:
            errors.append(f"{service_kind} server profile does not fail fast")
        if not developer_profile.fail_fast_on_unsupported:
            errors.append(f"{service_kind} developer profile does not fail fast")
        if server_profile.content_hash != canonical_sha256(
            server_profile.hash_inputs()
        ):
            errors.append(f"{service_kind} server content hash is not canonical")
        if developer_profile.content_hash != canonical_sha256(
            developer_profile.hash_inputs()
        ):
            errors.append(f"{service_kind} developer content hash is not canonical")
        if server_profile.content_hash == developer_profile.content_hash:
            errors.append(f"{service_kind} deployment_class is not part of hash")

        for ref in (
            server_profile.required_test_refs + developer_profile.required_test_refs
        ):
            if not (REPO_ROOT / ref).exists():
                errors.append(f"{service_kind} required test ref does not exist: {ref}")
        if not (REPO_ROOT / server_profile.evidence_ref).exists():
            errors.append(f"{service_kind} evidence_ref does not exist")

        try:
            _require_supported_semantic(
                developer_profile,
                "phase04.unsupported.local.semantic.probe",
            )
            errors.append(f"{service_kind} unsupported semantic did not fail fast")
        except UnsupportedSemanticError:
            pass

    relational = _conformance_profile(
        deployment_class="DEVELOPER_CI",
        capability=developer_capabilities["RELATIONAL"],
    )
    mutated = relational.hash_inputs()
    mutated["conformance_suite_version"] = "phase04.infrastructure.conformance.v2"
    if canonical_sha256(mutated) == relational.content_hash:
        errors.append("conformance suite version change did not change content hash")

    try:
        AdapterConformanceProfileV1(**relational.hash_inputs(), content_hash="bad")
        errors.append("invalid conformance content_hash was accepted")
    except ValidationError:
        pass

    try:
        payload = relational.hash_inputs()
        payload["fail_fast_on_unsupported"] = False
        payload["content_hash"] = canonical_sha256(payload)
        AdapterConformanceProfileV1(**payload)
        errors.append("fail_fast_on_unsupported=false was accepted")
    except ValidationError:
        pass

    return errors


def main() -> int:
    errors = verify_phase04_adapter_conformance_profiles()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 adapter conformance profile verification failed.")
        return 1
    print("PHASE04 adapter conformance profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
