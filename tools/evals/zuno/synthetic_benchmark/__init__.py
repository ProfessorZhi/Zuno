"""PHASE22 synthetic benchmark — DerivationSpec kernel (candidate_only).

This package is a small, deterministic kernel that validates a synthetic
benchmark case by **independently re-deriving** the expected answer from a
declarative :class:`DerivationSpec` and the structured inputs
(facts, graph, versions) it is given.

It is NOT a measurement of the Zuno production runtime and NOT a substitute
for human-review grading. The whole package is labelled ``candidate_only``
in the evidence doc.

The kernel deliberately avoids reading the prefilled ``expected_answer``
field on the case as input to derivation; the only thing it consumes from
the case is the declarative :class:`DerivationSpec` plus the inputs the
spec names. The final answer is then compared against ``expected_answer``
to score the case.
"""

from tools.evals.zuno.synthetic_benchmark.spec import (  # noqa: F401
    CASE_SCHEMA_VERSION,
    CaseValidation,
    DerivationSpec,
    DirectedEdge,
    Fact,
    RelationDirection,
    SourceSpan,
    TemporalVersion,
    derive_final_answer,
    spec_for_case_type,
    validate_case,
)

__all__ = [
    "CASE_SCHEMA_VERSION",
    "CaseValidation",
    "DerivationSpec",
    "DirectedEdge",
    "Fact",
    "RelationDirection",
    "SourceSpan",
    "TemporalVersion",
    "derive_final_answer",
    "spec_for_case_type",
    "validate_case",
]
