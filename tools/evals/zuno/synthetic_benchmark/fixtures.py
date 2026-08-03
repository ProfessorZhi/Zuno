"""Three representative synthetic-benchmark cases for the DerivationSpec kernel.

These three cases are intentionally tiny, fully fictional, and fully
deterministic — they exist to prove the kernel's three reasoning shapes:

1. ``syn_sd_001`` (single_doc_fact): derive an owner name from a
   structured Fact and its SourceSpan.
2. ``syn_gp_001`` (graph_path): traverse a 2-hop path
   ``Person -owns-> Product -in_division-> Division``.
3. ``syn_tv_001`` (temporal_version): pick the v2 release notes of a
   product given ``query_time = 2026-08-03`` when v1 was effective
   2025-01-01 and v2 supersedes it as of 2026-03-01.

The expected answers are written by the same author as the inputs —
this is fine for a ``candidate_only`` kernel proof, and is exactly the
same honesty property PR #100 records in its architecture proposal §5.
"""

from __future__ import annotations

import hashlib
from typing import Any

from tools.evals.zuno.synthetic_benchmark.spec import (
    DirectedEdge,
    Fact,
    RelationDirection,
    SourceSpan,
    TemporalVersion,
    _Inputs,
    GraphPathSpec,
    SingleDocFactSpec,
    TemporalVersionSpec,
    _SpecKind,
)

GENERATION_SEED = "phase22-cc-mm1-fixtures-v1"


# --- Case 1: single_doc_fact ---------------------------------------------


def _sd_inputs() -> _Inputs:
    span = SourceSpan(
        doc_id="doc_axis9_release_notes",
        version="v9.4.0",
        text=(
            "Axis-9 Industrial Controller release notes. "
            "Primary owner: Haruto Soma."
        ),
    )
    fact = Fact(
        fact_id="fact_axis9_owner",
        span=span,
        answer_field="owner",
        value="Haruto Soma",
    )
    return _Inputs(facts={fact.fact_id: fact})


def _sd_spec() -> SingleDocFactSpec:
    inputs = _sd_inputs()
    spec = SingleDocFactSpec(
        kind=_SpecKind.SINGLE_DOC_FACT,
        case_id="syn_sd_001",
        generation_seed=GENERATION_SEED,
        input_hash=inputs.input_digest(),
        fact_id="fact_axis9_owner",
        answer_field="owner",
    )
    return spec


SINGLE_DOC_FACT_CASE: dict[str, Any] = {
    "case_id": "syn_sd_001",
    "question": "Who is the primary owner of the Axis-9 Industrial Controller?",
    "question_type": "single_doc_fact",
    "expected_answer": "Haruto Soma",
    "security_scope": "perm_global_open",
    "build": {
        "spec": _sd_spec,
        "inputs": _sd_inputs,
    },
}


# --- Case 2: graph_path ---------------------------------------------------


def _gp_inputs() -> _Inputs:
    edges = (
        DirectedEdge(
            kind="owns",
            from_id="emp_haruto_soma",
            to_id="prod_axis_9",
            direction=RelationDirection.OUTGOING,
        ),
        DirectedEdge(
            kind="in_division",
            from_id="prod_axis_9",
            to_id="div_automation_systems",
            direction=RelationDirection.OUTGOING,
        ),
    )
    return _Inputs(graph=edges)


def _gp_spec() -> GraphPathSpec:
    inputs = _gp_inputs()
    return GraphPathSpec(
        kind=_SpecKind.GRAPH_PATH,
        case_id="syn_gp_001",
        generation_seed=GENERATION_SEED,
        input_hash=inputs.input_digest(),
        edges=(
            ("owns", "emp_haruto_soma", "prod_axis_9", RelationDirection.OUTGOING),
            (
                "in_division",
                "prod_axis_9",
                "div_automation_systems",
                RelationDirection.OUTGOING,
            ),
        ),
    )


GRAPH_PATH_CASE: dict[str, Any] = {
    "case_id": "syn_gp_001",
    "question": (
        "Which division owns the Axis-9 product via the primary owner?"
    ),
    "question_type": "graph_path",
    # The kernel returns the final to_id of the path.
    "expected_answer": "div_automation_systems",
    "security_scope": "perm_global_open",
    "build": {
        "spec": _gp_spec,
        "inputs": _gp_inputs,
    },
}


# --- Case 3: temporal_version --------------------------------------------


def _tv_inputs() -> _Inputs:
    v1_span = SourceSpan(
        doc_id="doc_axis9_release_notes_v1",
        version="v9.1.0",
        text="Axis-9 v9.1.0 released 2025-01-15.",
    )
    v2_span = SourceSpan(
        doc_id="doc_axis9_release_notes_v2",
        version="v9.4.0",
        text="Axis-9 v9.4.0 released 2026-03-10; supersedes v9.1.0.",
    )
    versions = (
        TemporalVersion(
            artifact_id="prod_axis_9_release_notes",
            version="v9.1.0",
            effective_at="2025-01-15",
            superseded_by=("v9.4.0",),
            span=v1_span,
        ),
        TemporalVersion(
            artifact_id="prod_axis_9_release_notes",
            version="v9.4.0",
            effective_at="2026-03-10",
            superseded_by=(),
            span=v2_span,
        ),
    )
    return _Inputs(versions=versions)


def _tv_spec() -> TemporalVersionSpec:
    inputs = _tv_inputs()
    return TemporalVersionSpec(
        kind=_SpecKind.TEMPORAL_VERSION,
        case_id="syn_tv_001",
        generation_seed=GENERATION_SEED,
        input_hash=inputs.input_digest(),
        artifact_id="prod_axis_9_release_notes",
        query_time="2026-08-03",
    )


TEMPORAL_VERSION_CASE: dict[str, Any] = {
    "case_id": "syn_tv_001",
    "question": (
        "Which Axis-9 release notes are current on 2026-08-03?"
    ),
    "question_type": "temporal_version",
    "expected_answer": "v9.4.0",
    "security_scope": "perm_global_open",
    "build": {
        "spec": _tv_spec,
        "inputs": _tv_inputs,
    },
}


# --- Registry -------------------------------------------------------------


ALL_CASES: tuple[dict[str, Any], ...] = (
    SINGLE_DOC_FACT_CASE,
    GRAPH_PATH_CASE,
    TEMPORAL_VERSION_CASE,
)


def registry_input_digest() -> str:
    """Hash the entire fixture registry — used by the reproducibility test."""

    payload = "|".join(c["case_id"] for c in ALL_CASES).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
