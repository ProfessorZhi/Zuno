from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from zuno.platform.contracts import (
    DataServiceCapabilityV1,
    InfrastructureCapabilityProfileV1,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
RELEASE_PROVENANCE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_release_provenance_manifest.py"
)

DERIVED_INDEXES = {
    "VECTOR": {
        "field": "vector_index",
        "adapter_name": "milvus-target",
        "required_semantic": "versioned_index",
    },
    "GRAPH": {
        "field": "graph_index",
        "adapter_name": "neo4j-target",
        "required_semantic": "versioned_graph",
    },
    "LEXICAL": {
        "field": "lexical_index",
        "adapter_name": "bm25-target",
        "required_semantic": "versioned_lexical_index",
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


def _derived_capabilities(
    profile: InfrastructureCapabilityProfileV1,
) -> dict[str, DataServiceCapabilityV1]:
    capabilities: dict[str, DataServiceCapabilityV1] = {}
    for service_kind, spec in DERIVED_INDEXES.items():
        capability = getattr(profile, spec["field"])
        if capability is not None:
            capabilities[service_kind] = capability
    return capabilities


def verify_phase04_derived_index_boundary() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    developer = _profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")
    server_capabilities = _derived_capabilities(server)
    developer_capabilities = _derived_capabilities(developer)

    if set(server_capabilities) != set(DERIVED_INDEXES):
        errors.append("server derived index coverage is incomplete")
    if set(developer_capabilities) != set(DERIVED_INDEXES):
        errors.append("developer derived index coverage is incomplete")

    for service_kind, spec in DERIVED_INDEXES.items():
        for profile_name, capability in [
            ("server", server_capabilities.get(service_kind)),
            ("developer", developer_capabilities.get(service_kind)),
        ]:
            if capability is None:
                continue
            if capability.service_kind != service_kind:
                errors.append(f"{profile_name} {service_kind} service_kind mismatch")
            if capability.adapter_name != spec["adapter_name"]:
                errors.append(f"{profile_name} {service_kind} adapter mismatch")
            if capability.authoritative:
                errors.append(f"{profile_name} {service_kind} is authoritative")
            if not capability.rebuildable:
                errors.append(f"{profile_name} {service_kind} is not rebuildable")
            if capability.backup_restore_class != "rebuild-from-source":
                errors.append(
                    f"{profile_name} {service_kind} is not rebuild-from-source"
                )
            if capability.consistency_model != "rebuildable":
                errors.append(f"{profile_name} {service_kind} is not rebuildable model")
            if spec["required_semantic"] not in capability.supported_semantics:
                errors.append(f"{profile_name} {service_kind} lacks versioned semantic")
            if "server_adapter_not_current" not in capability.unsupported_semantics:
                errors.append(
                    f"{profile_name} {service_kind} target adapter boundary is missing"
                )

    release_provenance = _load_module(
        RELEASE_PROVENANCE_VERIFIER,
        "verify_phase04_release_provenance_manifest",
    )
    forbidden_services = {"milvus", "neo4j", "bm25", "lexical", "search"}
    manifest = release_provenance._release_manifest()
    for service in forbidden_services:
        if service in release_provenance.REQUIRED_INFRA_SERVICES:
            errors.append(f"{service} is incorrectly required release infrastructure")
        if any(service in version.lower() for version in manifest.adapter_versions):
            errors.append(f"{service} appears in required release adapter versions")

    return errors


def main() -> int:
    errors = verify_phase04_derived_index_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 derived index boundary verification failed.")
        return 1
    print("PHASE04 derived index boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
