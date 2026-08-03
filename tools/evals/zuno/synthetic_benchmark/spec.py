"""DerivationSpec schema + deterministic validator kernel.

This module is intentionally small and side-effect free: every public
function is pure (or hash-only) so the kernel can be embedded into a
larger benchmark without polluting global state.

Three case types are supported by this kernel:

* ``single_doc_fact``  — pick a :class:`Fact` whose :class:`SourceSpan`
  text literally contains the answer substring and whose
  ``answer_field`` is named by the spec.
* ``graph_path``       — walk a directed path of length >= 2 across the
  relation graph, enforcing ``kind``/``from_id``/``to_id`` and
  :class:`RelationDirection` on every edge.
* ``temporal_version`` — pick the version whose ``effective_at`` is the
  largest value that does not exceed ``query_time`` and that is not
  listed in another version's ``superseded_by``.

All three kernels share two obligations:

1. The derived answer must be **literally present** in the chosen
   ``SourceSpan.text``. The validator fails the case otherwise — the
   spec is what the answer comes from, the span is the witness.
2. The validator does NOT consult ``case.expected_answer`` as an input
   to derivation; it only reads it at the end as the comparison target.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, TypeAlias

CASE_SCHEMA_VERSION = "1.0.0"

# --- Structured inputs ----------------------------------------------------


@dataclass(frozen=True)
class SourceSpan:
    """A span of text inside a document version that supports an answer."""

    doc_id: str
    version: str
    text: str

    def contains(self, needle: str) -> bool:
        return _norm(needle) in _norm(self.text)


@dataclass(frozen=True)
class Fact:
    """A structured fact with a supporting :class:`SourceSpan`.

    ``answer_field`` is the *name* of the attribute whose value is the
    answer (for example ``"value_eur"`` or ``"owner"``). The kernel reads
    ``getattr(fact, answer_field)`` to obtain the answer candidate.
    """

    fact_id: str
    span: SourceSpan
    answer_field: str
    value: str

    def candidate_answer(self) -> str:
        return self.value


class RelationDirection(str, Enum):
    OUTGOING = "outgoing"
    INCOMING = "incoming"
    UNDIRECTED = "undirected"


GraphPathHop: TypeAlias = tuple[str, str, str, RelationDirection]


@dataclass(frozen=True)
class DirectedEdge:
    """A single directed edge in the relation graph."""

    kind: str
    from_id: str
    to_id: str
    direction: RelationDirection

    def matches(self, *, kind: str, from_id: str, to_id: str) -> bool:
        """Return True if this edge satisfies the (kind, from, to) tuple.

        ``direction`` is checked separately by the path walker so this
        method only compares the structural triple.
        """
        return (
            self.kind == kind
            and self.from_id == from_id
            and self.to_id == to_id
        )


@dataclass(frozen=True)
class TemporalVersion:
    """A versioned artifact with explicit temporal bookkeeping."""

    artifact_id: str
    version: str
    effective_at: str
    superseded_by: tuple[str, ...] = ()
    span: SourceSpan = None  # type: ignore[assignment]

    def is_current_at(self, query_time: str) -> bool:
        """True iff ``effective_at <= query_time`` and not superseded."""

        if not _le(self.effective_at, query_time):
            return False
        return True


# --- DerivationSpec variants ---------------------------------------------


class _SpecKind(str, Enum):
    SINGLE_DOC_FACT = "single_doc_fact"
    GRAPH_PATH = "graph_path"
    TEMPORAL_VERSION = "temporal_version"


@dataclass(frozen=True)
class _BaseSpec:
    kind: _SpecKind
    case_id: str
    # Generation seed + hashes pinning the inputs. Two runs with the
    # same seed + same input hashes must derive the same final answer.
    generation_seed: str
    input_hash: str

    def spec_fingerprint(self) -> str:
        payload = (
            f"{self.kind.value}|{self.case_id}|"
            f"{self.generation_seed}|{self.input_hash}"
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class SingleDocFactSpec(_BaseSpec):
    """Spec for ``single_doc_fact``: derive answer from a single Fact."""

    fact_id: str
    answer_field: str

    def __post_init__(self) -> None:
        if self.kind != _SpecKind.SINGLE_DOC_FACT:
            raise ValueError(f"wrong kind for SingleDocFactSpec: {self.kind}")


@dataclass(frozen=True)
class GraphPathSpec(_BaseSpec):
    """Spec for ``graph_path``: walk a directed relation path.

    The path is given as an ordered list of (kind, from_id, to_id,
    direction) tuples. The validator must find edges with matching
    ``kind``, ``(from_id, to_id)`` and :class:`RelationDirection`.
    """

    edges: tuple[GraphPathHop, ...]

    def __post_init__(self) -> None:
        if self.kind != _SpecKind.GRAPH_PATH:
            raise ValueError(f"wrong kind for GraphPathSpec: {self.kind}")
        if len(self.edges) < 2:
            raise ValueError("graph_path spec needs >= 2 hops")
        # Contiguity check: edge i.to_id must equal edge i+1.from_id.
        for prev, nxt in zip(self.edges, self.edges[1:]):
            if prev[2] != nxt[1]:
                raise ValueError(
                    f"non-contiguous path: {prev} -> {nxt}"
                )


@dataclass(frozen=True)
class TemporalVersionSpec(_BaseSpec):
    """Spec for ``temporal_version``: pick current version of an artifact."""

    artifact_id: str
    query_time: str

    def __post_init__(self) -> None:
        if self.kind != _SpecKind.TEMPORAL_VERSION:
            raise ValueError(f"wrong kind for TemporalVersionSpec: {self.kind}")


DerivationSpec = (
    SingleDocFactSpec | GraphPathSpec | TemporalVersionSpec
)


# --- Inputs ----------------------------------------------------------------


@dataclass(frozen=True)
class _Inputs:
    facts: dict[str, Fact] = field(default_factory=dict)
    graph: tuple[DirectedEdge, ...] = ()
    versions: tuple[TemporalVersion, ...] = ()

    def input_digest(self) -> str:
        parts: list[bytes] = []
        for fid in sorted(self.facts):
            f = self.facts[fid]
            parts.append(
                f"fact|{fid}|{f.answer_field}|{f.value}|"
                f"{f.span.doc_id}|{f.span.version}|{_norm(f.span.text)}".encode()
            )
        for e in sorted(
            self.graph, key=lambda e: (e.kind, e.from_id, e.to_id, e.direction.value)
        ):
            parts.append(
                f"edge|{e.kind}|{e.from_id}|{e.to_id}|{e.direction.value}".encode()
            )
        for v in sorted(self.versions, key=lambda v: (v.artifact_id, v.version)):
            parts.append(
                f"ver|{v.artifact_id}|{v.version}|{v.effective_at}|"
                f"{','.join(sorted(v.superseded_by))}|"
                f"{v.span.doc_id if v.span else ''}|"
                f"{_norm(v.span.text) if v.span else ''}".encode()
            )
        return hashlib.sha256(b"\n".join(parts)).hexdigest()


# --- Public validator entrypoint ----------------------------------------


@dataclass(frozen=True)
class CaseValidation:
    case_id: str
    ok: bool
    derived_answer: str | None
    reason: str
    spec_fingerprint: str


def spec_for_case_type(case_type: str) -> type[_BaseSpec]:
    """Map a ``question_type`` string to its spec class."""

    mapping = {
        "single_doc_fact": SingleDocFactSpec,
        "graph_path": GraphPathSpec,
        "temporal_version": TemporalVersionSpec,
    }
    if case_type not in mapping:
        raise KeyError(f"unsupported case_type for this kernel: {case_type}")
    return mapping[case_type]


def validate_case(
    *,
    case_id: str,
    spec: DerivationSpec,
    facts: Iterable[Fact] = (),
    graph: Iterable[DirectedEdge] = (),
    versions: Iterable[TemporalVersion] = (),
    expected_answer: str,
    generation_seed: str,
) -> CaseValidation:
    """Validate one synthetic case.

    The kernel:

    1. Builds an ``_Inputs`` digest and refuses to validate unless the
       spec's ``input_hash`` matches the digest (reproducibility gate).
    2. Calls :func:`derive_final_answer` with ONLY the spec + inputs.
       ``expected_answer`` is NOT read until the comparison step.
    3. Compares the derived answer to ``expected_answer`` with the
       same normalisation the spec uses for spans.
    """

    inputs = _Inputs(
        facts={f.fact_id: f for f in facts},
        graph=tuple(graph),
        versions=tuple(versions),
    )
    digest = inputs.input_digest()
    if spec.input_hash != digest:
        return CaseValidation(
            case_id=case_id,
            ok=False,
            derived_answer=None,
            reason=(
                f"input_hash mismatch: spec={spec.input_hash[:12]} "
                f"inputs={digest[:12]}"
            ),
            spec_fingerprint=spec.spec_fingerprint(),
        )

    try:
        derived = derive_final_answer(spec=spec, inputs=inputs)
    except _DerivationError as exc:
        return CaseValidation(
            case_id=case_id,
            ok=False,
            derived_answer=None,
            reason=f"derivation_error: {exc}",
            spec_fingerprint=spec.spec_fingerprint(),
        )

    if not _norm(derived).strip():
        return CaseValidation(
            case_id=case_id,
            ok=False,
            derived_answer=derived,
            reason="derived answer is empty",
            spec_fingerprint=spec.spec_fingerprint(),
        )

    ok = _norm(derived) == _norm(expected_answer)
    return CaseValidation(
        case_id=case_id,
        ok=ok,
        derived_answer=derived,
        reason="" if ok else "derived_answer != expected_answer",
        spec_fingerprint=spec.spec_fingerprint(),
    )


class _DerivationError(Exception):
    pass


# --- Derivation per kind --------------------------------------------------


def derive_final_answer(*, spec: DerivationSpec, inputs: _Inputs) -> str:
    if isinstance(spec, SingleDocFactSpec):
        return _derive_single_doc_fact(spec, inputs)
    if isinstance(spec, GraphPathSpec):
        return _derive_graph_path(spec, inputs)
    if isinstance(spec, TemporalVersionSpec):
        return _derive_temporal_version(spec, inputs)
    raise _DerivationError(f"unknown spec kind: {spec!r}")


def _derive_single_doc_fact(spec: SingleDocFactSpec, inputs: _Inputs) -> str:
    fact = inputs.facts.get(spec.fact_id)
    if fact is None:
        raise _DerivationError(f"unknown fact_id: {spec.fact_id}")
    if fact.answer_field != spec.answer_field:
        raise _DerivationError(
            f"answer_field mismatch: spec={spec.answer_field} "
            f"fact={fact.answer_field}"
        )
    answer = fact.candidate_answer()
    if not fact.span.contains(answer):
        raise _DerivationError(
            f"SourceSpan for fact {spec.fact_id} does not literally "
            f"support answer {answer!r}"
        )
    return answer


def _derive_graph_path(spec: GraphPathSpec, inputs: _Inputs) -> str:
    """Walk the spec's edges through the directed graph.

    Returns the ``to_id`` of the final hop, which is the entity the
    question is asking about. The path is the answer *form*: the
    validator does not pick the entity from the prefilled expected
    answer, it picks it from the spec's last hop.
    """

    # Index edges by (kind, from_id, to_id) for O(1) lookup.
    by_triple: dict[tuple[str, str, str], list[DirectedEdge]] = {}
    for e in inputs.graph:
        by_triple.setdefault((e.kind, e.from_id, e.to_id), []).append(e)

    current_node = spec.edges[0][1]
    for hop_i, (kind, from_id, to_id, expected_direction) in enumerate(spec.edges):
        if from_id != current_node:
            raise _DerivationError(
                f"hop {hop_i}: spec from_id {from_id} does not follow "
                f"prior to_id {current_node}"
            )
        candidates = by_triple.get((kind, from_id, to_id), [])
        if not candidates:
            raise _DerivationError(
                f"hop {hop_i}: no edge matches "
                f"({kind}, {from_id} -> {to_id})"
            )
        if not _has_direction(candidates, expected_direction):
            raise _DerivationError(
                f"hop {hop_i}: direction mismatch for "
                f"({kind}, {from_id} -> {to_id}); "
                f"expected {expected_direction.value}, "
                f"got directions={[c.direction.value for c in candidates]}"
            )
        current_node = to_id
    return current_node


def _has_direction(
    edges: list[DirectedEdge],
    expected_direction: RelationDirection,
) -> bool:
    for edge in edges:
        if edge.direction == expected_direction:
            return True
        if expected_direction == RelationDirection.UNDIRECTED and edge.direction == RelationDirection.UNDIRECTED:
            return True
    return False


def _derive_temporal_version(
    spec: TemporalVersionSpec, inputs: _Inputs
) -> str:
    candidates = [v for v in inputs.versions if v.artifact_id == spec.artifact_id]
    if not candidates:
        raise _DerivationError(
            f"no versions for artifact {spec.artifact_id}"
        )

    # Step 1: filter to versions whose effective_at <= query_time.
    eligible = [v for v in candidates if _le(v.effective_at, spec.query_time)]
    if not eligible:
        raise _DerivationError(
            f"no version of {spec.artifact_id} effective at {spec.query_time}"
        )

    # Step 2: drop versions that are themselves superseded by another
    # *eligible* version. superseded_by here is a version string, not
    # a different artifact, so we look it up in the eligible set.
    superseded = set()
    for v in eligible:
        for sup in v.superseded_by:
            if any(
                other.artifact_id == v.artifact_id and other.version == sup
                for other in eligible
            ):
                superseded.add(v.version)
    current = [v for v in eligible if v.version not in superseded]
    if not current:
        raise _DerivationError(
            f"every eligible version of {spec.artifact_id} is superseded"
        )

    # Step 3: among the current versions, pick the largest effective_at.
    chosen = max(current, key=lambda v: v.effective_at)

    # Step 4: the span must literally contain the version string.
    if chosen.span is None:
        raise _DerivationError(
            f"chosen version {chosen.version} has no supporting span"
        )
    if not chosen.span.contains(chosen.version):
        raise _DerivationError(
            f"SourceSpan for version {chosen.version} does not literally "
            f"support the version string"
        )
    return chosen.version


# --- Helpers --------------------------------------------------------------


_WS = re.compile(r"\s+")


def _norm(s: Any) -> str:
    return _WS.sub(" ", str(s or "")).strip()


def _le(a: str, b: str) -> bool:
    """Lexicographic string ``<=`` — sufficient for ISO-8601 dates."""

    return str(a) <= str(b)
