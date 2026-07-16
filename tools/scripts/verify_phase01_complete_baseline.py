from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
WORK_PRODUCTS = PROGRAM_ROOT / "work-products"

PHASE01_FILE = PROGRAM_ROOT / "PHASE01_current-baseline-and-requirement-ledger.md"
PHASE_READINESS = WORK_PRODUCTS / "phase-readiness.yaml"
REQUIREMENT_LEDGER = WORK_PRODUCTS / "requirement-ledger.yaml"
PHASE01_BASELINE_COMMIT = "c01420e915db19a3b0d6f979ca4450c8d5de0c85"

INVENTORY_FILES = {
    "P01-T01": WORK_PRODUCTS / "current-runtime-inventory.md",
    "P01-T02": WORK_PRODUCTS / "current-persistence-inventory.md",
    "P01-T04": WORK_PRODUCTS / "frontend-current-inventory.md",
    "P01-T05": WORK_PRODUCTS / "legacy-bypass-inventory.yaml",
}
TEMPORARY_ALLOWLIST = WORK_PRODUCTS / "temporary-allowlist.yaml"
P01_T05_EVIDENCE = REPO_ROOT / "docs" / "evidence" / "phase01-legacy-bypass-inventory.md"

RISK_REGISTER = WORK_PRODUCTS / "program-risk-register.md"

MODULE_REQUIREMENT_SOURCES = [
    REPO_ROOT / "docs" / "modules" / "01-product-surface.md",
    REPO_ROOT / "docs" / "modules" / "02-input-document-ingestion.md",
    REPO_ROOT / "docs" / "modules" / "03-knowledge-agentic-graphrag.md",
    REPO_ROOT / "docs" / "modules" / "04-model-gateway.md",
    REPO_ROOT / "docs" / "modules" / "05-memory-context.md",
    REPO_ROOT / "docs" / "modules" / "06-agent-core-planning-control.md",
    REPO_ROOT / "docs" / "modules" / "07-capability-skill.md",
    REPO_ROOT / "docs" / "modules" / "08-tool-runtime.md",
    REPO_ROOT / "docs" / "modules" / "09-security.md",
    REPO_ROOT / "docs" / "modules" / "10-observability-eval.md",
    REPO_ROOT / "docs" / "modules" / "11-infrastructure.md",
    REPO_ROOT / "docs" / "governance" / "wave1-cross-module-contract-registry.md",
]

REQUIREMENT_PATTERN = re.compile(r"ARCH-[A-Z]+(?:-[A-Z]+)?-\d{3}")
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _extract_start_commit(text: str) -> str | None:
    match = re.search(r"(?m)^(?:start_commit|audit_baseline_commit):\s*([0-9a-f]{40})\s*$", text)
    return match.group(1) if match else None


def _source_requirement_ids() -> set[str]:
    ids: set[str] = set()
    for path in MODULE_REQUIREMENT_SOURCES:
        text = _read(path)
        for line in text.splitlines():
            if not line.lstrip().startswith("|"):
                continue
            match = REQUIREMENT_PATTERN.search(line)
            if not match:
                continue
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            if cells and cells[0] == match.group(0):
                ids.add(match.group(0))
    return ids


def _ledger_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if re.match(r"\s+- requirement_id: ", line):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _yaml_list_blocks(text: str, marker: str = "  - path: ") -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                blocks.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _path_values(text: str) -> set[str]:
    return set(re.findall(r'(?m)^\s+- path: "([^"]+)"', text))


def _field_values(text: str, field: str) -> set[str]:
    return set(re.findall(rf'(?m)^\s+{field}:\s+"([^"]+)"', text))


def _field_list_is_empty(block: str, field: str) -> bool:
    return re.search(rf"(?m)^\s+{field}:\s*\[\]\s*$", block) is not None


def _field_missing(block: str, field: str) -> bool:
    return re.search(rf"(?m)^\s+{field}:", block) is None


def _verify_work_product_freshness(errors: list[str]) -> None:
    for task_id, path in INVENTORY_FILES.items():
        text = _read(path)
        start_commit = _extract_start_commit(text)
        if start_commit is None:
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()} missing start_commit")
        elif not SHA_PATTERN.match(start_commit):
            errors.append(f"{path.relative_to(REPO_ROOT).as_posix()} has invalid start_commit")
        if start_commit and start_commit != PHASE01_BASELINE_COMMIT:
            errors.append(
                f"{task_id} inventory baseline {start_commit} is stale against PHASE01 baseline {PHASE01_BASELINE_COMMIT}"
            )


