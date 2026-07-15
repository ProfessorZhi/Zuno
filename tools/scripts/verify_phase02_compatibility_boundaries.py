from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"

REQUIRED = {
    "api": WORK_PRODUCTS / "api-contract-compatibility-matrix.yaml",
    "flags": WORK_PRODUCTS / "feature-flag-registry.yaml",
    "allowlist": WORK_PRODUCTS / "temporary-allowlist.yaml",
    "data": WORK_PRODUCTS / "data-cutover-matrix.yaml",
    "rollback": WORK_PRODUCTS / "rollback-recovery-playbook.md",
    "readiness": WORK_PRODUCTS / "phase02-readiness.yaml",
    "p01_legacy": WORK_PRODUCTS / "legacy-bypass-inventory.yaml",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _path_values(text: str) -> set[str]:
    return set(re.findall(r'^\s+- path: "([^"]+)"', text, re.MULTILINE))


def _blocks(text: str, marker: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                result.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        result.append("\n".join(current))
    return result


def verify_phase02_compatibility_boundaries() -> list[str]:
    errors: list[str] = []
    for label, path in REQUIRED.items():
        if not path.exists():
            errors.append(f"missing PHASE02 {label} artifact: {path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        return errors

    api = _read(REQUIRED["api"])
    flags = _read(REQUIRED["flags"])
    allowlist = _read(REQUIRED["allowlist"])
    data = _read(REQUIRED["data"])
    rollback = _read(REQUIRED["rollback"])
    readiness = _read(REQUIRED["readiness"])
    p01_legacy = _read(REQUIRED["p01_legacy"])

    for phrase in [
        "version_adapter_then_remove",
        "Security/Budget/Trace/RunOutcome preserved",
        "reauthorization on reconnect",
        "PreparedToolAction hash binding",
        "No compatibility adapter may own domain state",
    ]:
        if phrase not in api:
            errors.append(f"api-contract-compatibility-matrix.yaml missing phrase: {phrase}")

    if "allowed_states: [DECLARED, SHADOW, CANARY, DEFAULT_NEW, ROLLBACK_WINDOW, RETIRED]" not in flags:
        errors.append("feature-flag-registry.yaml missing full lifecycle")
    flag_blocks = _blocks(flags, "  - flag: ")
    if len(flag_blocks) < 5:
        errors.append("feature-flag-registry.yaml must define at least five rollout flags")
    for block in flag_blocks:
        for field in ["owner:", "scope:", "default:", "metric:", "rollback_command:", "expires_at_phase:", "retire_task:"]:
            if field not in block:
                errors.append(f"feature flag missing {field}: {block.splitlines()[0]}")
        if "retire_task: \"P22-T03\"" not in block:
            errors.append(f"feature flag missing P22-T03 retire task: {block.splitlines()[0]}")
        if "domain_fact_owner: \"unchanged\"" not in block and "domain_fact_owner: \"canonical owner tables after cutover\"" not in block:
            errors.append(f"feature flag must not own domain facts: {block.splitlines()[0]}")

    p01_paths = _path_values(p01_legacy)
    p02_paths = _path_values(allowlist)
    missing_paths = sorted(p01_paths - p02_paths)
    if missing_paths:
        errors.append(f"temporary-allowlist.yaml missing P01 legacy paths: {missing_paths[:10]}")
    allowlist_blocks = _blocks(allowlist, "  - path: ")
    for block in allowlist_blocks:
        for field in ["category:", "reason:", "owner:", "test:", "removal_task:", "deadline_phase:"]:
            if field not in block:
                errors.append(f"temporary allowlist entry missing {field}: {block.splitlines()[0]}")
        if 'removal_task: "P22-T03"' not in block:
            errors.append(f"temporary allowlist entry missing P22-T03 removal: {block.splitlines()[0]}")
    if 'new_bypass_default: "fail"' not in allowlist or 'final_zero_task: "P22-T03"' not in allowlist:
        errors.append("temporary-allowlist.yaml must declare fail-by-default and final zero task")

    for phrase in [
        "default_dual_write: \"forbidden_without_coordinator_decision\"",
        "SQLiteAgentRunStore",
        "WorkspaceTaskRuntimeService",
        "SQLiteDurableIngestionStore",
        "EffectReconciliation",
        "greenfield:",
    ]:
        if phrase not in data:
            errors.append(f"data-cutover-matrix.yaml missing phrase: {phrase}")
    for block in _blocks(data, "  - data_owner: "):
        for field in ["source:", "target:", "transform:", "hash:", "backfill_chunk:", "verification:", "rollback:", "retention:", "target_phase:", "removal_task:"]:
            if field not in block:
                errors.append(f"data cutover entry missing {field}: {block.splitlines()[0]}")

    for phrase in [
        "Rollback 不能恢复到绕过 Security",
        "Tool UNKNOWN",
        "HTTP 2xx, SSE close, Queue ACK, Object Commit and Audit Delivery",
        "forward-fix",
        "P22-T03",
    ]:
        if phrase not in rollback:
            errors.append(f"rollback-recovery-playbook.md missing phrase: {phrase}")

    for task_id in [f"P02-T{index:02d}" for index in range(1, 7)]:
        if task_id not in readiness:
            errors.append(f"phase02-readiness.yaml missing work package: {task_id}")
    if "unassigned: []" not in readiness:
        errors.append("phase02-readiness.yaml must show no unassigned P0 risks")
    return errors


def main() -> int:
    errors = verify_phase02_compatibility_boundaries()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE02 compatibility boundary verification failed.")
        return 1
    print("PHASE02 compatibility boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
