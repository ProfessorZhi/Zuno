"""PHASE22 Formal Benchmark Execution Entry (v1).

Reproducible formal entry for the fixed EnterpriseRAG benchmark. It turns
the existing contract smoke / ``blocked_not_measured`` state into a
machine-checkable execution contract:

* validates the formal Manifest Schema (``phase22-formal-benchmark-manifest.v1``);
* validates the **actual** Dataset file SHA-256 and the **actual** canonical
  Case Set hash (never trusts the declared hashes alone);
* validates the four-profile configuration completeness;
* validates the serialized Runtime / Credential / Reviewer / Budget /
  Security attestations through the existing PHASE22 preflight contract
  (``benchmark_preflight``, 11 gates, v8);
* validates the output path;
* executes the profiles that are allowed to run (injected canonical profile
  runtime factory) and writes precise, machine-readable blockers for the
  profiles that cannot run;
* writes immutable artifacts (write-once) with SHA-256, environment
  manifest, command line and Git SHA;
* never fabricates ``MEASURED``: test doubles stay blocked, runtime-observed
  stays ``RUNTIME_OBSERVED``, ``MEASURED`` requires a serialized Measurement
  Attestation bound to profile / artifact hash / fingerprint hash, and one
  blocked profile never fakes the other profiles' results.

Per-profile status vocabulary (fixed):

* ``READY_FOR_FORMAL_EXECUTION`` -- every gate passed; execution was not
  performed (``--check-only``).
* ``BLOCKED_NOT_MEASURED``       -- at least one required surface is missing
  or failed; precise ``blocker_codes`` are reported.
* ``RUNTIME_OBSERVED``           -- runtime evidence is complete but formal
  gates (reviewer / credentials / attestations) are pending.
* ``MEASURED``                   -- runtime evidence complete, all formal
  gates satisfied and a valid serialized Measurement Attestation is bound.
* ``INCOMPARABLE``               -- profiles disagree on a comparability
  dimension.
* ``ERROR``                      -- structural / execution error.

CLI Exit Code Contract (documented, not a crash):

* 0 -- READY_FOR_FORMAL_EXECUTION or MEASURED
* 1 -- RUNTIME_OBSERVED
* 2 -- BLOCKED_NOT_MEASURED
* 3 -- INCOMPARABLE
* 4 -- ERROR (including CLI usage / read / write / parse failures)

The CLI never prints a traceback, never leaks secrets or absolute paths in
stderr, and never modifies the input manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

# Allow running directly:
# ``python tools/evals/zuno/rag_eval/run_phase22_formal_benchmark.py``
# The canonical absolute imports work whenever the repo root and the backend
# root are on sys.path (pytest conftest adds both). For a standalone script
# run we insert them so the module works without going through a package
# entry point.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
_BACKEND_ROOT = os.path.join(_REPO_ROOT, "src", "backend")
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

# ---------------------------------------------------------------------------
# Version / status constants
# ---------------------------------------------------------------------------

ENTRY_VERSION = "phase22-formal-benchmark-entry.v1"
MANIFEST_VERSION = "phase22-formal-benchmark-manifest.v1"
BLOCKER_VOCABULARY_VERSION = "phase22-formal-benchmark-blockers.v1"

STATUS_READY = "READY_FOR_FORMAL_EXECUTION"
STATUS_BLOCKED = "BLOCKED_NOT_MEASURED"
STATUS_RUNTIME_OBSERVED = "RUNTIME_OBSERVED"
STATUS_MEASURED = "MEASURED"
STATUS_INCOMPARABLE = "INCOMPARABLE"
STATUS_ERROR = "ERROR"

ALL_STATUSES = frozenset(
    {
        STATUS_READY,
        STATUS_BLOCKED,
        STATUS_RUNTIME_OBSERVED,
        STATUS_MEASURED,
        STATUS_INCOMPARABLE,
        STATUS_ERROR,
    }
)

EXIT_OK = 0
EXIT_RUNTIME_OBSERVED = 1
EXIT_BLOCKED = 2
EXIT_INCOMPARABLE = 3
EXIT_ERROR = 4

STATUS_TO_EXIT = {
    STATUS_READY: EXIT_OK,
    STATUS_MEASURED: EXIT_OK,
    STATUS_RUNTIME_OBSERVED: EXIT_RUNTIME_OBSERVED,
    STATUS_BLOCKED: EXIT_BLOCKED,
    STATUS_INCOMPARABLE: EXIT_INCOMPARABLE,
    STATUS_ERROR: EXIT_ERROR,
}

# Fixed machine-readable blocker codes (PHASE22 formal entry vocabulary).
BLOCKER_DATASET_UNAVAILABLE = "DATASET_UNAVAILABLE"
BLOCKER_DATASET_HASH_MISMATCH = "DATASET_HASH_MISMATCH"
BLOCKER_CASE_SET_HASH_MISMATCH = "CASE_SET_HASH_MISMATCH"
BLOCKER_CANDIDATE_COUNT_MISMATCH = "CANDIDATE_COUNT_MISMATCH"
BLOCKER_MANIFEST_SCHEMA_INVALID = "MANIFEST_SCHEMA_INVALID"
BLOCKER_PROFILE_SET_INCOMPLETE = "PROFILE_SET_INCOMPLETE"
BLOCKER_CORPUS_SNAPSHOT_UNAVAILABLE = "CORPUS_SNAPSHOT_UNAVAILABLE"
BLOCKER_RUNTIME_ATTESTATION_MISSING = "RUNTIME_ATTESTATION_MISSING"
BLOCKER_RUNTIME_ATTESTATION_INVALID = "RUNTIME_ATTESTATION_INVALID"
BLOCKER_MISSING_FORMAL_CREDENTIAL = "MISSING_FORMAL_CREDENTIAL"
BLOCKER_REVIEWER_NOT_APPROVED = "REVIEWER_ATTESTATION_NOT_APPROVED"
BLOCKER_BUDGET_APPROVAL_MISSING = "BUDGET_APPROVAL_MISSING"
BLOCKER_SECURITY_APPROVAL_MISSING = "SECURITY_APPROVAL_MISSING"
BLOCKER_ARTIFACT_STORE_UNAVAILABLE = "ARTIFACT_STORE_UNAVAILABLE"
BLOCKER_PROFILE_RUNTIME_UNAVAILABLE = "PROFILE_RUNTIME_UNAVAILABLE"
BLOCKER_TEST_DOUBLE = "TEST_DOUBLE_NOT_MEASURED"
BLOCKER_MEASUREMENT_ATTESTATION_MISSING = "MEASUREMENT_ATTESTATION_MISSING"
BLOCKER_MEASUREMENT_ATTESTATION_INVALID = "MEASUREMENT_ATTESTATION_INVALID"
BLOCKER_PROFILES_INCOMPARABLE = "PROFILES_INCOMPARABLE"
BLOCKER_OUTPUT_PATH_UNAVAILABLE = "OUTPUT_PATH_UNAVAILABLE"
BLOCKER_OUTPUT_PATH_EXISTS = "OUTPUT_PATH_EXISTS"
BLOCKER_PROFILE_EXECUTION_FAILED = "PROFILE_EXECUTION_FAILED"
BLOCKER_INTERNAL_ERROR = "ENTRY_INTERNAL_ERROR"

ALL_BLOCKER_CODES = frozenset(
    {
        BLOCKER_DATASET_UNAVAILABLE,
        BLOCKER_DATASET_HASH_MISMATCH,
        BLOCKER_CASE_SET_HASH_MISMATCH,
        BLOCKER_CANDIDATE_COUNT_MISMATCH,
        BLOCKER_MANIFEST_SCHEMA_INVALID,
        BLOCKER_PROFILE_SET_INCOMPLETE,
        BLOCKER_CORPUS_SNAPSHOT_UNAVAILABLE,
        BLOCKER_RUNTIME_ATTESTATION_MISSING,
        BLOCKER_RUNTIME_ATTESTATION_INVALID,
        BLOCKER_MISSING_FORMAL_CREDENTIAL,
        BLOCKER_REVIEWER_NOT_APPROVED,
        BLOCKER_BUDGET_APPROVAL_MISSING,
        BLOCKER_SECURITY_APPROVAL_MISSING,
        BLOCKER_ARTIFACT_STORE_UNAVAILABLE,
        BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
        BLOCKER_TEST_DOUBLE,
        BLOCKER_MEASUREMENT_ATTESTATION_MISSING,
        BLOCKER_MEASUREMENT_ATTESTATION_INVALID,
        BLOCKER_PROFILES_INCOMPARABLE,
        BLOCKER_OUTPUT_PATH_UNAVAILABLE,
        BLOCKER_OUTPUT_PATH_EXISTS,
        BLOCKER_PROFILE_EXECUTION_FAILED,
        BLOCKER_INTERNAL_ERROR,
    }
)

# Entry-only top-level fields that are stripped before the preflight
# contract is evaluated (the preflight contract rejects unknown fields).
ENTRY_ONLY_TOP_FIELDS = ("manifest_version", "dataset_path", "case_set_hash")

REQUIRED_MANIFEST_FIELDS = (
    "manifest_version",
    "eval_run_id",
    "case_set_ref",
    "dataset_version",
    "dataset_path",
    "dataset_hash",
    "case_set_hash",
    "candidate_count",
    "profiles",
)

CANONICAL_PROFILES = (
    "standard_rag",
    "local_graphrag",
    "deep_graphrag",
    "agentic_graphrag",
)

FORMAL_ADAPTER_REFS = {
    "standard_rag": "canonical-adapter://phase22/standard_rag",
    "local_graphrag": "canonical-adapter://phase22/local_graphrag",
    "deep_graphrag": "canonical-adapter://phase22/deep_graphrag",
    "agentic_graphrag": "canonical-adapter://phase22/agentic_graphrag",
}

# Per-profile manifest fields required by the formal entry (beyond the
# preflight surface). Missing values block the owning profile.
REQUIRED_PROFILE_ENTRY_FIELDS = (
    "profile_name",
    "corpus_snapshot_ref",
    "knowledge_snapshot_ref",
    "model_config_ref",
    "judge_config_ref",
    "embedding_config_ref",
    "metric_definition_ref",
)

# Preflight gap code -> fixed blocker code mapping.
_PREFLIGHT_GAP_TO_BLOCKER: Mapping[str, str] = {
    # governance / reviewer
    "reviewer_not_approved": BLOCKER_REVIEWER_NOT_APPROVED,
    "benchmark_not_eligible": BLOCKER_REVIEWER_NOT_APPROVED,
    "license_not_verified": BLOCKER_REVIEWER_NOT_APPROVED,
    "integrity_not_verified": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_missing": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_invalid": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_field_missing": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_version_mismatch": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_hash_invalid": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_hash_mismatch": BLOCKER_REVIEWER_NOT_APPROVED,
    "reviewer_attestation_scope_mismatch": BLOCKER_REVIEWER_NOT_APPROVED,
    # dataset / snapshot
    "case_set_ref_missing": BLOCKER_DATASET_UNAVAILABLE,
    "dataset_version_missing": BLOCKER_DATASET_UNAVAILABLE,
    "dataset_hash_missing": BLOCKER_DATASET_UNAVAILABLE,
    "candidate_count_invalid": BLOCKER_DATASET_UNAVAILABLE,
    "profile_case_set_ref_missing": BLOCKER_DATASET_UNAVAILABLE,
    "profile_dataset_version_missing": BLOCKER_DATASET_UNAVAILABLE,
    "corpus_snapshot_missing": BLOCKER_CORPUS_SNAPSHOT_UNAVAILABLE,
    "profile_corpus_snapshot_missing": BLOCKER_CORPUS_SNAPSHOT_UNAVAILABLE,
    # runtime
    "product_runtime_not_attested": BLOCKER_RUNTIME_ATTESTATION_MISSING,
    "product_runtime_attestation_missing": BLOCKER_RUNTIME_ATTESTATION_MISSING,
    "product_runtime_attestation_invalid": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_field_missing": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_version_mismatch": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_hash_invalid": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_hash_mismatch": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_runtime_mismatch": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "product_runtime_attestation_scope_mismatch": BLOCKER_RUNTIME_ATTESTATION_INVALID,
    "runtime_name_missing": BLOCKER_RUNTIME_ATTESTATION_MISSING,
    "runtime_version_missing": BLOCKER_RUNTIME_ATTESTATION_MISSING,
    "runtime_adapter_unwired": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "knowledge_runtime_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "index_runtime_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "agent_run_runtime_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "trace_adapter_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "result_store_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "artifact_store_unavailable": BLOCKER_ARTIFACT_STORE_UNAVAILABLE,
    "usage_receipt_provider_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    "budget_settlement_provider_unavailable": BLOCKER_PROFILE_RUNTIME_UNAVAILABLE,
    # security
    "authorization_ref_missing": BLOCKER_SECURITY_APPROVAL_MISSING,
    "security_epoch_missing": BLOCKER_SECURITY_APPROVAL_MISSING,
    "profile_security_epoch_missing": BLOCKER_SECURITY_APPROVAL_MISSING,
    "security_epoch_stale": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_not_approved": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_missing": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_invalid": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_field_missing": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_version_mismatch": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_hash_invalid": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_hash_mismatch": BLOCKER_SECURITY_APPROVAL_MISSING,
    "formal_execution_attestation_scope_mismatch": BLOCKER_SECURITY_APPROVAL_MISSING,
    # budget
    "human_budget_not_approved": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_missing": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_invalid": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_field_missing": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_version_mismatch": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_hash_invalid": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_hash_mismatch": BLOCKER_BUDGET_APPROVAL_MISSING,
    "human_budget_attestation_scope_mismatch": BLOCKER_BUDGET_APPROVAL_MISSING,
    "budget_policy_ref_missing": BLOCKER_BUDGET_APPROVAL_MISSING,
    "profile_budget_policy_ref_missing": BLOCKER_BUDGET_APPROVAL_MISSING,
    "provider_cost_limit_invalid": BLOCKER_BUDGET_APPROVAL_MISSING,
    "token_limit_invalid": BLOCKER_BUDGET_APPROVAL_MISSING,
    "deadline_missing": BLOCKER_BUDGET_APPROVAL_MISSING,
    # credentials
    "credential_ref_missing": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credentials_missing": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_execution_not_requested": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_missing": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_invalid": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_field_missing": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_version_mismatch": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_hash_invalid": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_hash_mismatch": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    "formal_credential_attestation_scope_mismatch": BLOCKER_MISSING_FORMAL_CREDENTIAL,
    # output contract
    "output_artifact_ref_missing": BLOCKER_ARTIFACT_STORE_UNAVAILABLE,
    # gold firewall
    "gold_firewall_not_proven": BLOCKER_SECURITY_APPROVAL_MISSING,
    # governance identity
    "eval_run_id_missing": BLOCKER_MANIFEST_SCHEMA_INVALID,
}

# Gap codes owned by a specific profile (runtime gate) vs global gates.
_RUNTIME_OWNED_GAP_CODES = frozenset(
    {
        "product_runtime_not_attested",
        "product_runtime_attestation_missing",
        "product_runtime_attestation_invalid",
        "product_runtime_attestation_field_missing",
        "product_runtime_attestation_version_mismatch",
        "product_runtime_attestation_hash_invalid",
        "product_runtime_attestation_hash_mismatch",
        "product_runtime_attestation_runtime_mismatch",
        "product_runtime_attestation_scope_mismatch",
        "runtime_name_missing",
        "runtime_version_missing",
        "runtime_adapter_unwired",
        "knowledge_runtime_unavailable",
        "index_runtime_unavailable",
        "agent_run_runtime_unavailable",
        "trace_adapter_unavailable",
        "result_store_unavailable",
        "artifact_store_unavailable",
        "usage_receipt_provider_unavailable",
        "budget_settlement_provider_unavailable",
        "corpus_snapshot_missing",
    }
)


# ---------------------------------------------------------------------------
# Hash helpers
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> Optional[str]:
    """SHA-256 of a file, or ``None`` when the file is missing."""
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def canonical_sha256_hex(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def canonical_case_id_hash(rows: list[Mapping[str, Any]]) -> str:
    """Canonical hash over the ordered case ids of the actual dataset rows."""
    case_ids = [str(row.get("case_id") or row.get("id") or "") for row in rows]
    return canonical_sha256_hex(case_ids)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def _strict_parse_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def read_json(path: Path) -> Any:
    """Read a JSON file. Raises ``OSError`` / ``ValueError`` on failure."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle, parse_constant=_strict_parse_constant)