def _verify_inventory_coverage(errors: list[str]) -> None:
    runtime = _read(INVENTORY_FILES["P01-T01"])
    for phrase in [
        "dynamic",
        "Registry",
        "Factory",
        "Decorator",
        "Plugin Loader",
        "MCP",
        "CLI",
        "Worker",
    ]:
        if phrase not in runtime:
            errors.append(f"P01-T01 runtime inventory missing explicit dynamic-entry coverage: {phrase}")

    persistence = _read(INVENTORY_FILES["P01-T02"])
    for phrase in ["runtime/integration evidence", "Backup", "Restore", "PITR", "real environment"]:
        if phrase not in persistence:
            errors.append(f"P01-T02 persistence inventory missing required evidence boundary: {phrase}")

    frontend = _read(INVENTORY_FILES["P01-T04"])
    for phrase in ["Desktop", "Browser E2E", "SSE resume", "reauthorization", "UNKNOWN"]:
        if phrase not in frontend:
            errors.append(f"P01-T04 frontend inventory missing required surface: {phrase}")

    legacy = _read(INVENTORY_FILES["P01-T05"])
    allowlist = _read(TEMPORARY_ALLOWLIST) if TEMPORARY_ALLOWLIST.exists() else ""
    required_fields = [
        "path",
        "symbol",
        "owner",
        "risk",
        "target_gateway",
        "current_callers",
        "temporary_allowlist",
        "migration_task",
        "removal_task",
        "deadline",
        "guard",
        "test",
    ]
    legacy_paths = _path_values(legacy)
    allowlist_paths = _path_values(allowlist)
    missing_from_allowlist = sorted(legacy_paths - allowlist_paths)
    if missing_from_allowlist:
        errors.append(f"P01-T05 legacy paths missing from PHASE02 temporary allowlist: {missing_from_allowlist[:10]}")
    allowlist_only = sorted(allowlist_paths - legacy_paths)
    if allowlist_only:
        errors.append(f"PHASE02 temporary allowlist has paths not in P01-T05 inventory: {allowlist_only[:10]}")

    required_categories = {
        "root_alias",
        "legacy_directory",
        "direct_provider_sdk",
        "direct_tool_execute",
        "direct_mcp_call",
        "http_side_effect",
        "subprocess",
        "cross_owner_db_write",
        "deprecated_endpoint",
        "old_dto",
        "old_store",
        "old_runtime",
        "dynamic_bypass",
    }
    categories = _field_values(legacy, "category")
    missing_categories = sorted(required_categories - categories)
    if missing_categories:
        errors.append(f"P01-T05 legacy inventory missing bypass categories: {missing_categories}")

    for block in _yaml_list_blocks(legacy):
        first_line = block.splitlines()[0]
        for field in required_fields:
            if field == "path":
                has_field = re.search(r'(?m)^\s+- path:', block) is not None
            else:
                has_field = re.search(rf"(?m)^\s+{field}:", block) is not None
            if not has_field:
                errors.append(f"P01-T05 legacy inventory entry missing {field}: {first_line}")
        if "static inventory requires owner review" in block:
            errors.append(f"P01-T05 legacy inventory still has placeholder current_callers: {first_line}")


