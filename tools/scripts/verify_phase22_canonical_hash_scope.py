"""PHASE22 canonical hash and scope companion gate.

This is a read-only, fail-closed companion gate for PR #112
``claude/deepseek1-phase22-canonical-ingestion``. It enforces two
contracts on the official manifests:

Hash contract
  - The frozen ``source_manifest_hash``, ``canonical_ir_hash``, and the
    ``corpus_hash`` field of the runtime request manifest (a.k.a.
    ``dataset_corpus_hash``) are each read from their own canonical
    manifest and **must** be distinct.
  - Aliasing is rejected: an evidence or runtime payload that names
    ``source_manifest_hash`` in a field whose declared semantic is
    ``dataset_corpus_hash`` is a hard contract violation.
  - Each canonical manifest must independently carry the field; missing,
    empty, wrong-length, or wrong-value entries all fail closed.
  - The verifier must also be able to **point at** the field source so
    the evidence cannot hide where the hash was read from.

Scope contract
  - The official scope is ``tenant_auroralis`` + ``workspace_regression``
    only. The verification tenant/workspace (``tenant_auroralis_verify``,
    ``workspace_regression_verify``) is allowed only inside an explicit
    isolation envelope (independent DB / schema / compose project) and
    may never be mixed with the official scope in the same payload.
  - KnowledgeVersion, KnowledgeSpace, security-decision, and database
    column scopes must all be self-consistent.

Modes
  - ``--mode contract`` exercises a fixed fixture suite; this mode MUST
    exit ``0`` when the suite is healthy.
  - ``--mode repository`` reads PR #112's current manifests and evidence
    and reports the truth. It may legitimately exit non-zero (hash or
    scope violation) — the gate must never lower its standards to force
    a pass.

Exit codes
  - 0  CANONICAL_HASH_SCOPE_CONFIRMED
  - 2  HASH_CONTRACT_VIOLATION
  - 3  SCOPE_CONTRACT_VIOLATION
  - 4  IDENTITY_UNRESOLVED  (manifests missing or unparseable)
  - 5  TOOL_ERROR           (verifier bug)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

# --- Frozen expectations ----------------------------------------------------

# The three frozen hashes read directly from the official manifests. The
# verifier compares whatever the manifests declare against these values.
EXPECTED_SOURCE_MANIFEST_HASH = (
    "0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a"
)
EXPECTED_CANONICAL_IR_HASH = (
    "43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6"
)
# ``corpus_hash`` field of the runtime request manifest. This is the
# ``dataset_corpus_hash`` referenced by the CC-D task card.
EXPECTED_DATASET_CORPUS_HASH = (
    "749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4"
)

# The official scope tuple. The verifier must never accept ``*_verify``
# mixed with the official scope in the same payload.
OFFICIAL_TENANT = "tenant_auroralis"
OFFICIAL_WORKSPACE = "workspace_regression"
VERIFICATION_TENANT = "tenant_auroralis_verify"
VERIFICATION_WORKSPACE = "workspace_regression_verify"
ALLOWED_SCOPES: frozenset[str] = frozenset(
    {OFFICIAL_TENANT, VERIFICATION_TENANT}
)
ALLOWED_WORKSPACES: frozenset[str] = frozenset(
    {OFFICIAL_WORKSPACE, VERIFICATION_WORKSPACE}
)

# Repository-relative manifest paths the verifier reaches into.
SOURCE_UPLOAD_MANIFEST_REPO = (
    "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/source_upload_manifest.json"
)
CANONICAL_IR_MANIFEST_REPO = (
    "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/canonical_ir_manifest.json"
)
RUNTIME_REQUEST_MANIFEST_REPO = (
    "docs/evidence/goal05-phase22-machine-attested-synthetic-regression/runtime_request_manifest.json"
)


# --- Status enum ------------------------------------------------------------


@dataclass
class VerifierResult:
    status: str
    exit_code: int
    detected_hashes: dict[str, dict[str, str]] = field(default_factory=dict)
    detected_scope: dict[str, list[str]] = field(default_factory=dict)
    violations: list[dict[str, str]] = field(default_factory=list)
    not_proven_boundary: list[str] = field(default_factory=list)
    base_sha: str | None = None
    repository_status: str | None = None


# --- Utility helpers --------------------------------------------------------


_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _is_hex_64(value: str) -> bool:
    return bool(_HEX_64.match(value or ""))


def _find_field(
    payload: dict[str, Any], field: str
) -> tuple[Any | None, str | None]:
    """Return ``(value, path)`` for the first matching field, or ``(None, None)``.

    Walks the payload one level deep for the requested field name so the
    verifier can record exactly where the hash was read from.
    """

    if field in payload:
        return payload[field], f"$.{field}"
    for prefix in ("canonical_ir_manifest", "source_upload_manifest"):
        nested = payload.get(prefix)
        if isinstance(nested, dict) and field in nested:
            return nested[field], f"$.{prefix}.{field}"
    return None, None


def _collect_scope_strings(payload: dict[str, Any]) -> list[tuple[str, str, str]]:
    """Walk a payload and collect every ``tenant_id`` / ``workspace_id`` value
    along with its JSON path."""

    found: list[tuple[str, str, str]] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in {"tenant_id", "workspace_id", "tenant", "workspace"} and isinstance(value, str):
                    found.append((key, value, path + "." + key))
                walk(value, path + "." + str(key))
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, path + f"[{i}]")

    walk(payload, "$")
    return found


def _classify_scope_strings(
    scope_strings: list[tuple[str, str, str]],
) -> tuple[set[str], set[str]]:
    tenants = {value for key, value, _ in scope_strings if key in {"tenant_id", "tenant"}}
    workspaces = {value for key, value, _ in scope_strings if key in {"workspace_id", "workspace"}}
    return tenants, workspaces


def _record_violation(
    result: VerifierResult,
    *,
    kind: str,
    detail: str,
    field_source: str | None = None,
    observed: Any | None = None,
    expected: Any | None = None,
) -> None:
    result.violations.append(
        {
            "kind": kind,
            "detail": detail,
            "field_source": field_source or "",
            "observed": "" if observed is None else str(observed),
            "expected": "" if expected is None else str(expected),
        }
    )


# --- Hash contract ----------------------------------------------------------


HASH_FIELD_BINDINGS: dict[str, str] = {
    EXPECTED_SOURCE_MANIFEST_HASH: "source_upload_manifest.json:source_manifest_hash",
    EXPECTED_CANONICAL_IR_HASH: "canonical_ir_manifest.json:canonical_ir_hash",
    EXPECTED_DATASET_CORPUS_HASH: "runtime_request_manifest.json:corpus_hash",
}


def _enforce_hash_contract(
    result: VerifierResult,
    *,
    source_upload_manifest: dict[str, Any] | None,
    canonical_ir_manifest: dict[str, Any] | None,
    runtime_request_manifest: dict[str, Any] | None,
) -> bool:
    """Return True if the hash contract holds. ``False`` means a violation."""

    if not source_upload_manifest:
        _record_violation(
            result,
            kind="HASH_CONTRACT_VIOLATION",
            detail="source_upload_manifest.json missing or unparseable",
            field_source=SOURCE_UPLOAD_MANIFEST_REPO,
        )
        return False
    if not canonical_ir_manifest:
        _record_violation(
            result,
            kind="HASH_CONTRACT_VIOLATION",
            detail="canonical_ir_manifest.json missing or unparseable",
            field_source=CANONICAL_IR_MANIFEST_REPO,
        )
        return False
    if not runtime_request_manifest:
        _record_violation(
            result,
            kind="HASH_CONTRACT_VIOLATION",
            detail="runtime_request_manifest.json missing or unparseable",
            field_source=RUNTIME_REQUEST_MANIFEST_REPO,
        )
        return False

    sm_value, sm_path = _find_field(source_upload_manifest, "source_manifest_hash")
    cir_value, cir_path = _find_field(canonical_ir_manifest, "canonical_ir_hash")
    corpus_value, corpus_path = _find_field(
        runtime_request_manifest, "corpus_hash"
    )

    result.detected_hashes["source_manifest_hash"] = {
        "value": "" if sm_value is None else str(sm_value),
        "field_source": sm_path or "",
    }
    result.detected_hashes["canonical_ir_hash"] = {
        "value": "" if cir_value is None else str(cir_value),
        "field_source": cir_path or "",
    }
    result.detected_hashes["dataset_corpus_hash"] = {
        "value": "" if corpus_value is None else str(corpus_value),
        "field_source": corpus_path or "",
    }

    ok = True

    # 1. Independent reads.
    for field_name, value, source, expected in (
        ("source_manifest_hash", sm_value, sm_path, EXPECTED_SOURCE_MANIFEST_HASH),
        (
            "canonical_ir_hash",
            cir_value,
            cir_path,
            EXPECTED_CANONICAL_IR_HASH,
        ),
        ("dataset_corpus_hash", corpus_value, corpus_path, EXPECTED_DATASET_CORPUS_HASH),
    ):
        if value is None:
            _record_violation(
                result,
                kind="HASH_CONTRACT_VIOLATION",
                detail=f"{field_name} missing in canonical manifest",
                field_source=source or "",
            )
            ok = False
            continue
        if not isinstance(value, str) or not _is_hex_64(value):
            _record_violation(
                result,
                kind="HASH_CONTRACT_VIOLATION",
                detail=f"{field_name} is not a 64-char lowercase hex string",
                field_source=source or "",
                observed=value,
            )
            ok = False
            continue
        if value != expected:
            _record_violation(
                result,
                kind="HASH_CONTRACT_VIOLATION",
                detail=f"{field_name} does not match frozen value",
                field_source=source or "",
                observed=value,
                expected=expected,
            )
            ok = False

    # 2. Distinctness.
    values = {
        EXPECTED_SOURCE_MANIFEST_HASH: sm_value,
        EXPECTED_CANONICAL_IR_HASH: cir_value,
        EXPECTED_DATASET_CORPUS_HASH: corpus_value,
    }
    if len(set(values.values())) != len(values):
        # Find which ones collide.
        seen: dict[str, str] = {}
        collisions: list[str] = []
        for label, value in values.items():
            if value in seen and seen[value] != label:
                collisions.append(f"{label} == {seen[value]} == {value}")
            seen[value] = label
        _record_violation(
            result,
            kind="HASH_CONTRACT_VIOLATION",
            detail="two or more canonical hashes are equal (aliasing forbidden)",
            field_source=",".join(HASH_FIELD_BINDINGS.values()),
            observed="; ".join(collisions),
        )
        ok = False

    # 3. Aliasing inside evidence. Reject any payload field whose name
    # matches one hash but whose value is bound to the field source of a
    # different hash.
    for label, hash_value in values.items():
        if hash_value is None:
            continue
        for payload_name, payload in (
            ("source_upload_manifest", source_upload_manifest),
            ("canonical_ir_manifest", canonical_ir_manifest),
            ("runtime_request_manifest", runtime_request_manifest),
        ):
            for field_name, declared_value in payload.items():
                if not isinstance(declared_value, str):
                    continue
                if field_name == HASH_FIELD_BINDINGS[hash_value].split(":")[-1]:
                    continue
                if declared_value == hash_value:
                    # This field carries a hash that belongs to a
                    # different canonical key. That is aliasing.
                    _record_violation(
                        result,
                        kind="HASH_CONTRACT_VIOLATION",
                        detail=(
                            f"{payload_name}.{field_name} carries the value "
                            f"of {label} ({hash_value[:16]}...) — aliasing"
                        ),
                        field_source=f"$.{payload_name}.{field_name}",
                        observed=declared_value,
                        expected=label,
                    )
                    ok = False

    return ok


# --- Scope contract ---------------------------------------------------------


def _enforce_scope_contract(
    result: VerifierResult,
    *,
    source_upload_manifest: dict[str, Any],
    canonical_ir_manifest: dict[str, Any],
    runtime_request_manifest: dict[str, Any],
) -> bool:
    """Return True if the scope contract holds. ``False`` means violation."""

    ok = True
    tenants: set[str] = set()
    workspaces: set[str] = set()
    for label, payload in (
        ("source_upload_manifest", source_upload_manifest),
        ("canonical_ir_manifest", canonical_ir_manifest),
        ("runtime_request_manifest", runtime_request_manifest),
    ):
        if not isinstance(payload, dict):
            continue
        strings = _collect_scope_strings(payload)
        local_tenants, local_workspaces = _classify_scope_strings(strings)
        tenants.update(local_tenants)
        workspaces.update(local_workspaces)
        result.detected_scope[label] = [
            f"{key}={value}@{path}" for key, value, path in strings
        ]

    # Allowed scope set check.
    unknown_tenants = tenants - ALLOWED_SCOPES
    unknown_workspaces = workspaces - ALLOWED_WORKSPACES
    for value in sorted(unknown_tenants):
        _record_violation(
            result,
            kind="SCOPE_CONTRACT_VIOLATION",
            detail=f"unknown tenant_id {value!r}; allowed={sorted(ALLOWED_SCOPES)}",
            field_source="$.*",
            observed=value,
        )
        ok = False
    for value in sorted(unknown_workspaces):
        _record_violation(
            result,
            kind="SCOPE_CONTRACT_VIOLATION",
            detail=f"unknown workspace_id {value!r}; allowed={sorted(ALLOWED_WORKSPACES)}",
            field_source="$.*",
            observed=value,
        )
        ok = False

    # Mixing official and verification scopes in the same payload is
    # rejected. We allow official scope in every payload; verification
    # scope is only allowed in payloads that contain *only* verification
    # scope (i.e., no official scope in the same manifest).
    official_tenants = tenants & {OFFICIAL_TENANT}
    verify_tenants = tenants & {VERIFICATION_TENANT}
    if official_tenants and verify_tenants:
        _record_violation(
            result,
            kind="SCOPE_CONTRACT_VIOLATION",
            detail=(
                f"manifests mix official tenant ({OFFICIAL_TENANT}) with "
                f"verification tenant ({VERIFICATION_TENANT}); isolation "
                "broken"
            ),
            field_source="$.*",
            observed=f"official={sorted(official_tenants)} verify={sorted(verify_tenants)}",
        )
        ok = False
    official_workspaces = workspaces & {OFFICIAL_WORKSPACE}
    verify_workspaces = workspaces & {VERIFICATION_WORKSPACE}
    if official_workspaces and verify_workspaces:
        _record_violation(
            result,
            kind="SCOPE_CONTRACT_VIOLATION",
            detail=(
                f"manifests mix official workspace ({OFFICIAL_WORKSPACE}) with "
                f"verification workspace ({VERIFICATION_WORKSPACE}); isolation "
                "broken"
            ),
            field_source="$.*",
            observed=f"official={sorted(official_workspaces)} verify={sorted(verify_workspaces)}",
        )
        ok = False

    # KnowledgeVersion scope must match the database column scope.
    # The frozen KnowledgeVersion format is
    # ``knowledge-version:<tenant>:<workspace>:...:phase22-synthetic:<n>``.
    # We extract any knowledge_version_id we find and confirm its tenant
    # and workspace fragments match the manifest scopes.
    for label, payload in (
        ("source_upload_manifest", source_upload_manifest),
        ("canonical_ir_manifest", canonical_ir_manifest),
        ("runtime_request_manifest", runtime_request_manifest),
    ):
        kv_id = payload.get("knowledge_version_id") if isinstance(payload, dict) else None
        if not kv_id or not isinstance(kv_id, str):
            continue
        kv_uses_verify = (
            VERIFICATION_TENANT in kv_id or VERIFICATION_WORKSPACE in kv_id
        )
        kv_uses_official = (
            OFFICIAL_TENANT in kv_id or OFFICIAL_WORKSPACE in kv_id
        )
        # knowledge_version_id encodes an unknown tenant.
        if not kv_uses_verify and not kv_uses_official:
            _record_violation(
                result,
                kind="SCOPE_CONTRACT_VIOLATION",
                detail=(
                    f"{label}.knowledge_version_id does not encode any "
                    "allowed tenant scope"
                ),
                field_source=f"$.{label}.knowledge_version_id",
                observed=kv_id,
            )
            ok = False
            continue
        # knowledge_version_id uses verification scope but the manifest's
        # declared scopes[] only carries the official scope (or vice-versa).
        # That is a scope identity mismatch.
        payload_tenants, payload_workspaces = _classify_scope_strings(
            _collect_scope_strings(payload)
        )
        if kv_uses_verify and not (
            VERIFICATION_TENANT in payload_tenants
            or VERIFICATION_WORKSPACE in payload_workspaces
        ):
            _record_violation(
                result,
                kind="SCOPE_CONTRACT_VIOLATION",
                detail=(
                    f"{label}.knowledge_version_id encodes verification "
                    "scope but manifest scopes[] do not"
                ),
                field_source=f"$.{label}.knowledge_version_id",
                observed=kv_id,
            )
            ok = False

    return ok


# --- Contract fixtures ------------------------------------------------------


FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "fixtures"
    / "phase22_canonical_hash_scope"
)


def _expected_hashes_match(payload: dict[str, Any]) -> bool:
    """Return True if a fixture payload matches the frozen expectations."""

    if payload.get("source_manifest_hash") != EXPECTED_SOURCE_MANIFEST_HASH:
        return False
    if payload.get("canonical_ir_hash") != EXPECTED_CANONICAL_IR_HASH:
        return False
    if payload.get("dataset_corpus_hash") != EXPECTED_DATASET_CORPUS_HASH:
        return False
    return True


def _expected_scope_official(payload: dict[str, Any]) -> bool:
    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list):
        return False
    tenants = {s.get("tenant_id") for s in scopes if isinstance(s, dict)}
    workspaces = {s.get("workspace_id") for s in scopes if isinstance(s, dict)}
    return (
        tenants == {OFFICIAL_TENANT}
        and workspaces == {OFFICIAL_WORKSPACE}
    )


def _run_contract_mode() -> VerifierResult:
    """Run the fixed fixture suite and return a VerifierResult."""

    result = VerifierResult(
        status="CANONICAL_HASH_SCOPE_CONFIRMED", exit_code=0
    )

    fixtures_dir = FIXTURES_DIR
    if not fixtures_dir.exists():
        result.status = "TOOL_ERROR"
        result.exit_code = 5
        result.violations.append(
            {
                "kind": "TOOL_ERROR",
                "detail": f"fixture directory missing: {fixtures_dir}",
                "field_source": "",
                "observed": "",
                "expected": "",
            }
        )
        return result

    summary: dict[str, int] = {"passed": 0, "failed": 0}
    failures: list[dict[str, str]] = []

    expected_outcomes = _load_expected_outcomes(fixtures_dir)
    for fixture_path in sorted(fixtures_dir.glob("[0-9][0-9]_*.json")):
        name = fixture_path.stem
        expected = expected_outcomes.get(name, {})
        payload = _read_json(fixture_path)
        if payload is None:
            summary["failed"] += 1
            failures.append(
                {"fixture": name, "reason": "unparseable JSON"}
            )
            continue

        observed_kind, observed_detail = _classify_fixture(payload)
        expected_kind = expected.get("expected_status_kind", "CANONICAL_HASH_SCOPE_CONFIRMED")
        if observed_kind == expected_kind:
            summary["passed"] += 1
        else:
            summary["failed"] += 1
            failures.append(
                {
                    "fixture": name,
                    "expected_kind": expected_kind,
                    "observed_kind": observed_kind,
                    "observed_detail": observed_detail,
                }
            )

    if summary["failed"] > 0:
        result.status = "HASH_CONTRACT_VIOLATION" if any(
            "HASH" in f.get("observed_kind", "") for f in failures
        ) else "SCOPE_CONTRACT_VIOLATION"
        result.exit_code = (
            2 if result.status == "HASH_CONTRACT_VIOLATION" else 3
        )
        for failure in failures:
            _record_violation(
                result,
                kind="HASH_CONTRACT_VIOLATION"
                if "HASH" in failure.get("observed_kind", "")
                else "SCOPE_CONTRACT_VIOLATION",
                detail=(
                    f"fixture {failure['fixture']!r} expected "
                    f"{failure.get('expected_kind')!r}, got "
                    f"{failure.get('observed_kind')!r} ({failure.get('observed_detail')})"
                ),
                field_source=failure["fixture"],
            )

    result.detected_scope["_contract_summary"] = [
        f"passed={summary['passed']}",
        f"failed={summary['failed']}",
    ]
    return result


def _load_expected_outcomes(fixtures_dir: Path) -> dict[str, dict[str, str]]:
    """Load per-fixture expected outcomes from ``expected_outcomes.json``."""

    path = fixtures_dir / "expected_outcomes.json"
    if not path.exists():
        return {}
    data = _read_json(path)
    if not isinstance(data, dict):
        return {}
    return data


def _is_isolated_envelope(payload: dict[str, Any]) -> bool:
    """Return True if the payload declares an independent isolation envelope.

    Isolation is allowed only when every dimension (database, schema,
    compose project) is explicitly marked as independent.
    """

    isolation = payload.get("isolation")
    if not isinstance(isolation, dict):
        return False
    return all(
        isolation.get(key) == "independent"
        for key in ("database", "schema", "compose_project")
    )


def _classify_fixture(payload: dict[str, Any]) -> tuple[str, str]:
    """Classify a fixture payload into a status kind + detail.

    The fixture schema:
      - ``source_manifest_hash`` (string or null)
      - ``canonical_ir_hash`` (string or null)
      - ``dataset_corpus_hash`` (string or null)
      - ``scopes`` (list of {tenant_id, workspace_id, ...})
      - ``knowledge_version_id`` (optional string)
      - ``isolation`` (optional dict with database/schema/compose_project)
    """

    sm = payload.get("source_manifest_hash")
    cir = payload.get("canonical_ir_hash")
    corpus = payload.get("dataset_corpus_hash")

    # If any hash is None or empty -> HASH_CONTRACT_VIOLATION.
    for name, value in (
        ("source_manifest_hash", sm),
        ("canonical_ir_hash", cir),
        ("dataset_corpus_hash", corpus),
    ):
        if value is None or value == "":
            return "HASH_CONTRACT_VIOLATION", f"{name} missing/empty"

    # If any hash is not a 64-char lowercase hex string -> HASH_CONTRACT_VIOLATION.
    for name, value in (
        ("source_manifest_hash", sm),
        ("canonical_ir_hash", cir),
        ("dataset_corpus_hash", corpus),
    ):
        if not _is_hex_64(value):
            return "HASH_CONTRACT_VIOLATION", f"{name} not 64-char hex"

    # If any hash doesn't match the frozen expected -> HASH_CONTRACT_VIOLATION.
    for name, value, expected in (
        ("source_manifest_hash", sm, EXPECTED_SOURCE_MANIFEST_HASH),
        ("canonical_ir_hash", cir, EXPECTED_CANONICAL_IR_HASH),
        ("dataset_corpus_hash", corpus, EXPECTED_DATASET_CORPUS_HASH),
    ):
        if value != expected:
            return "HASH_CONTRACT_VIOLATION", f"{name} tampered or wrong"

    # If all three hashes are equal (aliasing) -> HASH_CONTRACT_VIOLATION.
    if sm == cir or sm == corpus or cir == corpus:
        return "HASH_CONTRACT_VIOLATION", "two or more canonical hashes equal"

    # Scope checks.
    scopes = payload.get("scopes", [])
    if not isinstance(scopes, list) or not scopes:
        return "SCOPE_CONTRACT_VIOLATION", "scopes missing/empty"
    tenants = {s.get("tenant_id") for s in scopes if isinstance(s, dict)}
    workspaces = {s.get("workspace_id") for s in scopes if isinstance(s, dict)}
    if tenants - ALLOWED_SCOPES:
        return "SCOPE_CONTRACT_VIOLATION", f"unknown tenant(s): {sorted(tenants - ALLOWED_SCOPES)}"
    if workspaces - ALLOWED_WORKSPACES:
        return "SCOPE_CONTRACT_VIOLATION", (
            f"unknown workspace(s): {sorted(workspaces - ALLOWED_WORKSPACES)}"
        )
    # Mixing official and verification scopes in the same payload is rejected.
    if (OFFICIAL_TENANT in tenants and VERIFICATION_TENANT in tenants) or (
        OFFICIAL_WORKSPACE in workspaces and VERIFICATION_WORKSPACE in workspaces
    ):
        return "SCOPE_CONTRACT_VIOLATION", "official and verification scopes mixed"
    # Verification scope is allowed ONLY when the payload declares an
    # independent isolation envelope.
    if VERIFICATION_TENANT in tenants or VERIFICATION_WORKSPACE in workspaces:
        if not _is_isolated_envelope(payload):
            return (
                "SCOPE_CONTRACT_VIOLATION",
                "verification scope used without independent isolation envelope",
            )

    # KnowledgeVersion identity check.
    kv_id = payload.get("knowledge_version_id")
    if isinstance(kv_id, str) and kv_id:
        kv_uses_verify = (
            VERIFICATION_TENANT in kv_id or VERIFICATION_WORKSPACE in kv_id
        )
        if kv_uses_verify and not (
            VERIFICATION_TENANT in tenants or VERIFICATION_WORKSPACE in workspaces
        ):
            return (
                "SCOPE_CONTRACT_VIOLATION",
                "knowledge_version_id encodes verification scope but payload scopes[] do not",
            )

    return "CANONICAL_HASH_SCOPE_CONFIRMED", "all checks passed"


# --- Repository mode --------------------------------------------------------


def _run_repository_mode() -> VerifierResult:
    """Verify PR #112's current manifests + evidence."""

    result = VerifierResult(
        status="CANONICAL_HASH_SCOPE_CONFIRMED", exit_code=0
    )

    # Base head read.
    head_path = REPO_ROOT / ".git" / "HEAD"
    if head_path.exists():
        result.base_sha = head_path.read_text(encoding="utf-8").strip()

    source_upload = _read_json(
        REPO_ROOT / SOURCE_UPLOAD_MANIFEST_REPO
    )
    canonical_ir = _read_json(
        REPO_ROOT / CANONICAL_IR_MANIFEST_REPO
    )
    runtime_request = _read_json(
        REPO_ROOT / RUNTIME_REQUEST_MANIFEST_REPO
    )

    hash_ok = _enforce_hash_contract(
        result,
        source_upload_manifest=source_upload,
        canonical_ir_manifest=canonical_ir,
        runtime_request_manifest=runtime_request,
    )
    scope_ok = (
        _enforce_scope_contract(
            result,
            source_upload_manifest=source_upload or {},
            canonical_ir_manifest=canonical_ir or {},
            runtime_request_manifest=runtime_request or {},
        )
        if (source_upload and canonical_ir and runtime_request)
        else True
    )

    # Status truth: each manifest must show whether it has been
    # *executed*. INPUTS_PREPARED / INPUT_GOLD_ISOLATED are honest
    # statuses; the verifier records what the manifest declared rather
    # than rewriting history.
    declared_statuses: dict[str, str | None] = {
        SOURCE_UPLOAD_MANIFEST_REPO: (
            source_upload.get("status") if isinstance(source_upload, dict) else None
        ),
        CANONICAL_IR_MANIFEST_REPO: (
            canonical_ir.get("status") if isinstance(canonical_ir, dict) else None
        ),
        RUNTIME_REQUEST_MANIFEST_REPO: (
            runtime_request.get("status") if isinstance(runtime_request, dict) else None
        ),
    }
    result.repository_status = json.dumps(declared_statuses, sort_keys=True)

    if not hash_ok:
        result.status = "HASH_CONTRACT_VIOLATION"
        result.exit_code = 2
    elif not scope_ok:
        result.status = "SCOPE_CONTRACT_VIOLATION"
        result.exit_code = 3

    if not (source_upload and canonical_ir and runtime_request) and not hash_ok:
        result.status = "IDENTITY_UNRESOLVED"
        result.exit_code = 4

    # Record the not-proven boundary: runtime / DB live introspection.
    result.not_proven_boundary.extend(
        [
            "live database column tenant_id/workspace_id introspection",
            "KnowledgeSpace scope column vs manifest scope",
            "security_decisions (security_authorization_decisions) scope consistency",
            "KnowledgeVersion persistence in knowledge_versions table",
            "source_upload_manifest.runtime_ingested live attestation",
            "canonical_ir_manifest.parser_runtime_executed live attestation",
            "canonical_ir_manifest.postgres_facts_verified live attestation",
        ]
    )

    return result


