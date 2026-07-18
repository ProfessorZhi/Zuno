from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DR_PROFILE = REPO_ROOT / "docs" / "governance" / "infrastructure-dr-profile.yaml"

REQUIRED_COMPONENTS = {
    "postgresql_domain_store",
    "object_manifest_and_minio",
    "rabbitmq_outbox_inbox_delivery",
    "langgraph_postgres_checkpointer",
    "product_projection_replay",
    "pitr",
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


def verify_phase04_dr_profile() -> list[str]:
    errors: list[str] = []
    if not DR_PROFILE.exists():
        return ["missing infrastructure DR profile"]

    data = yaml.safe_load(DR_PROFILE.read_text(encoding="utf-8"))
    if data.get("status") != "implementation_available_for_phase04_dr_profile_subscope":
        errors.append("DR profile status does not mark the DR profile subscope current")
    if data.get("phase") != "PHASE04" or data.get("task_id") != "P04-T07":
        errors.append("DR profile is not bound to PHASE04/P04-T07")
    if data.get("owner") != "Infrastructure":
        errors.append("DR profile owner must be Infrastructure")
    if data.get("deployment_class") != "SERVER_PRODUCT":
        errors.append("DR profile must target SERVER_PRODUCT")
    if data.get("phase04_completion_claim") is not False:
        errors.append("DR profile must not claim PHASE04 completion")
    if data.get("phase05_ready") is not False:
        errors.append("DR profile must keep PHASE05 not ready")
    boundary = _as_text(data.get("boundary"))
    if (
        "PITR alignment" not in boundary
        or "official LangGraph PostgreSQL Checkpointer graph interrupt/resume plus retention cleanup plus backup/restore" not in boundary
        or "Product Projection Replay from restored authoritative fact" not in boundary
        or "combined-service fault remain" not in boundary
    ):
        errors.append("DR profile boundary must separate proven recovery subsets from remaining blockers")

    cutover_policy = data.get("cutover_policy") or {}
    if cutover_policy.get("explicit_cutover_required") is not True:
        errors.append("DR profile must require explicit cutover approval")
    if cutover_policy.get("cutover_allowed_by_default") is not False:
        errors.append("DR profile must fail closed for automatic cutover")
    if not _as_text(cutover_policy.get("approval_owner")):
        errors.append("DR profile cutover approval owner is missing")

    profiles = data.get("recovery_profiles")
    if not isinstance(profiles, list):
        return errors + ["DR profile recovery_profiles must be a list"]

    components = {item.get("component") for item in profiles if isinstance(item, dict)}
    missing = sorted(REQUIRED_COMPONENTS - components)
    if missing:
        errors.append(f"DR profile missing component(s): {missing!r}")

    for item in profiles:
        if not isinstance(item, dict):
            errors.append("DR profile recovery profile entry is not an object")
            continue
        component = _as_text(item.get("component"))
        for key in [
            "authority",
            "owner",
            "recovery_owner",
            "rpo",
            "rto",
            "backup_method",
            "verification_command",
            "evidence_ref",
            "current_status",
            "current_boundary",
        ]:
            if not _as_text(item.get(key)):
                errors.append(f"{component or '<missing>'} missing {key}")
        command = _as_text(item.get("verification_command"))
        if command and not _command_has_known_boundary(command):
            errors.append(f"{component} verification command is not executable/bounded")
        evidence_ref = _as_text(item.get("evidence_ref"))
        if evidence_ref and not _path_exists(evidence_ref):
            errors.append(f"{component} evidence_ref does not exist: {evidence_ref}")

    by_component: dict[str, dict[str, Any]] = {
        _as_text(item.get("component")): item
        for item in profiles
        if isinstance(item, dict)
    }
    checkpointer = by_component.get("langgraph_postgres_checkpointer") or {}
    if checkpointer.get("current_status") != "implementation_available_subset":
        errors.append("official Checkpointer DR profile must reference the proven backup/restore subset")
    if (
        checkpointer.get("verification_command")
        != "python tools/scripts/verify_phase04_official_checkpointer_backup_restore.py"
    ):
        errors.append("official Checkpointer DR profile must use the official backup/restore verifier")

    pitr = by_component.get("pitr") or {}
    if pitr.get("current_status") != "implementation_available_subset":
        errors.append("PITR DR profile must reference the proven PITR alignment subset")
    if pitr.get("verification_command") != "python tools/scripts/verify_phase04_pitr_alignment.py":
        errors.append("PITR DR profile must use the PITR alignment verifier")

    projection = by_component.get("product_projection_replay") or {}
    if projection.get("current_status") != "implementation_available_subset":
        errors.append("product projection replay must reference the proven restore/replay subset")
    if (
        projection.get("verification_command")
        != "python tools/scripts/verify_phase04_backup_restore_replay.py"
    ):
        errors.append("product projection replay must use the backup/restore/replay verifier")

    return errors


def main() -> int:
    errors = verify_phase04_dr_profile()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 DR profile verification failed.")
        return 1
    print("PHASE04 DR profile verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