def _write_atomic(path: Path, content: str) -> None:
    """Write an immutable artifact with explicit ``\\n`` line endings so the
    file bytes are byte-identical across platforms (the recorded SHA-256 is
    the hash of exactly these bytes)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(content, encoding="utf-8", newline="\n")
    tmp_path.replace(path)


def _write_sidecar_sha256(sidecar_path: Path, target_path: Path) -> str:
    """Compute the SHA-256 of the on-disk final ``target_path`` bytes and
    persist it to ``sidecar_path``. The hash is derived from the actual
    bytes committed to disk via ``_write_atomic`` so the sidecar is
    byte-stable and never self-referential.
    """
    final_bytes = target_path.read_bytes()
    digest = hashlib.sha256(final_bytes).hexdigest()
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_sidecar = sidecar_path.with_suffix(sidecar_path.suffix + ".tmp")
    tmp_sidecar.write_text(digest + "\n", encoding="utf-8", newline="\n")
    tmp_sidecar.replace(sidecar_path)
    return digest


class _AtomicArtifactPublisher:
    """PHASE22 (Slice A): atomic publish for the formal benchmark artifacts.

    Contract:

    - The publisher NEVER writes to ``output_dir`` directly. Every artifact
      is first written to a unique staging directory under
      ``output_dir.parent / f".staging-{run_id}"`` so partial output cannot
      be observed by a downstream consumer reading ``output_dir``.
    - On commit, the staging directory is renamed to ``output_dir`` in a
      single atomic step. A failure at any time leaves the staging dir as
      the only on-disk residue — the final output directory is never
      partially populated.
    - The report bytes are committed to disk first; the sidecar SHA-256 is
      computed from the on-disk final bytes (not from a serialized dict
      that contains the sidecar field). The ``report_integrity`` field
      documents the sidecar protocol — the report NEVER carries a
      self-referential hash.
    - If the final output directory already exists, the publisher raises
      ``OUTPUT_PATH_EXISTS`` rather than overwriting. The final output is
      write-once; tests assert that re-running against the same directory
      fails closed.
    - The staging directory is removed on every failure path. The final
      output directory is published only after the rename succeeds.
    """

    def __init__(self, output_dir: Path, run_id: str) -> None:
        self.output_dir = Path(output_dir)
        self.run_id = str(run_id or "run")
        self.parent_dir = self.output_dir.parent
        self.staging_dir = self.parent_dir / f".staging-{self.run_id}"
        self._committed = False

    def open(self) -> None:
        """Prepare the staging directory. Raises ``OUTPUT_PATH_EXISTS`` if the
        final output already exists, or ``OUTPUT_PATH_UNAVAILABLE`` if the
        staging directory cannot be created.
        """
        if self.output_dir.exists():
            raise OutputPathExists(self.output_dir)
        if self.staging_dir.exists():
            # left-over from a previous crash; remove so we don't reuse stale
            # partial artifacts.
            shutil.rmtree(self.staging_dir, ignore_errors=True)
        try:
            self.staging_dir.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            raise OutputPathUnavailable(str(exc)) from exc

    def write(self, relative_path: str, content: str) -> None:
        """Write one artifact to the staging directory."""
        target = self.staging_dir / relative_path
        _write_atomic(target, content)

    def write_binary(self, relative_path: str, content: bytes) -> None:
        target = self.staging_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target.with_suffix(target.suffix + ".tmp")
        tmp_path.write_bytes(content)
        tmp_path.replace(target)

    def write_sidecar_for(self, relative_path: str) -> str:
        """Compute the SHA-256 of the on-disk staging bytes for
        ``relative_path`` and persist the sidecar next to it. Returns the
        digest. The sidecar hash is always derived from the on-disk bytes,
        never from the serialized dict that may carry a sidecar field.
        """
        target = self.staging_dir / relative_path
        sidecar = self.staging_dir / f"{relative_path}.sha256"
        return _write_sidecar_sha256(sidecar, target)

    def path(self, relative_path: str) -> Path:
        return self.staging_dir / relative_path

    def commit(self) -> None:
        """Atomically rename the staging directory to the final output
        directory. Raises if the rename fails (the staging dir is left
        on disk for diagnostics; the final output is not partially
        populated)."""
        if self._committed:
            raise RuntimeError("publisher already committed")
        try:
            self.staging_dir.replace(self.output_dir)
        except OSError as exc:
            raise OutputPathUnavailable(
                f"rename staging->final failed: {exc}"
            ) from exc
        self._committed = True

    def discard(self) -> None:
        """Remove the staging directory. Used on every failure path so the
        final output dir is never partially populated."""
        if self._committed:
            return
        shutil.rmtree(self.staging_dir, ignore_errors=True)


class OutputPathExists(RuntimeError):
    """PHASE22 (Slice A): the final output directory already exists. The
    publisher refuses to overwrite an immutable artifact set."""


class OutputPathUnavailable(RuntimeError):
    """PHASE22 (Slice A): the staging directory cannot be created, or the
    final rename to ``output_dir`` failed. The publish is aborted; no
    final output is published."""


def serialize_json(payload: Any) -> str:
    text = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    if not text.endswith("\n"):
        text += "\n"
    return text


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_git_info() -> tuple[str, bool]:
    import subprocess

    try:
        sha_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        sha = sha_result.stdout.strip()
        status_result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            capture_output=True,
            text=True,
            check=True,
        )
        dirty = bool(status_result.stdout.strip())
        return sha, dirty
    except Exception:
        return "unknown", True


# ---------------------------------------------------------------------------
# Manifest validation
# ---------------------------------------------------------------------------


def validate_manifest_schema(manifest: Any) -> tuple[Optional[str], list[str]]:
    """Validate the formal manifest schema. Returns ``(error_code, details)``
    where ``error_code`` is ``None`` when the schema is valid."""
    if not isinstance(manifest, Mapping):
        return BLOCKER_MANIFEST_SCHEMA_INVALID, ["manifest_not_object"]
    details: list[str] = []
    for field_name in REQUIRED_MANIFEST_FIELDS:
        if field_name not in manifest:
            details.append(f"missing_field:{field_name}")
    if "manifest_version" in manifest and manifest["manifest_version"] != MANIFEST_VERSION:
        details.append("manifest_version_mismatch")
    profiles = manifest.get("profiles")
    if not isinstance(profiles, list):
        details.append("profiles_not_a_list")
    else:
        names = []
        for entry in profiles:
            if not isinstance(entry, Mapping):
                details.append("profile_invalid_entry")
                continue
            name = entry.get("profile_name")
            if not isinstance(name, str) or not name:
                details.append("profile_name_missing")
                continue
            names.append(name)
            for field_name in REQUIRED_PROFILE_ENTRY_FIELDS:
                value = entry.get(field_name)
                if not isinstance(value, str) or not str(value).strip():
                    details.append(f"profile_field_missing:{name}:{field_name}")
        if len(set(names)) != len(names):
            details.append("profile_duplicate")
        if set(names) != set(CANONICAL_PROFILES):
            details.append("profile_set_incomplete")
    if details:
        return BLOCKER_MANIFEST_SCHEMA_INVALID, details
    return None, []


def build_preflight_payload(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Strip the entry-only fields so the v8 preflight contract accepts it."""
    return {
        key: value
        for key, value in manifest.items()
        if key not in ENTRY_ONLY_TOP_FIELDS
    }


