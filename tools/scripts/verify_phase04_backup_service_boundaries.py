from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DR_PROFILE = REPO_ROOT / "docs" / "governance" / "infrastructure-dr-profile.yaml"
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
BACKUP_SCOPE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-backup-service-boundaries.md"
)

REQUIRED_BACKUP_COMPONENTS = {
    "postgresql_domain_store",
    "object_manifest_and_minio",
    "rabbitmq_outbox_inbox_delivery",
    "langgraph_postgres_checkpointer",
    "product_projection_replay",
    "pitr",
}

SERVICE_BOUNDARY_EXPECTATIONS = {
    "database": {
        "service_kind": "RELATIONAL",
        "adapter_name": "postgresql",
        "semantic": "transaction",
        "authoritative": True,
    },
    "queue": {
        "service_kind": "QUEUE",
        "adapter_name": "rabbitmq",
        "semantic": "publisher_confirm",
        "authoritative": False,
    },
    "object_store": {
        "service_kind": "OBJECT",
        "adapter_name": "minio-s3",
        "semantic": "restore",
        "authoritative": False,
    },
    "checkpoint_store": {
        "service_kind": "CHECKPOINT",
        "adapter_name": "official-langgraph-postgres-checkpointer",
        "semantic": "resume",
        "authoritative": False,
        "unsupported": "official_adapter_not_yet_installed",
    },
}


def _as_text(value: object) -> str:
    return str(value or "").strip()


def _path_exists(ref: str) -> bool:
    if not ref.startswith(("docs/", ".agent/", "tools/", "tests/")):
        return False
    return (REPO_ROOT / ref.split(":", 1)[0]).exists()


def _command_has_known_boundary(command: str) -> bool:
    if command.startswith("python "):
        script = command.split()[1]
        return (REPO_ROOT / script).exists()
    return command.startswith(("blocked:", "target_not_current:"))


