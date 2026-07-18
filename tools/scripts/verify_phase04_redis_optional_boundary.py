from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from zuno.platform.contracts import InfrastructureCapabilityProfileV1

REPO_ROOT = Path(__file__).resolve().parents[2]
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
COMPLETE_INFRA_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_complete_infrastructure.py"
)
RELEASE_PROVENANCE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_release_provenance_manifest.py"
)


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


def verify_phase04_redis_optional_boundary() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    developer = _profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")

    if server.cache is None:
        errors.append("server profile has no CACHE service")
    if developer.cache is None:
        errors.append("developer profile has no CACHE service")
    if errors:
        return errors

    for profile_name, cache in [
        ("server", server.cache),
        ("developer", developer.cache),
    ]:
        if cache.service_kind != "CACHE":
            errors.append(f"{profile_name} cache service_kind is not CACHE")
        if cache.adapter_name != "redis-optional-cache":
            errors.append(f"{profile_name} cache adapter is not Redis optional cache")
        if cache.authoritative:
            errors.append(f"{profile_name} Redis cache is authoritative")
        if not cache.rebuildable:
            errors.append(f"{profile_name} Redis cache is not rebuildable")
        if cache.backup_restore_class != "rebuild-from-source":
            errors.append(f"{profile_name} Redis cache is not rebuild-from-source")
        if "optional_acceleration" not in cache.supported_semantics:
            errors.append(f"{profile_name} Redis optional acceleration is missing")
        if "not_authoritative" not in cache.unsupported_semantics:
            errors.append(f"{profile_name} Redis non-authoritative marker is missing")
        if cache.consistency_model != "rebuildable":
            errors.append(f"{profile_name} Redis consistency model is not rebuildable")

    complete_infra = _load_module(
        COMPLETE_INFRA_VERIFIER,
        "verify_phase04_complete_infrastructure",
    )
    if "Redis" in complete_infra.REQUIRED_REAL_SERVICES:
        errors.append(
            "Redis is incorrectly required for PHASE04 complete infrastructure"
        )
    for service_name in complete_infra.REQUIRED_REAL_SERVICES:
        if service_name.lower().startswith("redis"):
            errors.append("Redis appears in required real services")

    release_provenance = _load_module(
        RELEASE_PROVENANCE_VERIFIER,
        "verify_phase04_release_provenance_manifest",
    )
    if "redis" in release_provenance.REQUIRED_INFRA_SERVICES:
        errors.append("Redis is incorrectly bound as required release infrastructure")
    manifest = release_provenance._release_manifest()
    if any("redis" in version.lower() for version in manifest.adapter_versions):
        errors.append("Redis adapter appears in required release adapter versions")

    return errors


def main() -> int:
    errors = verify_phase04_redis_optional_boundary()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 Redis optional boundary verification failed.")
        return 1
    print("PHASE04 Redis optional boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
