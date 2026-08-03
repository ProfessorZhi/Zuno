"""Focused unit tests for the DerivationSpec kernel + fixtures.

These tests intentionally stay narrow: they cover the three reasoning
shapes the kernel supports (single_doc_fact, graph_path, temporal_version)
plus the two negative-path promises the brief asks for (wrong direction
fails, wrong temporal version fails), plus the reproducibility gate
(same seed + same inputs => same hash => same derived answer).
"""

from __future__ import annotations

import pytest

from tools.evals.zuno.synthetic_benchmark import (
    CASE_SCHEMA_VERSION,
    DirectedEdge,
    Fact,
    RelationDirection,
    SourceSpan,
    TemporalVersion,
    validate_case,
)
from tools.evals.zuno.synthetic_benchmark.fixtures import (
    ALL_CASES,
    GENERATION_SEED,
    GRAPH_PATH_CASE,
    SINGLE_DOC_FACT_CASE,
    TEMPORAL_VERSION_CASE,
    registry_input_digest,
)
from tools.evals.zuno.synthetic_benchmark.spec import (
    GraphPathSpec,
    SingleDocFactSpec,
    TemporalVersionSpec,
    _Inputs,
    _SpecKind,
    derive_final_answer,
)


def _build(case):
    return case["build"]["spec"](), case["build"]["inputs"]()


# --- happy path: all three fixture cases pass ---------------------------


def test_all_three_fixtures_validate():
    for case in ALL_CASES:
        spec, inputs = _build(case)
        result = validate_case(
            case_id=case["case_id"],
            spec=spec,
            facts=inputs.facts.values(),
            graph=inputs.graph,
            versions=inputs.versions,
            expected_answer=case["expected_answer"],
            generation_seed=GENERATION_SEED,
        )
        assert result.ok, (
            f"{case['case_id']} failed: {result.reason} "
            f"(derived={result.derived_answer!r})"
        )
        assert result.derived_answer == case["expected_answer"]


def test_schema_version_is_pinned():
    # Pin the schema version so we know when a breaking change lands.
    assert CASE_SCHEMA_VERSION == "1.0.0"


# --- single_doc_fact kernel ---------------------------------------------


def test_single_doc_fact_kernel_reads_span_not_expected_answer():
    """Kernel must derive the answer from the span, not from expected_answer."""

    spec, inputs = _build(SINGLE_DOC_FACT_CASE)
    derived = derive_final_answer(spec=spec, inputs=inputs)
    assert derived == "Haruto Soma"
    # The span literally contains the answer.
    fact = list(inputs.facts.values())[0]
    assert fact.span.contains(derived)


def test_single_doc_fact_fails_when_span_does_not_contain_answer():
    """SourceSpan must truly support the answer — mismatch fails the case."""

    spec, _ = _build(SINGLE_DOC_FACT_CASE)
    bad_span = SourceSpan(
        doc_id="doc_axis9_release_notes",
        version="v9.4.0",
        text="Axis-9 release notes — owner TBD.",
    )
    bad_fact = Fact(
        fact_id="fact_axis9_owner",
        span=bad_span,
        answer_field="owner",
        value="Haruto Soma",
    )
    bad_inputs = _Inputs(facts={bad_fact.fact_id: bad_fact})
    with pytest.raises(Exception) as excinfo:
        derive_final_answer(spec=spec, inputs=bad_inputs)
    assert "SourceSpan" in str(excinfo.value) or "literally" in str(excinfo.value)


# --- graph_path kernel ---------------------------------------------------


def test_graph_path_kernel_traverses_two_hops():
    spec, inputs = _build(GRAPH_PATH_CASE)
    derived = derive_final_answer(spec=spec, inputs=inputs)
    assert derived == "div_automation_systems"


def test_graph_path_fails_on_wrong_direction():
    """Wrong relation direction must fail — that's the brief's first promise."""

    spec, _ = _build(GRAPH_PATH_CASE)
    # Flip the second edge to INCOMING — same (kind, from, to) triple,
    # but the direction no longer matches an outgoing walk.
    bad_edges = (
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
            direction=RelationDirection.INCOMING,  # wrong direction
        ),
    )
    bad_inputs = _Inputs(graph=bad_edges)
    with pytest.raises(Exception) as excinfo:
        derive_final_answer(spec=spec, inputs=bad_inputs)
    assert "direction" in str(excinfo.value)


def test_graph_path_fails_on_missing_edge():
    spec, _ = _build(GRAPH_PATH_CASE)
    # Drop the second hop entirely.
    bad_inputs = _Inputs(
        graph=(
            DirectedEdge(
                kind="owns",
                from_id="emp_haruto_soma",
                to_id="prod_axis_9",
                direction=RelationDirection.OUTGOING,
            ),
        )
    )
    with pytest.raises(Exception) as excinfo:
        derive_final_answer(spec=spec, inputs=bad_inputs)
    assert "no edge matches" in str(excinfo.value)


