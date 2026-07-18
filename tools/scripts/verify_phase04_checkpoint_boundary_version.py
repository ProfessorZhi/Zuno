from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SCHEMA_REGISTRY = (
    REPO_ROOT
    / "src"
    / "backend"
    / "zuno"
    / "platform"
    / "database"
    / "schema_registry.py"
)
DATABASE_README = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "database" / "README.md"
)
CONTRACT_REGISTRY = (
    REPO_ROOT / "docs" / "governance" / "wave1-cross-module-contract-registry.md"
)
CAPABILITY_PROFILE_VERIFIER = (
    REPO_ROOT
    / "tools"
    / "scripts"
    / "verify_phase04_infrastructure_capability_profile.py"
)
UPGRADE_PROFILE_VERIFIER = (
    REPO_ROOT / "tools" / "scripts" / "verify_phase04_upgrade_compatibility_profiles.py"
)
CAPABILITY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-infrastructure-capability-profile.md"
)
UPGRADE_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-upgrade-compatibility-profiles.md"
)
BOUNDARY_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-checkpoint-boundary-version.md"
)
COMPLETE_BLOCKER_EVIDENCE = (
    REPO_ROOT / "docs" / "evidence" / "phase04-complete-infrastructure-blocker.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_file(path: Path, errors: list[str]) -> str:
    if not path.exists():
        errors.append(
            f"missing required file: {path.relative_to(REPO_ROOT).as_posix()}"
        )
        return ""
    return _read(path)


def _load_module(path: Path, name: str):
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path.relative_to(REPO_ROOT).as_posix()}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_phase04_checkpoint_boundary_version() -> list[str]:
    errors: list[str] = []

    schema_registry = _require_file(SCHEMA_REGISTRY, errors)
    database_readme = _require_file(DATABASE_README, errors)
    contract_registry = _require_file(CONTRACT_REGISTRY, errors)
    capability_evidence = _require_file(CAPABILITY_EVIDENCE, errors)
    upgrade_evidence = _require_file(UPGRADE_EVIDENCE, errors)
    boundary_evidence = _require_file(BOUNDARY_EVIDENCE, errors)
    complete_evidence = _require_file(COMPLETE_BLOCKER_EVIDENCE, errors)

    capability_module = _load_module(
        CAPABILITY_PROFILE_VERIFIER,
        "verify_phase04_infrastructure_capability_profile",
    )
    upgrade_module = _load_module(
        UPGRADE_PROFILE_VERIFIER,
        "verify_phase04_upgrade_compatibility_profiles",
    )

    capability_errors = (
        capability_module.verify_phase04_infrastructure_capability_profile()
    )
    errors.extend(
        f"capability profile dependency failed: {error}" for error in capability_errors
    )
    upgrade_errors = upgrade_module.verify_phase04_upgrade_compatibility_profiles()
    errors.extend(
        f"upgrade profile dependency failed: {error}" for error in upgrade_errors
    )

    profile = capability_module._profile(
        deployment_class="SERVER_PRODUCT", profile_version="phase04.1"
    )
    checkpoint = profile.checkpoint_store
    if checkpoint.service_kind != "CHECKPOINT":
        errors.append("checkpoint service kind drifted")
    if checkpoint.adapter_name != "official-langgraph-postgres-checkpointer":
        errors.append("checkpoint adapter name drifted")
    if "official_adapter_not_yet_installed" not in checkpoint.unsupported_semantics:
        errors.append("checkpoint unsupported official adapter boundary is missing")
    if checkpoint.schema_or_contract_version != "phase04.contract.v1":
        errors.append("checkpoint schema_or_contract_version drifted")

    checkpoint_upgrade = upgrade_module._upgrade_profile(checkpoint)
    if checkpoint_upgrade.current_runtime_status != "BLOCKED":
        errors.append("checkpoint upgrade profile must remain BLOCKED")
    if checkpoint_upgrade.unknown_adapter_version_action != "FAIL_CLOSED":
        errors.append("checkpoint unknown adapter version must fail closed")
    if checkpoint_upgrade.unknown_schema_or_contract_version_action != "FAIL_CLOSED":
        errors.append("checkpoint unknown schema version must fail closed")
    if upgrade_module._version_is_compatible(
        checkpoint_upgrade,
        adapter_version="phase05.unknown-major",
        schema_or_contract_version=checkpoint.schema_or_contract_version,
        mode="read",
    ):
        errors.append("checkpoint unknown adapter major version was read-compatible")
    if upgrade_module._version_is_compatible(
        checkpoint_upgrade,
        adapter_version=checkpoint.adapter_version,
        schema_or_contract_version="phase05.unknown-major",
        mode="write",
    ):
        errors.append("checkpoint unknown schema major version was write-compatible")

    for phrase in [
        '"agent_runtime_checkpoints": "Agent Core / Planning & Control"',
        '"infra_checkpoints"',
    ]:
        if phrase not in schema_registry:
            errors.append(
                f"schema registry missing checkpoint/domain split phrase: {phrase}"
            )
    for phrase in [
        "禁止在 Infrastructure 表或 receipt 中复制领域终态",
        "checkpoint receipt 解释为领域成功",
    ]:
        if phrase not in database_readme:
            errors.append(
                f"database README missing checkpoint boundary phrase: {phrase}"
            )
    if "Checkpoint Commit != Domain Commit" not in contract_registry:
        errors.append("contract registry missing Checkpoint Commit boundary")

    for phrase in [
        "unsupported_semantics_explicit: passed",
        "It does not prove official LangGraph PostgreSQL Checkpointer integration",
    ]:
        if phrase not in capability_evidence:
            errors.append(f"capability evidence missing phrase: {phrase}")
    for phrase in [
        "unknown_version_fail_closed: passed",
        "Official LangGraph PostgreSQL Checkpointer remains blocked",
    ]:
        if phrase not in upgrade_evidence:
            errors.append(f"upgrade evidence missing phrase: {phrase}")
    for phrase in [
        "checkpoint_domain_fact_separation: passed",
        "checkpoint_version_fail_closed: passed",
        "official_checkpointer_runtime_boundary: passed",
        "phase_completion: blocked_combined_fault_and_cross_domain_replay_boundary",
        "不证明 combined-service fault、跨领域 replay final cutover 或 PHASE04 closure",
    ]:
        if phrase not in boundary_evidence:
            errors.append(f"checkpoint boundary evidence missing phrase: {phrase}")
    for phrase in [
        "langgraph_postgres_checkpointer: proven",
        "infrastructure_capability_profile: proven",
        "upgrade_compatibility_profiles: proven",
    ]:
        if phrase not in complete_evidence:
            errors.append(f"complete blocker evidence missing phrase: {phrase}")

    return errors


def main() -> int:
    errors = verify_phase04_checkpoint_boundary_version()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE04 checkpoint boundary/version verification failed.")
        return 1
    print("PHASE04 checkpoint boundary/version verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