def _verify_requirement_ledger(errors: list[str]) -> None:
    ledger = _read(REQUIREMENT_LEDGER)
    source_ids = _source_requirement_ids()
    ledger_ids = set(
        re.findall(r"(?m)^\s+- requirement_id:\s*(ARCH-[A-Z]+(?:-[A-Z]+)?-\d{3})\s*$", ledger)
    )
    if source_ids != ledger_ids:
        missing = sorted(source_ids - ledger_ids)
        extra = sorted(ledger_ids - source_ids)
        if missing:
            errors.append(f"requirement ledger missing source ids: {missing[:10]}")
        if extra:
            errors.append(f"requirement ledger has ids not in sources: {extra[:10]}")

    count_match = re.search(r"(?m)^requirement_count:\s*(\d+)\s*$", ledger)
    if not count_match:
        errors.append("requirement ledger missing requirement_count")
    elif int(count_match.group(1)) != len(source_ids):
        errors.append(
            f"requirement_count {count_match.group(1)} does not match source count {len(source_ids)}"
        )

    blocks = _ledger_blocks(ledger)
    missing_reviewer = 0
    missing_reverse_trace = 0
    empty_test_refs = 0
    empty_evidence_refs = 0
    for block in blocks:
        if _field_missing(block, "reviewer"):
            missing_reviewer += 1
        if _field_missing(block, "reverse_trace_refs"):
            missing_reverse_trace += 1
        if _field_list_is_empty(block, "test_ids"):
            empty_test_refs += 1
        if _field_list_is_empty(block, "evidence_refs"):
            empty_evidence_refs += 1

    if missing_reviewer:
        errors.append(f"requirement ledger entries missing reviewer: {missing_reviewer}")
    if missing_reverse_trace:
        errors.append(f"requirement ledger entries missing reverse_trace_refs: {missing_reverse_trace}")
    if empty_test_refs:
        errors.append(f"requirement ledger entries with empty test_ids: {empty_test_refs}")
    if empty_evidence_refs:
        errors.append(f"requirement ledger entries with empty evidence_refs: {empty_evidence_refs}")


def _verify_readiness(errors: list[str]) -> None:
    readiness = _read(PHASE_READINESS)
    for task_id in [f"P01-T{index:02d}" for index in range(1, 7)]:
        if task_id not in readiness:
            errors.append(f"phase-readiness.yaml missing work package {task_id}")
        if re.search(rf"(?s){task_id}:\s*\n\s+state:\s+completed\b", readiness) is None:
            errors.append(f"{task_id} is not completed in phase-readiness.yaml")
    if "coordinator_approval: approved" not in readiness:
        errors.append("PHASE01 coordinator approval is not approved")
    if "may_start_phase02_after_validation: true" not in readiness:
        errors.append("PHASE02 start gate remains closed")

    risks = _read(RISK_REGISTER)
    if re.search(r"\|\s*P0\s*\|", risks) and "unassigned P0: none" not in risks:
        errors.append("program risk register does not explicitly prove no unassigned P0")


def _verify_phase01_evidence(errors: list[str]) -> None:
    evidence_dir = REPO_ROOT / "docs" / "evidence"
    phase01_evidence = sorted(evidence_dir.glob("phase01-*.md"))
    if not phase01_evidence:
        errors.append("docs/evidence has no phase01-*.md reproducible evidence bundle")
        return
    if not P01_T05_EVIDENCE.exists():
        errors.append("P01-T05 evidence missing: docs/evidence/phase01-legacy-bypass-inventory.md")
    else:
        p01_t05 = _read(P01_T05_EVIDENCE).lower()
        for phrase in [
            "current",
            "gap",
            "plan",
            "search commands",
            "result counts",
            "sample findings",
            "artifact hash",
            "guard gaps",
            "provider sdk",
            "cross-owner db writes",
        ]:
            if phrase not in p01_t05:
                errors.append(f"P01-T05 evidence missing reproducibility field: {phrase}")
    combined = "\n".join(_read(path) for path in phase01_evidence)
    for phrase in ["commit", "environment", "command", "result", "artifact hash"]:
        if phrase not in combined.lower():
            errors.append(f"PHASE01 evidence bundle missing reproducibility field: {phrase}")


def verify_phase01_complete_baseline() -> list[str]:
    errors: list[str] = []
    required_paths = [
        PHASE01_FILE,
        PHASE_READINESS,
        REQUIREMENT_LEDGER,
        RISK_REGISTER,
        TEMPORARY_ALLOWLIST,
        *INVENTORY_FILES.values(),
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing PHASE01 artifact: {path.relative_to(REPO_ROOT).as_posix()}")
    if errors:
        return errors

    _verify_work_product_freshness(errors)
    _verify_inventory_coverage(errors)
    _verify_requirement_ledger(errors)
    _verify_readiness(errors)
    _verify_phase01_evidence(errors)
    return errors


def main() -> int:
    errors = verify_phase01_complete_baseline()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE01 complete baseline verification failed.")
        return 1
    print("PHASE01 complete baseline verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