def preflight_gap_to_blocker(gap_code: str) -> str:
    mapped = _PREFLIGHT_GAP_TO_BLOCKER.get(gap_code)
    if mapped is not None:
        return mapped
    if gap_code.startswith("input_") or gap_code.startswith("profile_"):
        return BLOCKER_MANIFEST_SCHEMA_INVALID
    return BLOCKER_PROFILE_RUNTIME_UNAVAILABLE


# ---------------------------------------------------------------------------
# Per-profile execution
# ---------------------------------------------------------------------------


def _import_factory(factory_ref: str) -> Callable[..., Any]:
    """Import ``module:attr``. Raises ``ImportError``/``AttributeError``."""
    module_name, _, attr_name = factory_ref.partition(":")
    if not module_name or not attr_name:
        raise ValueError("profile_runtime_factory must be MODULE:ATTR")
    module = __import__(module_name, fromlist=[attr_name])
    factory = getattr(module, attr_name)
    if not callable(factory):
        raise TypeError("profile_runtime_factory is not callable")
    return factory


def _result_to_dict(result: Any) -> dict[str, Any]:
    if isinstance(result, Mapping):
        return dict(result)
    if hasattr(result, "__dataclass_fields__"):
        import dataclasses

        return dataclasses.asdict(result)
    return dict(result)