def test_graph_path_rejects_non_contiguous_spec():
    """The spec itself must declare a contiguous path — else it's malformed."""

    with pytest.raises(ValueError):
        GraphPathSpec(
            kind=_SpecKind.GRAPH_PATH,
            case_id="syn_gp_bad",
            generation_seed=GENERATION_SEED,
            input_hash="0" * 64,
            edges=(
                ("owns", "emp_a", "prod_x", RelationDirection.OUTGOING),
                (
                    "in_division",
                    "prod_y",
                    "div_z",
                    RelationDirection.OUTGOING,
                ),  # not contiguous
            ),
        )


# --- temporal_version kernel --------------------------------------------


def test_temporal_version_kernel_picks_current_version():
    spec, inputs = _build(TEMPORAL_VERSION_CASE)
    derived = derive_final_answer(spec=spec, inputs=inputs)
    assert derived == "v9.4.0"


def test_temporal_version_fails_when_querying_before_effective_at():
    """If query_time precedes every effective_at, derivation must fail."""

    spec, _ = _build(TEMPORAL_VERSION_CASE)
    early_inputs = _Inputs(
        versions=(
            TemporalVersion(
                artifact_id="prod_axis_9_release_notes",
                version="v9.1.0",
                effective_at="2025-01-15",
                span=SourceSpan(
                    doc_id="doc_axis9_release_notes_v1",
                    version="v9.1.0",
                    text="Axis-9 v9.1.0 released 2025-01-15.",
                ),
            ),
        )
    )
    early_spec = TemporalVersionSpec(
        kind=_SpecKind.TEMPORAL_VERSION,
        case_id="syn_tv_early",
        generation_seed=GENERATION_SEED,
        input_hash=early_inputs.input_digest(),
        artifact_id="prod_axis_9_release_notes",
        query_time="2024-01-01",  # before anything
    )
    with pytest.raises(Exception) as excinfo:
        derive_final_answer(spec=early_spec, inputs=early_inputs)
    assert "effective" in str(excinfo.value)


def test_temporal_version_picks_v1_when_v2_not_yet_effective():
    """Wrong temporal version (asking for v2 before its effective_at) fails."""

    # Build a *new* spec that asks query_time=2025-06-01, before v9.4.0.
    inputs = _Inputs(
        versions=(
            TemporalVersion(
                artifact_id="prod_axis_9_release_notes",
                version="v9.1.0",
                effective_at="2025-01-15",
                span=SourceSpan(
                    doc_id="doc_axis9_release_notes_v1",
                    version="v9.1.0",
                    text="Axis-9 v9.1.0 released 2025-01-15.",
                ),
            ),
            TemporalVersion(
                artifact_id="prod_axis_9_release_notes",
                version="v9.4.0",
                effective_at="2026-03-10",
                span=SourceSpan(
                    doc_id="doc_axis9_release_notes_v2",
                    version="v9.4.0",
                    text="Axis-9 v9.4.0 released 2026-03-10.",
                ),
            ),
        )
    )
    spec = TemporalVersionSpec(
        kind=_SpecKind.TEMPORAL_VERSION,
        case_id="syn_tv_mid",
        generation_seed=GENERATION_SEED,
        input_hash=inputs.input_digest(),
        artifact_id="prod_axis_9_release_notes",
        query_time="2025-06-01",
    )
    derived = derive_final_answer(spec=spec, inputs=inputs)
    assert derived == "v9.1.0"  # not v9.4.0 — v9.4.0 is not yet effective
    # And asking the validator for v9.4.0 must fail.
    result = validate_case(
        case_id="syn_tv_mid",
        spec=spec,
        versions=inputs.versions,
        expected_answer="v9.4.0",
        generation_seed=GENERATION_SEED,
    )
    assert result.ok is False
    assert result.derived_answer == "v9.1.0"


# --- reproducibility -----------------------------------------------------


def test_same_seed_same_inputs_produce_identical_digest():
    """Same seed + same inputs => same input digest (no hidden randomness)."""

    digest_a = registry_input_digest()
    digest_b = registry_input_digest()
    assert digest_a == digest_b


def test_validate_case_rejects_input_hash_mismatch():
    """A spec whose input_hash disagrees with the actual inputs must fail."""

    spec, inputs = _build(SINGLE_DOC_FACT_CASE)
    # Lie about the input_hash; the validator must refuse to run.
    fake_spec = SingleDocFactSpec(
        kind=spec.kind,
        case_id=spec.case_id,
        generation_seed=spec.generation_seed,
        input_hash="0" * 64,
        fact_id=spec.fact_id,
        answer_field=spec.answer_field,
    )
    result = validate_case(
        case_id=spec.case_id,
        spec=fake_spec,
        facts=inputs.facts.values(),
        expected_answer=SINGLE_DOC_FACT_CASE["expected_answer"],
        generation_seed=GENERATION_SEED,
    )
    assert result.ok is False
    assert "input_hash mismatch" in result.reason


def test_validate_case_rejects_derived_answer_mismatch():
    """When derivation succeeds but the answer disagrees, the case fails."""

    spec, inputs = _build(SINGLE_DOC_FACT_CASE)
    result = validate_case(
        case_id=spec.case_id,
        spec=spec,
        facts=inputs.facts.values(),
        expected_answer="Wrong Name",
        generation_seed=GENERATION_SEED,
    )
    assert result.ok is False
    assert result.derived_answer == "Haruto Soma"
    assert result.reason == "derived_answer != expected_answer"