def _load_dr_profile() -> dict[str, Any]:
    if not DR_PROFILE.exists():
        raise FileNotFoundError("missing infrastructure DR profile")
    data = yaml.safe_load(DR_PROFILE.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("infrastructure DR profile must be a mapping")
    return data


def _load_capability_profile_verifier():
    spec = spec_from_file_location(
        "verify_phase04_infrastructure_capability_profile",
        CAPABILITY_PROFILE_VERIFIER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load capability profile verifier")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_backup_scope_profiles(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("backup_scope_profile_version") != 1:
        errors.append("backup scope profile version must be fixed to 1")
    boundary = _as_text(data.get("backup_scope_boundary"))
    for phrase in [
        "backup scope",
        "RPO source",
        "encryption requirement",
        "verification command",
        "does not claim production encrypted backup completion",
    ]:
        if phrase not in boundary:
            errors.append(f"backup scope boundary missing phrase: {phrase}")

    profiles = data.get("backup_scope_profiles")
    if not isinstance(profiles, list):
        return errors + ["backup_scope_profiles must be a list"]
    recovery_profiles = data.get("recovery_profiles")
    if not isinstance(recovery_profiles, list):
        return errors + ["recovery_profiles must be a list"]

    backup_components = {
        item.get("component") for item in profiles if isinstance(item, dict)
    }
    recovery_components = {
        item.get("component") for item in recovery_profiles if isinstance(item, dict)
    }
    if backup_components != REQUIRED_BACKUP_COMPONENTS:
        errors.append(f"backup scope components drifted: {sorted(backup_components)!r}")
    if backup_components != recovery_components:
        errors.append("backup scope components must match recovery profile components")

    for item in profiles:
        if not isinstance(item, dict):
            errors.append("backup scope entry is not an object")
            continue
        component = _as_text(item.get("component"))
        for key in [
            "backup_scope",
            "rpo_source",
            "encryption_requirement",
            "encryption_current_boundary",
            "verification_command",
            "evidence_ref",
            "completion_boundary",
        ]:
            if not _as_text(item.get(key)):
                errors.append(f"{component or '<missing>'} missing {key}")
        encryption_requirement = _as_text(item.get("encryption_requirement")).lower()
        if not any(token in encryption_requirement for token in ["encrypt", "kms"]):
            errors.append(f"{component} encryption requirement is not explicit")
        command = _as_text(item.get("verification_command"))
        if command and not _command_has_known_boundary(command):
            errors.append(f"{component} verification command is not executable/bounded")
        evidence_ref = _as_text(item.get("evidence_ref"))
        if evidence_ref and not _path_exists(evidence_ref):
            errors.append(f"{component} evidence_ref does not exist: {evidence_ref}")

    by_component = {
        _as_text(item.get("component")): item
        for item in profiles
        if isinstance(item, dict)
    }
    postgres_boundary = _as_text(
        by_component.get("postgresql_domain_store", {}).get(
            "encryption_current_boundary"
        )
    )
    if (
        "production encrypted backup" not in postgres_boundary
        or "not promoted" not in postgres_boundary
    ):
        errors.append("PostgreSQL backup encryption boundary must reject overclaiming")
    if "blocked by dependency approval" not in _as_text(
        by_component.get("langgraph_postgres_checkpointer", {}).get(
            "encryption_current_boundary"
        )
    ):
        errors.append("Checkpointer backup scope must remain blocked")
    if "target_not_current" not in _as_text(
        by_component.get("pitr", {}).get("completion_boundary")
    ):
        errors.append("PITR backup scope must remain target_not_current")

    return errors


def _verify_service_capability_boundaries() -> list[str]:
    verifier = _load_capability_profile_verifier()
    errors = verifier.verify_phase04_infrastructure_capability_profile()
    if errors:
        return [f"capability profile dependency failed: {error}" for error in errors]

    profile = verifier._profile(
        deployment_class="SERVER_PRODUCT", profile_version="phase04.1"
    )
    for capability_name, expected in SERVICE_BOUNDARY_EXPECTATIONS.items():
        capability = getattr(profile, capability_name)
        if capability.service_kind != expected["service_kind"]:
            errors.append(f"{capability_name} service kind drifted")
        if capability.adapter_name != expected["adapter_name"]:
            errors.append(f"{capability_name} adapter name drifted")
        if capability.authoritative is not expected["authoritative"]:
            errors.append(f"{capability_name} authoritative boundary drifted")
        if expected["semantic"] not in capability.supported_semantics:
            errors.append(f"{capability_name} missing supported semantic")
        unsupported = expected.get("unsupported")
        if unsupported and unsupported not in capability.unsupported_semantics:
            errors.append(f"{capability_name} missing unsupported semantic boundary")

    return errors


def _verify_evidence_file() -> list[str]:
    if not BACKUP_SCOPE_EVIDENCE.exists():
        return ["missing PHASE04 backup/service boundary evidence"]
    evidence = BACKUP_SCOPE_EVIDENCE.read_text(encoding="utf-8")
    return [
        f"backup/service boundary evidence missing phrase: {phrase}"
        for phrase in [
            "backup_scope_profile: passed",
            "backup_rpo_source_coverage: passed",
            "backup_encryption_requirement_defined: passed",
            "service_boundary_profile: passed",
            "checkpoint_boundary_blocked_not_completed: passed",
            "phase_completion: blocked_official_checkpointer_and_full_recovery_set",
            "不证明生产 encrypted backup、PITR、完整 RecoverySet 或 official Checkpointer restore",
        ]
        if phrase not in evidence
    ]


def verify_phase04_backup_service_boundaries() -> list[str]:
    try:
        data = _load_dr_profile()
    except (FileNotFoundError, ValueError) as exc:
        return [str(exc)]

    errors: list[str] = []
    errors.extend(_verify_backup_scope_profiles(data))
    errors.extend(_verify_service_capability_boundaries())
    errors.extend(_verify_evidence_file())
    return errors


def main() -> int:
    errors = verify_phase04_backup_service_boundaries()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 backup/service boundary verification failed.")
        return 1
    print("PHASE04 backup/service boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