# --- Entry point ------------------------------------------------------------


def _format_report(result: VerifierResult) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "gate_kind": "phase22_canonical_hash_scope",
        "status": result.status,
        "exit_code": result.exit_code,
        "base_sha": result.base_sha,
        "repository_status": result.repository_status,
        "expected_hashes": {
            "source_manifest_hash": EXPECTED_SOURCE_MANIFEST_HASH,
            "canonical_ir_hash": EXPECTED_CANONICAL_IR_HASH,
            "dataset_corpus_hash": EXPECTED_DATASET_CORPUS_HASH,
        },
        "detected_hashes": result.detected_hashes,
        "detected_scope": result.detected_scope,
        "violations": result.violations,
        "not_proven_boundary": result.not_proven_boundary,
        "official_scope": {
            "tenant_id": OFFICIAL_TENANT,
            "workspace_id": OFFICIAL_WORKSPACE,
        },
        "verification_scope": {
            "tenant_id": VERIFICATION_TENANT,
            "workspace_id": VERIFICATION_WORKSPACE,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="PHASE22 canonical hash / scope companion gate"
    )
    parser.add_argument(
        "--mode",
        choices=("contract", "repository"),
        required=True,
        help="contract = fixture suite; repository = PR #112 manifests",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional path to write a structured JSON report.",
    )
    args = parser.parse_args(argv)

    try:
        if args.mode == "contract":
            result = _run_contract_mode()
        else:
            result = _run_repository_mode()
    except Exception as exc:  # noqa: BLE001 - verifier must report cleanly
        result = VerifierResult(status="TOOL_ERROR", exit_code=5)
        _record_violation(
            result,
            kind="TOOL_ERROR",
            detail=f"verifier raised {type(exc).__name__}: {exc}",
        )

    report = _format_report(result)
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())