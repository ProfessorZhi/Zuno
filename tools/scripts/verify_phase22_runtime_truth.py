"""PHASE22 DeepSeek2 runtime truth verifier (detached, fail-closed).

Rejects evidence that violates the PHASE22 truth boundary:

1. canonical manifest chunk count != runtime written chunk count (e.g.
   24 manifest chunks but 35 written);
2. zip-length / identity mismatches (document/chunk counts, chunk id set,
   per-chunk text hashes);
3. corpus receipt visible while knowledge_version_id is empty;
4. per-document (last-document) receipts masquerading as corpus-level;
5. canonical Neo4j path receipt count 0 while anything claims passed;
6. Milvus tenant isolation not exercised (only workspace);
7. duplicate corpus receipt kinds;
8. corpus receipt scope inconsistency (tenant/workspace/kv/content hash);
9. empty index manifest hash in an activation claim;
10. null profile_run_id with RUNTIME_OBSERVED measurement state;
11. zero trace files reported as a passed gold trace scan;
12. adapter-live-smoke receipts used to activate a snapshot;
13. placeholder security gate markers in the harness;
14. placeholder graph port markers in the harness;
15. local credential leakage in evidence.

Any rejection returns a non-zero exit code.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
TRACK_DIR = REPO_ROOT / "docs" / "evidence" / "goal05-phase22-machine-attested-synthetic-regression"
EVIDENCE_DIR = TRACK_DIR / "deepseek2-cc-b34c"

LIVE_EVIDENCE = EVIDENCE_DIR / "live_three_index_visibility_evidence.json"
SNAPSHOT_EVIDENCE = EVIDENCE_DIR / "snapshot_activation_evidence.json"
FOUR_PROFILE_EVIDENCE = EVIDENCE_DIR / "four_profile_runtime_evidence.json"
GOLD_SCAN_EVIDENCE = EVIDENCE_DIR / "gold_isolation_scan.json"
CANONICAL_IR_MANIFEST = TRACK_DIR / "canonical_ir_manifest.json"

PLACEHOLDER_SECURITY_GATE_MARKERS = (
    "class SecurityGate",
    "def authorize(self",
)
PLACEHOLDER_GRAPH_PORT_MARKERS = (
    "graph_entity_anchor=_stable_hash",
    "def graph_neighbor",
    "def graph_path",
    "return []",
    "Based on the retrieved evidence",
    "usage_recorder(lambda usage: None)",
)
KNOWN_LOCAL_CREDENTIALS = (
    "neo4j12345",
    "minioadmin",
    "postgres:postgres@",
    "ZUNO_TEST_NEO4J_PASSWORD=",
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _has_marker(text: str, markers: tuple[str, ...]) -> list[str]:
    return [marker for marker in markers if marker in text]


def verify_runtime_truth() -> list[str]:
    errors: list[str] = []

    # ── Inputs must exist ──────────────────────────────────────────────────
    required = {
        "live evidence": LIVE_EVIDENCE,
        "snapshot evidence": SNAPSHOT_EVIDENCE,
        "four-profile evidence": FOUR_PROFILE_EVIDENCE,
        "gold scan": GOLD_SCAN_EVIDENCE,
        "canonical IR manifest": CANONICAL_IR_MANIFEST,
    }
    for label, path in required.items():
        if not path.exists():
            errors.append(f"missing required evidence: {label} ({path.as_posix()})")
    if errors:
        return errors

    canonical_ir = _read_json(CANONICAL_IR_MANIFEST)
    live = _read_json(LIVE_EVIDENCE)
    snapshot = _read_json(SNAPSHOT_EVIDENCE)
    four_profile = _read_json(FOUR_PROFILE_EVIDENCE)
    gold_scan = _read_json(GOLD_SCAN_EVIDENCE)

    manifest_chunk_count = int(canonical_ir.get("chunk_count") or 0)
    manifest_document_count = int(canonical_ir.get("document_count") or 0)

    # ── 1 + 2: canonical input identity ───────────────────────────────────
    expected_chunk_count = int(live.get("input", {}).get("expected_chunk_count") or 0)
    if expected_chunk_count != manifest_chunk_count:
        errors.append(
            f"1/2: expected_chunk_count {expected_chunk_count} != canonical manifest chunk_count {manifest_chunk_count}"
        )
    if int(live.get("input", {}).get("expected_document_count") or 0) != manifest_document_count:
        errors.append(
            f"1/2: expected_document_count != canonical manifest document_count {manifest_document_count}"
        )
    identity_checks = live.get("input", {}).get("identity_checks", {})
    for check_name in [
        "document_count_equal",
        "chunk_count_equal",
        "chunk_id_set_equal",
        "chunk_hashes_all_equal",
    ]:
        if identity_checks.get(check_name) is not True:
            errors.append(f"2: canonical identity check failed: {check_name}")
    if int(identity_checks.get("chunk_hash_mismatch_count") or 0) != 0:
        errors.append("2: canonical chunk text hashes mismatch the manifest")

    writes = live.get("adapter_smoke", {}).get("writes", {})
    for index_kind in ["elasticsearch", "milvus", "neo4j"]:
        written = int(writes.get(index_kind, {}).get("chunk_count") or 0)
        if written != manifest_chunk_count:
            errors.append(
                f"1: {index_kind} wrote {written} chunks but the canonical manifest has {manifest_chunk_count}"
            )

    # ── 3: visible corpus receipt with empty knowledge_version_id ─────────
    for kind, receipt in live.get("corpus_index_build_receipts", {}).items():
        if receipt.get("visibility_status") == "visible":
            if not str(receipt.get("knowledge_version_id") or "").strip():
                errors.append(f"3: corpus receipt {kind} is visible with empty knowledge_version_id")
            if receipt.get("receipt_scope") != "formal":
                errors.append(f"3: corpus receipt {kind} visible but scope is not formal")
        if receipt.get("knowledge_version_id"):
            errors.append(f"3: corpus receipt {kind} must not carry knowledge_version_id while dependency is blocked")
        if receipt.get("snapshot_eligible") is not False:
            errors.append(f"3: corpus receipt {kind} must keep snapshot_eligible=false while dependency is blocked")

    # ── 4: corpus-level receipts only (never the last document job) ───────
    for kind, receipt in live.get("corpus_index_build_receipts", {}).items():
        if not str(receipt.get("index_build_run_id") or "").strip():
            errors.append(f"4: corpus receipt {kind} missing index_build_run_id")
        if not (
            receipt.get("expected_document_count")
            and receipt.get("expected_chunk_count")
            and receipt.get("observed_document_count")
            and receipt.get("observed_chunk_count")
        ):
            errors.append(f"4: corpus receipt {kind} missing corpus-level counts")
        if "manifests[-1]" in json.dumps(live):
            errors.append("4: evidence still references the last-document receipt pattern")
    if live.get("evidence_kind") != "three_index_adapter_live_smoke":
        errors.append(f"4: live evidence kind must be three_index_adapter_live_smoke, got {live.get('evidence_kind')!r}")

    # ── 5: no overall pass claim without canonical path receipts ──────────
    if "all_visibility_passed" in json.dumps(live):
        errors.append("5: evidence must not claim all_visibility_passed")
    path_receipt_count = int(live.get("adapter_smoke", {}).get("neo4j_paths", {}).get("canonical_path_receipt_count") or 0)
    if path_receipt_count != 0:
        errors.append(f"5: canonical path receipt count must be 0 while knowledge_version_id is blocked, got {path_receipt_count}")
    for label, path_info in live.get("adapter_smoke", {}).get("neo4j_paths", {}).get("path_readbacks", {}).items():
        # While the knowledge_version_id is blocked every path query must be
        # REJECTED (fail closed) — never executed and never "visible".
        if path_info.get("rejected") is not True:
            errors.append(f"5: neo4j path {label} must be rejected while kv is blocked")
        if path_info.get("query_executed") is True:
            errors.append(f"5: neo4j path {label} executed an unscoped query")

    # ── 6: Milvus tenant isolation exercised (fail-closed matrix) ─────────
    milvus_matrix = live.get("adapter_smoke", {}).get("scope_matrix", {}).get("milvus", {}).get("matrix", {})
    if "same_workspace_different_tenant" not in milvus_matrix:
        errors.append("6: Milvus scope matrix missing same_workspace_different_tenant")
    else:
        entry = milvus_matrix.get("same_workspace_different_tenant")
        if entry.get("query_executed") is not True or entry.get("result") != 0:
            errors.append(f"6: Milvus same-workspace-different-tenant must execute and return 0 rows, got {entry!r}")
    for key in ["same_tenant_different_workspace", "same_tenant_workspace_different_kv", "foreign_snapshot_scope"]:
        entry = milvus_matrix.get(key)
        if entry is None:
            errors.append(f"6: Milvus scope matrix missing {key}")
        elif entry.get("query_executed") is not True or entry.get("result") != 0:
            errors.append(f"6: Milvus {key} must execute and return 0 rows, got {entry!r}")
    if live.get("adapter_smoke", {}).get("scope_matrix", {}).get("milvus", {}).get("injection_contained") is not True:
        errors.append("6: Milvus expr injection attempt must be contained")

    # ── 7 + 8: unique receipt kinds and consistent scope ──────────────────
    corpus_receipts = live.get("corpus_index_build_receipts", {})
    if not isinstance(corpus_receipts, dict):
        errors.append("7: corpus_index_build_receipts must be an object keyed by index kind")
    elif len(corpus_receipts) != 3:
        errors.append(f"7: expected exactly 3 corpus receipts, got {len(corpus_receipts)}")
    else:
        scopes = {
            kind: (
                receipt.get("tenant_id"),
                receipt.get("workspace_id"),
                receipt.get("knowledge_version_id"),
                receipt.get("content_set_hash"),
                receipt.get("config_hash"),
            )
            for kind, receipt in corpus_receipts.items()
        }
        if len({scope for scope in scopes.values()}) != 1:
            errors.append(f"8: corpus receipt scope inconsistent across kinds: {scopes}")

    # ── 9: non-empty index manifest hash on activation claims ─────────────
    if snapshot.get("activation_status") != "NOT_RUN_DEPENDENCY_BLOCKED":
        if not str(snapshot.get("scope", {}).get("index_job_manifest_hash") or "").strip():
            errors.append("9: activation claim with empty index_job_manifest_hash")
    if not str(snapshot.get("scope", {}).get("index_job_manifest_hash") or "").strip():
        errors.append("9: snapshot evidence missing index_job_manifest_hash")

    # ── 10: no RUNTIME_OBSERVED without profile runs ──────────────────────
    for profile_id, block in four_profile.get("per_profile", {}).items():
        if block.get("measurement_status") == "RUNTIME_OBSERVED" and block.get("profile_run_id") is None:
            errors.append(f"10: profile {profile_id} claims RUNTIME_OBSERVED with null profile_run_id")
    if four_profile.get("status") != "FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED":
        errors.append(f"10: four-profile status must be FOUR_PROFILE_RUNTIME_NOT_RUN_DEPENDENCY_BLOCKED, got {four_profile.get('status')!r}")
    if four_profile.get("profile_run_ids") != []:
        errors.append("10: profile_run_ids must stay empty while dependency blocked")
    for profile_id, block in four_profile.get("per_profile", {}).items():
        if block.get("measurement_status") != "BLOCKED":
            errors.append(f"10: profile {profile_id} must be BLOCKED while dependency blocked")

    # ── 11: zero trace files cannot be a passed gold trace scan ───────────
    trace_file_count = int(gold_scan.get("trace_scan_file_count") or 0)
    trace_status = gold_scan.get("trace_gold_isolation_status")
    if trace_file_count == 0:
        if trace_status != "NOT_RUN_DEPENDENCY_BLOCKED":
            errors.append(f"11: zero trace files must yield trace_gold_isolation_status NOT_RUN_DEPENDENCY_BLOCKED, got {trace_status!r}")
        if gold_scan.get("scan_passed") is not False:
            errors.append("11: zero trace files must not be reported as a full gold-scan pass")
    if gold_scan.get("request_forbidden_field_count") != 0:
        errors.append(f"11: runtime request gold forbidden fields must be 0, got {gold_scan.get('request_forbidden_field_count')}")

    # ── 12: smoke receipts can never activate a snapshot ──────────────────
    if snapshot.get("activation_status") == "ACTIVATED":
        errors.append("12: snapshot activation must not be ACTIVE while DeepSeek1 dependency is not accepted")
    if snapshot.get("snapshot_id") is not None:
        errors.append("12: snapshot_id must be null while dependency is blocked")
    if snapshot.get("activation_status") != "NOT_RUN_DEPENDENCY_BLOCKED":
        errors.append(f"12: snapshot activation status must be NOT_RUN_DEPENDENCY_BLOCKED, got {snapshot.get('activation_status')!r}")
    if snapshot.get("dependency", {}).get("dependency_accepted") is not False:
        errors.append("12: dependency_accepted must be false while DeepSeek1 PR is REQUEST_WORKER_CHANGES")

    # ── 1-8: ACTIVATED evidence would have to prove the persistence gate ──
    # (the evidence must remain blocked this round, so an ACTIVATED claim is
    # rejected outright; the gate itself is enforced by unit tests).
    activation_evidence = snapshot.get("activation_receipt", {})
    if activation_evidence.get("activation_status") == "ACTIVATED":
        errors.append("1: evidence claims ACTIVATED while dependency is blocked")
    for check_name in ["consistency_checks", "provided_corpus_receipt_kinds"]:
        if activation_evidence.get(check_name) is None:
            errors.append(f"8: activation receipt missing {check_name}")

    # ── 9: no unscoped query may have been executed ───────────────────────
    for index_kind, scope_block in live.get("adapter_smoke", {}).get("scope_matrix", {}).items():
        matrix = scope_block.get("matrix", {})
        for entry_name in ["missing_scope", "empty_scope", "same_tenant_workspace_kv"]:
            entry = matrix.get(entry_name)
            if entry is None:
                errors.append(f"9: scope matrix {index_kind} missing {entry_name}")
                continue
            if entry.get("query_executed") is True:
                errors.append(f"9: {index_kind} {entry_name} executed an unscoped query")
            if entry.get("rejected") is not True:
                errors.append(f"9: {index_kind} {entry_name} must be recorded as rejected")
        for entry_name in [
            "same_workspace_different_tenant",
            "same_tenant_different_workspace",
            "same_tenant_workspace_different_kv",
            "foreign_snapshot_scope",
        ]:
            entry = matrix.get(entry_name)
            if entry is None:
                errors.append(f"9: scope matrix {index_kind} missing {entry_name}")
            elif entry.get("query_executed") is not True or entry.get("result") != 0:
                errors.append(f"9: {index_kind} {entry_name} must execute and return 0 rows, got {entry!r}")

    # ── 10: source manifest must be validated ─────────────────────────────
    identity_checks = live.get("input", {}).get("identity_checks", {})
    for check_name in [
        "source_count_8",
        "source_paths_exist",
        "source_hashes_match",
        "documents_one_to_one",
        "chunk_documents_exist",
        "source_manifest_hash_valid",
        "canonical_ir_binds_source_manifest",
        "corpus_files_exact",
        "document_count_equal",
        "chunk_count_equal",
        "chunk_id_set_equal",
        "chunk_hashes_all_equal",
    ]:
        if identity_checks.get(check_name) is not True:
            errors.append(f"10: canonical identity check failed: {check_name}")

    # ── 11: five hash identities recorded separately ──────────────────────
    input_hashes = live.get("input", {})
    for hash_name in [
        "dataset_corpus_hash",
        "source_manifest_hash",
        "canonical_ir_hash",
        "content_set_hash",
        "embedding_config_hash",
    ]:
        if not str(input_hashes.get(hash_name) or "").strip():
            errors.append(f"11: evidence missing separated hash field {hash_name}")
    distinct_hashes = {input_hashes.get(name) for name in [
        "dataset_corpus_hash",
        "source_manifest_hash",
        "canonical_ir_hash",
        "content_set_hash",
        "embedding_config_hash",
    ]}
    if len(distinct_hashes) != 5:
        errors.append("11: the five hash identities must be distinct (conflation detected)")

    # ── 12b: dependency head must be the current PR #112 candidate ────────
    for evidence in (snapshot, four_profile):
        dependency_head = evidence.get("dependency", {}).get("dependency_head_sha")
        if dependency_head == "bf4b2cb11b53e78b3a7242df5996e4aed2cc1a4b":
            errors.append("12b: evidence still records the stale DeepSeek1 head bf4b2cb1")
        if dependency_head != "ce495af2a39c01379878a9e2c1bb58d876456b1e":
            errors.append(f"12b: dependency_head_sha must be the current candidate ce495af2…, got {dependency_head!r}")
        if evidence.get("dependency", {}).get("dependency_pr") != "112":
            errors.append("12b: dependency_pr must be 112")

    # ── 14: no measurement success with null profile runs ─────────────────
    for profile_id, block in four_profile.get("per_profile", {}).items():
        if block.get("measurement_status") == "MEASURED" and block.get("profile_run_id") is None:
            errors.append(f"14: profile {profile_id} claims MEASURED with null profile_run_id")

    # ── 15: no CI Passed claim without CI ─────────────────────────────────
    for path in [LIVE_EVIDENCE, SNAPSHOT_EVIDENCE, FOUR_PROFILE_EVIDENCE]:
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if "ci_passed" in lowered or "ci passed" in lowered or "github_actions_passed" in lowered:
            errors.append(f"15: evidence claims CI Passed without CI: {path.name}")

    # ── 13 + 14: placeholder runtime markers in the harness ───────────────
    harness_path = REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval" / "run_phase22_four_profile_benchmark.py"
    if harness_path.exists():
        source = harness_path.read_text(encoding="utf-8")
        hits = _has_marker(source, PLACEHOLDER_SECURITY_GATE_MARKERS)
        if hits:
            errors.append(f"13: placeholder security gate markers present in harness: {hits}")
        hits = _has_marker(source, PLACEHOLDER_GRAPH_PORT_MARKERS)
        if hits:
            errors.append(f"14: placeholder graph port markers present in harness: {hits}")

    # ── 15: local credential leakage in evidence ──────────────────────────
    for path in [LIVE_EVIDENCE, SNAPSHOT_EVIDENCE, FOUR_PROFILE_EVIDENCE, GOLD_SCAN_EVIDENCE]:
        text = path.read_text(encoding="utf-8")
        for credential in KNOWN_LOCAL_CREDENTIALS:
            if credential in text:
                errors.append(f"15: credential leakage in {path.name}: {credential}")

    return errors


def main() -> int:
    errors = verify_runtime_truth()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PHASE22 DeepSeek2 runtime truth boundary passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