def _result_field(result: Any, field_name: str, default: Any = None) -> Any:
    payload = _result_to_dict(result)
    return payload.get(field_name, default)


def _run_profile_cases(
    runner: Any,
    *,
    profile_name: str,
    rows: list[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Run one profile over the case set through the injected runner.

    A per-case exception never aborts the entry: the case becomes a
    fail-closed blocked result so the profile can report a precise blocker
    instead of crashing the run.
    """
    from tools.evals.zuno.rag_eval.canonical_profile_runners import (
        CanonicalCaseInput,
        CanonicalCaseResult,
    )

    eval_run_id = str(manifest.get("eval_run_id") or "")
    results: list[dict[str, Any]] = []
    for row in rows:
        case_input = CanonicalCaseInput(
            eval_run_id=eval_run_id,
            case_id=str(row.get("case_id") or row.get("id") or ""),
            profile_name=profile_name,
            question=str(row.get("question") or row.get("query") or ""),
            question_type=str(row.get("question_type") or "unknown"),
            corpus_snapshot_ref=str(row.get("corpus_snapshot_ref") or ""),
            gold_document_refs=tuple(
                str(item) for item in (row.get("expected_doc_ids") or [])
            ),
            gold_evidence_refs=tuple(
                str(item) for item in (row.get("gold_evidence") or [])
            ),
            authorization_ref=str(manifest.get("authorization_ref") or ""),
            security_epoch=str(manifest.get("security_epoch") or ""),
            deadline=str(manifest.get("deadline") or ""),
        )
        try:
            result = runner.run_canonical_case(case_input)
        except Exception:
            result = CanonicalCaseResult(
                eval_run_id=eval_run_id,
                case_id=case_input.case_id,
                profile_name=profile_name,
                runtime_status="failed",
                measurement_state="BLOCKED",
                answer="",
                retrieved_document_refs=(),
                retrieved_evidence_refs=(),
                citation_refs=(),
                knowledge_snapshot_ref="",
                plan_version_ref="",
                run_outcome_ref="",
                budget_settlement_ref="",
                blocked_reason="profile_case_execution_failed",
            )
        results.append(_result_to_dict(result))
    return results


def _aggregate_profile_state(results: list[dict[str, Any]]) -> str:
    """Aggregate per-case measurement states into the profile state."""
    states = {str(item.get("measurement_state") or "") for item in results}
    if not states:
        return "BLOCKED"
    if states == {"MEASURED"}:
        return "MEASURED"
    if states == {"RUNTIME_OBSERVED"}:
        return "RUNTIME_OBSERVED"
    if states == {"BLOCKED"}:
        return "BLOCKED"
    if "BLOCKED" in states:
        return "BLOCKED"
    if "FAILED" in states:
        return "FAILED"
    return sorted(states)[0]


# ---------------------------------------------------------------------------
# Fingerprint / attestation
# ---------------------------------------------------------------------------


def build_profile_fingerprint(
    *,
    profile_name: str,
    manifest: Mapping[str, Any],
    profile_block: Mapping[str, Any],
    case_set_hash: str,
) -> dict[str, str | None]:
    """Twelve-dimension comparability fingerprint (release-decision contract)."""
    return {
        "dataset_version": str(manifest.get("dataset_version") or ""),
        "case_set_hash": case_set_hash,
        "corpus_snapshot": str(profile_block.get("corpus_snapshot_ref") or ""),
        "knowledge_snapshot": str(profile_block.get("knowledge_snapshot_ref") or ""),
        "graph_snapshot": str(profile_block.get("knowledge_snapshot_ref") or ""),
        "model_profile": str(profile_block.get("model_config_ref") or ""),
        "judge_policy": str(profile_block.get("judge_config_ref") or ""),
        "embedding_profile": str(profile_block.get("embedding_config_ref") or ""),
        "metric_definition": str(profile_block.get("metric_definition_ref") or ""),
        "runtime_profile": "{}@{}".format(
            str(profile_block.get("runtime_name") or ""),
            str(profile_block.get("runtime_version") or ""),
        ),
        "security_scope": str(profile_block.get("security_epoch") or ""),
        "budget_class": str(profile_block.get("budget_policy_ref") or ""),
    }


def build_profile_artifact(
    *,
    profile_name: str,
    manifest: Mapping[str, Any],
    profile_block: Mapping[str, Any],
    case_set_hash: str,
    rows: list[Mapping[str, Any]],
    results: list[dict[str, Any]],
    measurement_status: str,
    blocker_codes: list[str],
    blocker_details: list[str],
    preflight_profile_result: Any,
) -> dict[str, Any]:
    """Deterministic per-profile artifact payload (no timestamps, no
    environment data — rerun-reproducible byte-for-byte)."""
    fingerprint = build_profile_fingerprint(
        profile_name=profile_name,
        manifest=manifest,
        profile_block=profile_block,
        case_set_hash=case_set_hash,
    )
    runtime_attestations = [
        item.get("product_runtime_attestation")
        for item in results
        if isinstance(item.get("product_runtime_attestation"), dict)
        and item.get("product_runtime_attestation")
    ]
    evidence_refs = sorted(
        {
            str(ref)
            for item in results
            for ref in (item.get("evidence_refs") or [])
            if ref
        }
    )
    # The Measurement Attestation is profile-level evidence, never part of
    # the per-case measurement facts: strip it so the facts artifact stays
    # deterministic and the attestation binds to the facts only.
    per_case_results = [
        {key: value for key, value in item.items() if key != "measurement_attestation"}
        for item in results
    ]
    return {
        "profile_id": profile_name,
        "runtime_adapter": FORMAL_ADAPTER_REFS.get(profile_name, ""),
        "dataset_version": str(manifest.get("dataset_version") or ""),
        "case_set_hash": case_set_hash,
        "corpus_snapshot": str(profile_block.get("corpus_snapshot_ref") or ""),
        "knowledge_snapshot": str(profile_block.get("knowledge_snapshot_ref") or ""),
        "model_config_ref": str(profile_block.get("model_config_ref") or ""),
        "judge_config_ref": str(profile_block.get("judge_config_ref") or ""),
        "embedding_config_ref": str(profile_block.get("embedding_config_ref") or ""),
        "security_policy_ref": "{}@{}".format(
            str(manifest.get("authorization_ref") or ""),
            str(profile_block.get("security_epoch") or ""),
        ),
        "formal_credential_ref": str(manifest.get("credential_ref") or ""),
        "reviewer_attestation_ref": _attestation_ref(
            manifest.get("reviewer_attestation")
        ),
        "budget_approval_ref": _attestation_ref(
            manifest.get("human_budget_attestation")
        ),
        "runtime_attestation_ref": (
            str(runtime_attestations[0].get("attestation_ref") or "")
            if runtime_attestations
            else ""
        ),
        "measurement_status": measurement_status,
        "blocker_codes": sorted(set(blocker_codes)),
        "blocker_details": sorted(set(blocker_details)),
        "fingerprint": fingerprint,
        "fingerprint_hash": canonical_sha256_hex(fingerprint),
        "evidence_ref": evidence_refs[0] if evidence_refs else "",
        "preflight_profile_state": (
            preflight_profile_result.state if preflight_profile_result is not None else ""
        ),
        "preflight_profile_gap_codes": list(
            preflight_profile_result.gap_codes
            if preflight_profile_result is not None
            else ()
        ),
        "case_count": len(rows),
        "per_case_results": per_case_results,
    }


def _attestation_ref(attestation: Any) -> str:
    if isinstance(attestation, Mapping):
        value = attestation.get("attestation_ref")
        if isinstance(value, str):
            return value
    return ""


def validate_measurement_attestation(
    attestation: Any,
    *,
    profile_id: str,
    measurement_status: str,
    artifact_hash: str,
    fingerprint_hash: str,
    evidence_ref: str,
) -> Optional[str]:
    """Validate a serialized Measurement Attestation. Returns ``None`` on
    success, or a fixed blocker code on failure."""
    from tools.evals.zuno.rag_eval.release_decision import (
        MEASUREMENT_ATTESTATION_VERSION,
        compute_measurement_attestation_hash,
    )

    if attestation is None:
        return BLOCKER_MEASUREMENT_ATTESTATION_MISSING
    if not isinstance(attestation, Mapping):
        return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    required_fields = (
        "attestation_ref",
        "profile_id",
        "measurement_status",
        "artifact_hash",
        "fingerprint_hash",
        "evidence_ref",
        "measurement_attestation_contract_version",
        "attestation_hash",
    )
    for field_name in required_fields:
        value = attestation.get(field_name)
        if not isinstance(value, str) or not value:
            return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    if (
        attestation.get("measurement_attestation_contract_version")
        != MEASUREMENT_ATTESTATION_VERSION
    ):
        return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    try:
        expected_hash = compute_measurement_attestation_hash(attestation)
    except (TypeError, ValueError):
        return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    if attestation.get("attestation_hash") != expected_hash:
        return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    if (
        attestation.get("profile_id") != profile_id
        or attestation.get("measurement_status") != measurement_status
        or attestation.get("artifact_hash") != artifact_hash
        or attestation.get("fingerprint_hash") != fingerprint_hash
        or attestation.get("evidence_ref") != evidence_ref
    ):
        return BLOCKER_MEASUREMENT_ATTESTATION_INVALID
    return None


# ---------------------------------------------------------------------------
# Entry orchestrator
# ---------------------------------------------------------------------------


def run_formal_benchmark(
    manifest: Mapping[str, Any],
    output_dir: Path,
    *,
    profile_runtime_factory: Optional[Callable[..., Any]] = None,
    check_only: bool = False,
) -> dict[str, Any]:
    """Run the formal benchmark entry. Never raises for business-level
    blockers; only I/O / structural catastrophes raise ``OSError`` /
    ``ValueError`` which the CLI maps to ERROR."""
    from tools.evals.zuno.rag_eval.benchmark_preflight import (
        BenchmarkPreflightEvaluator,
        STATE_BLOCKED,
        STATE_INCOMPARABLE,
        STATE_INVALID,
        STATE_READY,
        report_to_dict,
    )

    schema_error, schema_details = validate_manifest_schema(manifest)
    if schema_error is not None:
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_MANIFEST_SCHEMA_INVALID,
            blocker_details=schema_details,
        )

    output_dir = Path(output_dir)
    if output_dir.exists():
        # PHASE22 (Slice A): the final output dir is write-once. A re-run
        # against the same path is rejected up-front — never silently
        # overwrite the immutable artifact set.
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_OUTPUT_PATH_EXISTS,
            blocker_details=["immutable_artifact_exists"],
        )
    parent_dir = output_dir.parent
    if not parent_dir.exists():
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            return _error_report(
                manifest=manifest,
                output_dir=output_dir,
                reason=BLOCKER_OUTPUT_PATH_UNAVAILABLE,
                blocker_details=["output_dir_creation_failed"],
            )
    if not parent_dir.is_dir():
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_OUTPUT_PATH_UNAVAILABLE,
            blocker_details=["output_path_not_a_directory"],
        )
    report_path = output_dir / "benchmark_report.json"

    # PHASE22 (Slice A): atomic publish via the staging directory. Every
    # artifact is written to ``output_dir.parent / f".staging-{run_id}"``
    # first; the final rename publishes the entire set. The publisher
    # raises OutputPathExists / OutputPathUnavailable on failure paths.
    run_id = str(manifest.get("eval_run_id") or "run")
    publisher = _AtomicArtifactPublisher(output_dir=output_dir, run_id=run_id)
    try:
        publisher.open()
    except OutputPathExists:
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_OUTPUT_PATH_EXISTS,
            blocker_details=["immutable_artifact_exists"],
        )
    except OutputPathUnavailable as exc:
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_OUTPUT_PATH_UNAVAILABLE,
            blocker_details=[f"staging_open_failed:{exc}"],
        )

    # -- dataset / case hash validation (actual files, never declared-only)
    dataset_path = Path(str(manifest.get("dataset_path") or ""))
    dataset_sha = sha256_file(dataset_path)
    declared_dataset_hash = str(manifest.get("dataset_hash") or "")
    rows: list[Mapping[str, Any]] = []
    dataset_blockers: list[str] = []
    dataset_details: list[str] = []
    if dataset_sha is None:
        dataset_blockers.append(BLOCKER_DATASET_UNAVAILABLE)
        dataset_details.append("dataset_file_not_found")
    else:
        try:
            rows = read_jsonl(dataset_path)
        except (OSError, ValueError, json.JSONDecodeError):
            dataset_blockers.append(BLOCKER_DATASET_UNAVAILABLE)
            dataset_details.append("dataset_file_unreadable")
            rows = []
        if declared_dataset_hash and dataset_sha != declared_dataset_hash:
            dataset_blockers.append(BLOCKER_DATASET_HASH_MISMATCH)
            dataset_details.append("dataset_sha256_mismatch")
    actual_case_hash = canonical_case_id_hash(rows) if rows else ""
    declared_case_hash = str(manifest.get("case_set_hash") or "")
    if declared_case_hash and actual_case_hash and actual_case_hash != declared_case_hash:
        dataset_blockers.append(BLOCKER_CASE_SET_HASH_MISMATCH)
        dataset_details.append("case_set_hash_mismatch")
    try:
        declared_count = int(manifest.get("candidate_count") or 0)
    except (TypeError, ValueError):
        declared_count = 0
    if rows and declared_count > 0 and len(rows) != declared_count:
        dataset_blockers.append(BLOCKER_CANDIDATE_COUNT_MISMATCH)
        dataset_details.append(
            f"candidate_count_declared:{declared_count}_actual:{len(rows)}"
        )

    # -- preflight (11 gates, v8 contract)
    preflight_report = BenchmarkPreflightEvaluator().evaluate(
        build_preflight_payload(manifest)
    )
    preflight_dict = report_to_dict(preflight_report)
    preflight_ready = preflight_report.state == STATE_READY
    preflight_by_profile = {
        pr.profile_name: pr for pr in preflight_report.profile_results
    }
    # Global preflight gaps are owned by every profile: a globally blocked
    # preflight must never let any profile proceed to execution.
    global_preflight_gaps = list(preflight_report.gap_codes)

    # INCOMPARABLE preflight: the four profiles disagree on a shared
    # comparability dimension before execution. The run is INCOMPARABLE —
    # never a quality conclusion — and execution is skipped entirely.
    if preflight_report.state == STATE_INCOMPARABLE:
        incomparable_report = _incomparable_report(
            manifest=manifest,
            preflight_dict=preflight_dict,
            gap_codes=list(preflight_report.gap_codes),
            dataset_sha=dataset_sha,
            declared_dataset_hash=declared_dataset_hash,
            case_set_hash=actual_case_hash or declared_case_hash,
            declared_case_set_hash=declared_case_hash,
            declared_count=declared_count,
            actual_count=len(rows),
            publisher=publisher,
        )
        try:
            publisher.commit()
        except OutputPathUnavailable as exc:
            publisher.discard()
            return _error_report(
                manifest=manifest,
                output_dir=output_dir,
                reason=BLOCKER_OUTPUT_PATH_UNAVAILABLE,
                blocker_details=[f"commit_failed:{exc}"],
            )
        return incomparable_report

    # -- execution factory
    factory = None
    if preflight_ready and not check_only and profile_runtime_factory is not None:
        factory = profile_runtime_factory

    profiles_block: dict[str, Any] = {}
    profiles: list[dict[str, Any]] = []
    for profile_name in CANONICAL_PROFILES:
        profile_block = _manifest_profile(manifest, profile_name)
        profile_blockers: list[str] = []
        profile_details: list[str] = []
        profile_blockers.extend(dataset_blockers)
        profile_details.extend(dataset_details)

        # per-profile schema completeness (entry fields)
        for field_name in REQUIRED_PROFILE_ENTRY_FIELDS:
            value = profile_block.get(field_name)
            if not isinstance(value, str) or not str(value).strip():
                profile_blockers.append(BLOCKER_MANIFEST_SCHEMA_INVALID)
                profile_details.append(f"profile_field_missing:{profile_name}:{field_name}")

        for gap in global_preflight_gaps:
            profile_blockers.append(preflight_gap_to_blocker(gap))
            profile_details.append(gap)
        preflight_profile = preflight_by_profile.get(profile_name)
        if preflight_profile is not None and preflight_profile.gap_codes:
            for gap in preflight_profile.gap_codes:
                profile_blockers.append(preflight_gap_to_blocker(gap))
                profile_details.append(gap)
        if preflight_profile is not None and preflight_profile.state != STATE_READY:
            profile_details.append(f"preflight_state:{preflight_profile.state}")

        measurement_status = STATUS_BLOCKED
        results: list[dict[str, Any]] = []
        runner = None
        if not profile_blockers:
            if check_only:
                measurement_status = STATUS_READY
            elif factory is not None:
                try:
                    runner = factory.create_runner(profile_name)
                except Exception:
                    profile_blockers.append(BLOCKER_PROFILE_RUNTIME_UNAVAILABLE)
                    profile_details.append("factory_create_runner_failed")
            else:
                # No injected factory: try the canonical factory with an
                # empty dependency bundle (fails closed with precise gaps).
                try:
                    from tools.evals.zuno.rag_eval.canonical_profile_runners import (
                        CanonicalRuntimeDependencies,
                    )
                    from tools.evals.zuno.rag_eval.profile_runtime_factory import (
                        CanonicalProfileRuntimeFactory,
                    )

                    deps = CanonicalRuntimeDependencies()
                    factory = CanonicalProfileRuntimeFactory(
                        runtime_mode="canonical", canonical_deps=deps
                    )
                    runner = factory.create_runner(profile_name)
                except Exception:
                    for gap in CanonicalRuntimeDependencies().validate_dependencies(
                        profile_name
                    ):
                        profile_blockers.append(BLOCKER_PROFILE_RUNTIME_UNAVAILABLE)
                        profile_details.append(gap)
                    profile_blockers.append(BLOCKER_PROFILE_RUNTIME_UNAVAILABLE)
                    profile_details.append("canonical_dependency_bundle_unavailable")
        if runner is not None and rows:
            results = _run_profile_cases(
                runner,
                profile_name=profile_name,
                rows=rows,
                manifest=manifest,
            )
            profile_state = _aggregate_profile_state(results)
            if profile_state == "FAILED":
                profile_blockers.append(BLOCKER_PROFILE_EXECUTION_FAILED)
                profile_details.append("runtime_execution_failed")
                measurement_status = STATUS_BLOCKED
            elif profile_state == "BLOCKED":
                blocked_reasons = sorted(
                    {
                        str(item.get("blocked_reason") or "")
                        for item in results
                        if item.get("blocked_reason")
                    }
                )
                dependency_gaps = sorted(
                    {
                        str(gap)
                        for item in results
                        for gap in (item.get("dependency_gaps") or [])
                    }
                )
                profile_blockers.append(BLOCKER_PROFILE_RUNTIME_UNAVAILABLE)
                profile_details.extend(blocked_reasons)
                profile_details.extend(dependency_gaps)
                measurement_status = STATUS_BLOCKED
            elif profile_state == "MEASURED":
                if any(item.get("is_test_double") for item in results):
                    profile_blockers.append(BLOCKER_TEST_DOUBLE)
                    profile_details.append("not_measured_test_double_runner")
                    measurement_status = STATUS_BLOCKED
                else:
                    measurement_status = STATUS_MEASURED
            elif profile_state == "RUNTIME_OBSERVED":
                measurement_status = STATUS_RUNTIME_OBSERVED
            else:
                profile_blockers.append(BLOCKER_PROFILE_EXECUTION_FAILED)
                profile_details.append(f"unexpected_profile_state:{profile_state}")
                measurement_status = STATUS_BLOCKED
        elif runner is not None and not rows and not profile_blockers:
            profile_blockers.append(BLOCKER_DATASET_UNAVAILABLE)
            profile_details.append("dataset_no_rows")

        # -- per-profile artifact (deterministic)
        artifact_payload = build_profile_artifact(
            profile_name=profile_name,
            manifest=manifest,
            profile_block=profile_block,
            case_set_hash=actual_case_hash or declared_case_hash,
            rows=rows,
            results=results,
            measurement_status=measurement_status,
            blocker_codes=profile_blockers,
            blocker_details=profile_details,
            preflight_profile_result=preflight_profile,
        )

        # -- measurement attestation is mandatory for MEASURED. The artifact
        # file holds the measurement facts only; the attestation is written
        # as a separate file and its ``artifact_hash`` binds to the facts
        # artifact hash (deterministic, no self-reference).
        attestation_path = None
        attestation_hash = None
        if measurement_status == STATUS_MEASURED:
            attestation = None
            first_candidate = None
            for item in results:
                candidate = item.get("measurement_attestation")
                if not candidate:
                    continue
                if first_candidate is None:
                    first_candidate = candidate
                # The measurement owner's attestation must be scoped to this
                # profile; a foreign or container attestation is never taken.
                if isinstance(candidate, Mapping) and candidate.get("profile_id") == profile_name:
                    attestation = candidate
                    break
                if not isinstance(candidate, Mapping):
                    attestation = candidate
                    break
            if attestation is None:
                # A present-but-foreign attestation is an INVALID attestation
                # (the measurement owner misbehaved), never a silent missing.
                attestation = first_candidate
            artifact_text = serialize_json(artifact_payload)
            artifact_hash = text_sha256(artifact_text)
            evidence_ref = str(artifact_payload.get("evidence_ref") or "")
            attestation_gap = validate_measurement_attestation(
                attestation,
                profile_id=profile_name,
                measurement_status=STATUS_MEASURED,
                artifact_hash=artifact_hash,
                fingerprint_hash=str(artifact_payload.get("fingerprint_hash") or ""),
                evidence_ref=evidence_ref,
            )
            if attestation_gap is not None:
                measurement_status = STATUS_BLOCKED
                artifact_payload["measurement_status"] = STATUS_BLOCKED
                artifact_payload["blocker_codes"] = sorted(
                    set(artifact_payload["blocker_codes"]) | {attestation_gap}
                )
                artifact_payload["blocker_details"] = sorted(
                    set(artifact_payload["blocker_details"]) | {attestation_gap}
                )
            else:
                attestation_relpath = (
                    f"profiles/{profile_name}.measurement-attestation.json"
                )
                attestation_text = serialize_json(attestation)
                publisher.write(attestation_relpath, attestation_text)
                attestation_hash = text_sha256(attestation_text)
                attestation_path = attestation_relpath

        artifact_relpath = f"profiles/{profile_name}.json"
        artifact_text = serialize_json(artifact_payload)
        publisher.write(artifact_relpath, artifact_text)
        artifact_hash = text_sha256(artifact_text)
        profiles_block[profile_name] = {
            "profile_id": profile_name,
            "measurement_status": measurement_status,
            "blocker_codes": artifact_payload["blocker_codes"],
            "artifact": {
                "path": f"profiles/{profile_name}.json",
                "artifact_hash": artifact_hash,
            },
            "measurement_attestation": (
                {
                    "path": f"profiles/{profile_name}.measurement-attestation.json",
                    "sha256": attestation_hash,
                }
                if attestation_path is not None
                else None
            ),
        }
        profiles.append(
            {
                "profile_id": profile_name,
                "runtime_adapter": artifact_payload["runtime_adapter"],
                "dataset_version": artifact_payload["dataset_version"],
                "case_set_hash": artifact_payload["case_set_hash"],
                "corpus_snapshot": artifact_payload["corpus_snapshot"],
                "knowledge_snapshot": artifact_payload["knowledge_snapshot"],
                "model_config_ref": artifact_payload["model_config_ref"],
                "judge_config_ref": artifact_payload["judge_config_ref"],
                "embedding_config_ref": artifact_payload["embedding_config_ref"],
                "security_policy_ref": artifact_payload["security_policy_ref"],
                "formal_credential_ref": artifact_payload["formal_credential_ref"],
                "reviewer_attestation_ref": artifact_payload["reviewer_attestation_ref"],
                "budget_approval_ref": artifact_payload["budget_approval_ref"],
                "runtime_attestation_ref": artifact_payload["runtime_attestation_ref"],
                "output_artifact_path": f"profiles/{profile_name}.json",
                "output_artifact_hash": artifact_hash,
                "measurement_status": measurement_status,
                "blocker_codes": artifact_payload["blocker_codes"],
            }
        )

    overall_status = _aggregate_overall(profiles)

    environment = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "entry_version": ENTRY_VERSION,
        "manifest_version": MANIFEST_VERSION,
        "blocker_vocabulary_version": BLOCKER_VOCABULARY_VERSION,
    }
    git_sha, git_dirty = get_git_info()
    environment["git_commit_sha"] = git_sha
    environment["git_working_tree_dirty"] = git_dirty

    report = {
        "entry_version": ENTRY_VERSION,
        "manifest_version": MANIFEST_VERSION,
        "eval_run_id": str(manifest.get("eval_run_id") or ""),
        "overall_status": overall_status,
        "dataset_path": str(dataset_path),
        "dataset_sha256": dataset_sha,
        "declared_dataset_hash": declared_dataset_hash,
        "case_set_hash": actual_case_hash or declared_case_hash,
        "declared_case_set_hash": declared_case_hash,
        "candidate_count_declared": declared_count,
        "candidate_count_actual": len(rows),
        "preflight": preflight_dict,
        "profiles": profiles,
        "environment": environment,
        "command": {
            "argv": list(sys.argv),
            "check_only": check_only,
            "profile_runtime_factory": (
                getattr(profile_runtime_factory, "__module__", "") + ":"
                + getattr(profile_runtime_factory, "__name__", "")
                if profile_runtime_factory is not None
                else ""
            ),
        },
        "artifact_refs": {
            "report": {"path": "benchmark_report.json"},
            "profiles": {
                profile_name: {
                    "path": f"profiles/{profile_name}.json",
                    "sha256": profiles_block[profile_name]["artifact"]["artifact_hash"],
                    "measurement_attestation": profiles_block[profile_name].get(
                        "measurement_attestation"
                    ),
                }
                for profile_name in CANONICAL_PROFILES
            },
        },
        "reproduce_command": _reproduce_command(),
    }
    # PHASE22 final engineering closure (P0-7): the report MUST NOT carry a
    # self-referential checksum. ``report_integrity`` only documents the
    # sidecar protocol; the actual SHA-256 is computed from the on-disk
    # final bytes after atomic rename and persisted to
    # ``benchmark_report.json.sha256``.
    report["report_integrity"] = {
        "algorithm": "sha256",
        "sidecar_path": "benchmark_report.json.sha256",
        "encoding": "utf-8",
        "line_endings": "lf",
    }
    report.pop("report_checksum_sidecar", None)

    # PHASE22 (Slice A): atomic publish. Write the report + sidecar to the
    # staging directory first, then rename once every artifact is on disk.
    env_payload = serialize_json(environment)
    env_hash = canonical_sha256_hex(json.loads(env_payload))
    publisher.write("environment.json", env_payload)
    publisher.write("environment.json.sha256", env_hash + "\n")
    publisher.write("benchmark_report.json", serialize_json(report))
    publisher.write_sidecar_for("benchmark_report.json")

    # Update the report's environment reference now that the staging bytes
    # are stable; the on-disk file is the source of truth and the report
    # in-process copy is the verifier view.
    report["artifact_refs"]["environment"] = {
        "path": "environment.json",
        "sha256": env_hash,
    }

    try:
        publisher.commit()
    except OutputPathUnavailable as exc:
        publisher.discard()
        return _error_report(
            manifest=manifest,
            output_dir=output_dir,
            reason=BLOCKER_OUTPUT_PATH_UNAVAILABLE,
            blocker_details=[f"commit_failed:{exc}"],
        )

    return report


def _manifest_profile(
    manifest: Mapping[str, Any], profile_name: str
) -> dict[str, Any]:
    for entry in manifest.get("profiles") or []:
        if isinstance(entry, Mapping) and entry.get("profile_name") == profile_name:
            return dict(entry)
    return {}


def _aggregate_overall(profiles: list[dict[str, Any]]) -> str:
    statuses = [str(profile.get("measurement_status") or "") for profile in profiles]
    if any(status == STATUS_ERROR for status in statuses):
        return STATUS_ERROR
    if all(status == STATUS_MEASURED for status in statuses):
        # Comparability over the shared comparison dimensions: every MEASURED
        # profile must agree on dataset / case set / corpus / knowledge /
        # model / judge / embedding / security scope. A disagreement makes the
        # whole run INCOMPARABLE — never a quality conclusion.
        first = profiles[0]
        for other in profiles[1:]:
            for dimension in (
                "case_set_hash",
                "corpus_snapshot",
                "knowledge_snapshot",
                "model_config_ref",
                "judge_config_ref",
                "embedding_config_ref",
                "security_policy_ref",
            ):
                if first.get(dimension) != other.get(dimension):
                    return STATUS_INCOMPARABLE
        return STATUS_MEASURED
    if any(status == STATUS_BLOCKED for status in statuses):
        return STATUS_BLOCKED
    if any(status == STATUS_RUNTIME_OBSERVED for status in statuses):
        return STATUS_RUNTIME_OBSERVED
    if all(status == STATUS_READY for status in statuses):
        return STATUS_READY
    return STATUS_BLOCKED


def _incomparable_report(
    *,
    manifest: Mapping[str, Any],
    preflight_dict: Mapping[str, Any],
    gap_codes: list[str],
    dataset_sha: Optional[str],
    declared_dataset_hash: str,
    case_set_hash: str,
    declared_case_set_hash: str,
    declared_count: int,
    actual_count: int,
    publisher: _AtomicArtifactPublisher,
) -> dict[str, Any]:
    """Report for a preflight INCOMPARABLE run: every profile is marked
    INCOMPARABLE with the mismatch codes; execution is skipped. The
    publisher is used to atomically publish the report and profile
    artifacts via the staging directory.
    """
    profiles = []
    profiles_block: dict[str, Any] = {}
    for profile_name in CANONICAL_PROFILES:
        artifact_payload = {
            "profile_id": profile_name,
            "runtime_adapter": FORMAL_ADAPTER_REFS.get(profile_name, ""),
            "dataset_version": str(manifest.get("dataset_version") or ""),
            "case_set_hash": case_set_hash,
            "corpus_snapshot": "",
            "knowledge_snapshot": "",
            "model_config_ref": "",
            "judge_config_ref": "",
            "embedding_config_ref": "",
            "security_policy_ref": "",
            "formal_credential_ref": "",
            "reviewer_attestation_ref": "",
            "budget_approval_ref": "",
            "runtime_attestation_ref": "",
            "measurement_status": STATUS_INCOMPARABLE,
            "blocker_codes": [BLOCKER_PROFILES_INCOMPARABLE],
            "blocker_details": list(gap_codes),
            "per_case_results": [],
        }
        artifact_relpath = f"profiles/{profile_name}.json"
        artifact_text = serialize_json(artifact_payload)
        publisher.write(artifact_relpath, artifact_text)
        artifact_hash = text_sha256(artifact_text)
        profiles_block[profile_name] = {
            "profile_id": profile_name,
            "measurement_status": STATUS_INCOMPARABLE,
            "blocker_codes": [BLOCKER_PROFILES_INCOMPARABLE],
            "artifact": {
                "path": artifact_relpath,
                "artifact_hash": artifact_hash,
            },
            "measurement_attestation": None,
        }
        profiles.append(
            {
                "profile_id": profile_name,
                "runtime_adapter": artifact_payload["runtime_adapter"],
                "dataset_version": artifact_payload["dataset_version"],
                "case_set_hash": case_set_hash,
                "corpus_snapshot": "",
                "knowledge_snapshot": "",
                "model_config_ref": "",
                "judge_config_ref": "",
                "embedding_config_ref": "",
                "security_policy_ref": "",
                "formal_credential_ref": "",
                "reviewer_attestation_ref": "",
                "budget_approval_ref": "",
                "runtime_attestation_ref": "",
                "output_artifact_path": artifact_relpath,
                "output_artifact_hash": artifact_hash,
                "measurement_status": STATUS_INCOMPARABLE,
                "blocker_codes": [BLOCKER_PROFILES_INCOMPARABLE],
            }
        )
    git_sha, git_dirty = get_git_info()
    report = {
        "entry_version": ENTRY_VERSION,
        "manifest_version": MANIFEST_VERSION,
        "eval_run_id": str(manifest.get("eval_run_id") or ""),
        "overall_status": STATUS_INCOMPARABLE,
        "dataset_path": str(manifest.get("dataset_path") or ""),
        "dataset_sha256": dataset_sha,
        "declared_dataset_hash": declared_dataset_hash,
        "case_set_hash": case_set_hash,
        "declared_case_set_hash": declared_case_set_hash,
        "candidate_count_declared": declared_count,
        "candidate_count_actual": actual_count,
        "preflight": dict(preflight_dict),
        "profiles": profiles,
        "environment": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "entry_version": ENTRY_VERSION,
            "manifest_version": MANIFEST_VERSION,
            "blocker_vocabulary_version": BLOCKER_VOCABULARY_VERSION,
            "git_commit_sha": git_sha,
            "git_working_tree_dirty": git_dirty,
        },
        "command": {
            "argv": list(sys.argv),
            "check_only": False,
            "profile_runtime_factory": "",
        },
        "artifact_refs": {
            "report": {"path": "benchmark_report.json"},
            "profiles": {
                profile_name: {
                    "path": f"profiles/{profile_name}.json",
                    "sha256": profiles_block[profile_name]["artifact"]["artifact_hash"],
                    "measurement_attestation": None,
                }
                for profile_name in CANONICAL_PROFILES
            },
        },
        "reproduce_command": _reproduce_command(),
    }
    # PHASE22 final engineering closure (P0-7): the report MUST NOT carry a
    # self-referential checksum. ``report_integrity`` only documents the
    # sidecar protocol; the actual SHA-256 is computed from the on-disk
    # final bytes after atomic rename and persisted to
    # ``benchmark_report.json.sha256``.
    report["report_integrity"] = {
        "algorithm": "sha256",
        "sidecar_path": "benchmark_report.json.sha256",
        "encoding": "utf-8",
        "line_endings": "lf",
    }
    report.pop("report_checksum_sidecar", None)
    publisher.write("benchmark_report.json", serialize_json(report))
    publisher.write_sidecar_for("benchmark_report.json")
    return report


def _error_report(
    *,
    manifest: Mapping[str, Any],
    output_dir: Path,
    reason: str,
    blocker_details: list[str],
) -> dict[str, Any]:
    report = {
        "entry_version": ENTRY_VERSION,
        "manifest_version": MANIFEST_VERSION,
        "eval_run_id": str(manifest.get("eval_run_id") or "") if isinstance(manifest, Mapping) else "",
        "overall_status": STATUS_ERROR,
        "error": reason,
        "blocker_details": blocker_details,
        "profiles": [],
        "artifact_refs": {},
        "reproduce_command": _reproduce_command(),
    }
    return report


def _reproduce_command() -> str:
    return "python -m tools.evals.zuno.rag_eval.run_phase22_formal_benchmark --manifest <MANIFEST_JSON> --output <ARTIFACT_DIR>"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class OutputWriteError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _read_input(path: str) -> tuple[Optional[Mapping[str, Any]], Optional[str]]:
    try:
        payload = read_json(Path(path))
    except FileNotFoundError:
        return None, "input_file_not_found"
    except IsADirectoryError:
        return None, "input_path_is_directory"
    except PermissionError:
        return None, "input_file_not_readable"
    except UnicodeDecodeError:
        return None, "input_invalid_utf8"
    except json.JSONDecodeError:
        return None, "input_invalid_json"
    except ValueError as exc:
        if "invalid JSON constant" in str(exc):
            return None, "input_invalid_number"
        return None, "input_invalid_json"
    except OSError:
        return None, "input_file_not_readable"
    if not isinstance(payload, Mapping):
        return None, "input_not_object"
    return payload, None


def _import_factory_from_ref(factory_ref: Optional[str]) -> tuple[Optional[Callable[..., Any]], Optional[str]]:
    if not factory_ref:
        return None, None
    try:
        return _import_factory(factory_ref), None
    except (ImportError, AttributeError, ValueError, TypeError):
        return None, "factory_import_failed"


class _FixedExitArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:  # pragma: no cover  (defensive)
        sys.stderr.write("formal_benchmark: argparse_error\n")
        sys.stderr.write(self.format_usage())
        raise SystemExit(EXIT_ERROR)


def run(argv: Optional[list] = None) -> int:
    parser = _FixedExitArgumentParser(
        prog="run_phase22_formal_benchmark",
        description=(
            "PHASE22 formal benchmark execution entry. Validates the formal "
            "manifest (dataset/case hashes + attestations), executes the "
            "profiles that may run, and writes immutable artifacts with "
            "blockers for the profiles that cannot run."
        ),
    )
    parser.add_argument("--manifest", required=True, help="Path to the formal benchmark manifest JSON.")
    parser.add_argument("--output", required=True, help="Artifact output directory (write-once).")
    parser.add_argument(
        "--profile-runtime-factory",
        default=None,
        help="Optional MODULE:ATTR profile runtime factory (tests / composition root).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate everything but do not execute profiles.",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else EXIT_ERROR

    manifest, read_error = _read_input(args.manifest)
    if read_error is not None:
        sys.stderr.write("formal_benchmark: " + read_error + "\n")
        return EXIT_ERROR

    factory, factory_error = _import_factory_from_ref(args.profile_runtime_factory)
    if factory_error is not None:
        sys.stderr.write("formal_benchmark: " + factory_error + "\n")
        return EXIT_ERROR

    try:
        report = run_formal_benchmark(
            manifest,
            Path(args.output),
            profile_runtime_factory=factory,
            check_only=bool(args.check_only),
        )
    except Exception:
        # PHASE22 (Slice A): an exception inside the orchestrator must not
        # be silently swallowed. The error report is written through the
        # atomic publisher so we never leave a partial output directory.
        error_publisher = _AtomicArtifactPublisher(
            output_dir=Path(args.output),
            run_id=str((manifest or {}).get("eval_run_id") or "run"),
        )
        try:
            error_publisher.open()
        except (OutputPathExists, OutputPathUnavailable):
            # Final output already exists or staging unavailable; surface
            # the error without writing any artifact.
            sys.stderr.write("formal_benchmark: output_path_unavailable\n")
            return EXIT_ERROR
        error_report = _error_report(
            manifest=manifest,
            output_dir=Path(args.output),
            reason=BLOCKER_INTERNAL_ERROR,
            blocker_details=["entry_internal_error"],
        )
        error_report["report_integrity"] = {
            "algorithm": "sha256",
            "sidecar_path": "benchmark_report.json.sha256",
            "encoding": "utf-8",
            "line_endings": "lf",
        }
        error_publisher.write("benchmark_report.json", serialize_json(error_report))
        error_publisher.write_sidecar_for("benchmark_report.json")
        try:
            error_publisher.commit()
        except OutputPathUnavailable:
            error_publisher.discard()
            sys.stderr.write("formal_benchmark: output_write_failed\n")
            return EXIT_ERROR
        return EXIT_ERROR

    return STATUS_TO_EXIT.get(str(report.get("overall_status")), EXIT_ERROR)


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
