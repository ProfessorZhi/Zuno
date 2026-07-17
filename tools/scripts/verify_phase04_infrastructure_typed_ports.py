from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from pydantic import ValidationError

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

SERVICE_FIELDS = {
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
}

REQUIRED_SERVICE_KINDS = {
    "RELATIONAL",
    "OBJECT",
    "CHECKPOINT",
    "QUEUE",
    "VECTOR",
    "GRAPH",
    "LEXICAL",
    "CACHE",
    "SECRET_KMS",
    "TRACE_AUDIT",
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


def _service_kind_set(profile: InfrastructureCapabilityProfileV1) -> set[str]:
    kinds: set[str] = set()
    for field in SERVICE_FIELDS:
        capability = getattr(profile, field)
        if capability is not None:
            kinds.add(capability.service_kind)
    return kinds


def verify_phase04_infrastructure_typed_ports() -> list[str]:
    errors: list[str] = []
    server = _profile(deployment_class="SERVER_PRODUCT", profile_version="phase04.1")
    developer = _profile(deployment_class="DEVELOPER_CI", profile_version="phase04.1")

    if type(server) is not type(developer):
        errors.append("developer and server profiles use different profile classes")
    if not isinstance(server.database, DataServiceCapabilityV1):
        errors.append("server database does not use DataServiceCapabilityV1")
    if not isinstance(developer.database, DataServiceCapabilityV1):
        errors.append("developer database does not use DataServiceCapabilityV1")

    profile_fields = type(server).model_fields
    for field in SERVICE_FIELDS:
        if field not in profile_fields:
            errors.append(f"typed profile missing service field: {field}")
            continue
        annotation = profile_fields[field].annotation
        if "DataServiceCapabilityV1" not in repr(annotation):
            errors.append(f"{field} is not typed as DataServiceCapabilityV1")

    if _service_kind_set(server) != REQUIRED_SERVICE_KINDS:
        errors.append(f"server service kinds mismatch: {_service_kind_set(server)!r}")
    if _service_kind_set(developer) != REQUIRED_SERVICE_KINDS:
        errors.append(
            f"developer service kinds mismatch: {_service_kind_set(developer)!r}"
        )
    if _service_kind_set(server) != _service_kind_set(developer):
        errors.append("developer and server service kind sets diverged")

    try:
        DataServiceCapabilityV1(
            service_kind="UNKNOWN",  # type: ignore[arg-type]
            adapter_name="bad",
            adapter_version="phase04.v1",
            deployment_profile="bad",
            authoritative=False,
            rebuildable=False,
            consistency_model="unknown",
            tenant_isolation_mode="unknown",
            backup_restore_class="unknown",
            schema_or_contract_version="phase04.contract.v1",
            config_hash="bad",
            supported_semantics=("bad",),
            unsupported_semantics=(),
        )
        errors.append("unknown service_kind was accepted")
    except ValidationError:
        pass

    return errors


def main() -> int:
    errors = verify_phase04_infrastructure_typed_ports()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 infrastructure typed port verification failed.")
        return 1
    print("PHASE04 infrastructure typed port verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
