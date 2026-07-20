from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY = REPO_ROOT / ".agent/programs/work-products/phase11-legacy-upload-parser-cutover-inventory.md"
MATRIX = REPO_ROOT / ".agent/programs/work-products/goal01-closure-matrix.md"

EXPECTED_ROWS = {
    "P11-LC-01": {
        "path": "src/backend/zuno/api/v1/upload.py",
        "status": "not_phase11_ingestion",
    },
    "P11-LC-02": {
        "path": "src/backend/zuno/platform/services/workspace/attachment_service.py",
        "status": "legacy_active_default",
    },
    "P11-LC-03": {
        "path": "src/backend/zuno/platform/services/pipeline/manager.py",
        "status": "legacy_active_default",
    },
    "P11-LC-04": {
        "path": "src/backend/zuno/platform/services/rag/parser.py",
        "status": "versioned_adapter_required",
    },
    "P11-LC-05": {
        "path": "src/backend/zuno/knowledge/ingestion/gateway.py",
        "status": "canonical_runtime_candidate",
    },
    "P11-LC-06": {
        "path": "src/backend/zuno/knowledge/ingestion/async_runtime.py",
        "status": "canonical_runtime_candidate",
    },
}

SOURCE_EXPECTATIONS = {
    "src/backend/zuno/platform/services/workspace/attachment_service.py": [
        "doc_parser.parse_doc_into_chunks",
        "_image_to_text",
    ],
    "src/backend/zuno/platform/services/pipeline/manager.py": [
        "doc_parser.parse_doc_into_chunks",
        "run_rag_index_stage",
        "run_graph_stage",
    ],
    "src/backend/zuno/platform/services/rag/parser.py": [
        "ChunkModel",
        "parse_doc_into_chunks",
    ],
    "src/backend/zuno/knowledge/ingestion/gateway.py": [
        "CanonicalDocumentIR",
        "ParseJobSnapshot",
        "ParseGateway",
    ],
    "src/backend/zuno/knowledge/ingestion/async_runtime.py": [
        "LocalQueueBackend",
        "SQLiteDurableIngestionStore",
        "LocalObjectStore",
    ],
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _matrix_legacy_cutover_row(matrix: str) -> str:
    for line in matrix.splitlines():
        if line.startswith("| Legacy upload/parser Cutover |"):
            return line
    return ""


def verify_phase11_legacy_upload_parser_cutover() -> list[str]:
    errors: list[str] = []
    if not INVENTORY.exists():
        return [f"missing inventory: {INVENTORY.relative_to(REPO_ROOT).as_posix()}"]
    if not MATRIX.exists():
        return [f"missing matrix: {MATRIX.relative_to(REPO_ROOT).as_posix()}"]

    inventory = _read(INVENTORY)
    matrix = _read(MATRIX)

    for row_id, expected in EXPECTED_ROWS.items():
        if row_id not in inventory:
            errors.append(f"inventory missing row id: {row_id}")
        if expected["path"] not in inventory:
            errors.append(f"inventory missing path for {row_id}: {expected['path']}")
        if expected["status"] not in inventory:
            errors.append(f"inventory missing classification for {row_id}: {expected['status']}")
        if "| `target_not_current` |" not in inventory:
            errors.append("inventory must keep reopened rows target_not_current")
            break

    for relative_path, required_terms in SOURCE_EXPECTATIONS.items():
        path = REPO_ROOT / relative_path
        if not path.exists():
            errors.append(f"expected active source path missing: {relative_path}")
            continue
        text = _read(path)
        for term in required_terms:
            if term not in text:
                errors.append(f"{relative_path} missing expected active cutover term: {term}")

    for required_phrase in [
        "PHASE11 仍为 `in_progress`",
        "legacy_active_default",
        "versioned_adapter_required",
        "not_phase11_ingestion",
        "canonical_runtime_candidate",
        "不得作为 PHASE11 完成证据",
        "不得用 SQLite/LocalQueue 关闭生产 durable ingestion",
    ]:
        if required_phrase not in inventory:
            errors.append(f"inventory missing governance phrase: {required_phrase}")

    row = _matrix_legacy_cutover_row(matrix)
    if not row:
        errors.append("Goal01 matrix missing Legacy upload/parser Cutover row")
    else:
        if "`target_not_current`" not in row:
            errors.append("Goal01 matrix Legacy upload/parser Cutover row must remain target_not_current")
        if "cutover inventory" not in row:
            errors.append("Goal01 matrix Legacy upload/parser Cutover row must reference cutover inventory evidence")

    return errors


def main() -> int:
    errors = verify_phase11_legacy_upload_parser_cutover()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE11 legacy upload/parser cutover verification failed.")
        return 1
    print("PHASE11 legacy upload/parser cutover verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
