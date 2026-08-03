"""PHASE22 execution-candidate gate for Derivation Pack + Ingestion Preflight.

This controller-owned gate composes two worker handoffs without creating a
production ingestion path. It is fail-closed: a candidate can enter
``execution_candidate`` only when the DerivationSpec pack validates and the
canonical ingestion preflight is READY.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
READY = "READY_FOR_CANONICAL_INGESTION"
BLOCKED = "BLOCKED_WITH_EXACT_GAP"
EXECUTION_CANDIDATE = "execution_candidate"
BLOCKED_WITH_EXACT_GAP = "blocked_with_exact_gap"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evals.zuno.synthetic_benchmark.fixtures import ALL_CASES, GENERATION_SEED  # noqa: E402
from tools.evals.zuno.synthetic_benchmark.spec import validate_case  # noqa: E402
from tools.scripts.phase22_canonical_ingestion_preflight import run_preflight  # noqa: E402


@dataclass(frozen=True)
class DerivationPackReport:
    status: str
    checked_case_ids: tuple[str, ...]
    failures: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExecutionCandidateDecision:
    status: str
    derivation_pack_status: str
    canonical_ingestion_preflight_status: str
    dependency_status: str
    reasons: tuple[str, ...] = field(default_factory=tuple)


def validate_derivation_pack(
    cases: Iterable[dict[str, Any]] = ALL_CASES,
) -> DerivationPackReport:
    failures: list[str] = []
    checked: list[str] = []
    for case in cases:
        case_id = str(case["case_id"])
        checked.append(case_id)
        spec = case["build"]["spec"]()
        inputs = case["build"]["inputs"]()
        result = validate_case(
            case_id=case_id,
            spec=spec,
            facts=inputs.facts.values(),
            graph=inputs.graph,
            versions=inputs.versions,
            expected_answer=str(case["expected_answer"]),
            generation_seed=GENERATION_SEED,
        )
        if not result.ok:
            failures.append(f"{case_id}: {result.reason}")

    return DerivationPackReport(
        status="legal" if not failures else "invalid",
        checked_case_ids=tuple(checked),
        failures=tuple(failures),
    )


def normalize_preflight_status(preflight_result: Any) -> str:
    """Map worker output fields to the single canonical preflight status.

    Worker B exposed ``verdict``. Controller-owned integration uses only
    ``canonical_ingestion_preflight_status`` downstream.
    """

    if isinstance(preflight_result, str):
        candidate = preflight_result
    elif isinstance(preflight_result, dict):
        candidate = str(preflight_result.get("verdict", ""))
    else:
        candidate = str(getattr(preflight_result, "verdict", ""))

    if candidate == READY:
        return READY
    return BLOCKED


def evaluate_execution_candidate(
    *,
    repo_root: Path = REPO_ROOT,
    cases: Iterable[dict[str, Any]] = ALL_CASES,
    preflight_result: Any | None = None,
) -> ExecutionCandidateDecision:
    derivation = validate_derivation_pack(cases)
    preflight = preflight_result if preflight_result is not None else run_preflight(repo_root)
    preflight_status = normalize_preflight_status(preflight)

    reasons: list[str] = []
    if derivation.status != "legal":
        reasons.extend(f"derivation_pack_invalid: {failure}" for failure in derivation.failures)
    if preflight_status != READY:
        if hasattr(preflight, "describe"):
            detail = preflight.describe()
            if detail:
                reasons.append(f"canonical_ingestion_preflight_blocked: {detail}")
            else:
                reasons.append("canonical_ingestion_preflight_blocked")
        else:
            reasons.append("canonical_ingestion_preflight_blocked")

    dependency_status = "DEPENDENCY_COMPATIBLE" if not reasons else "DEPENDENCY_BLOCKED"
    return ExecutionCandidateDecision(
        status=EXECUTION_CANDIDATE if not reasons else BLOCKED_WITH_EXACT_GAP,
        derivation_pack_status=derivation.status,
        canonical_ingestion_preflight_status=preflight_status,
        dependency_status=dependency_status,
        reasons=tuple(reasons),
    )


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    repo_root = Path(argv[0]).resolve() if argv else REPO_ROOT
    decision = evaluate_execution_candidate(repo_root=repo_root)
    print(f"derivation_pack_status={decision.derivation_pack_status}")
    print(
        "canonical_ingestion_preflight_status="
        f"{decision.canonical_ingestion_preflight_status}"
    )
    print(f"dependency_status={decision.dependency_status}")
    for reason in decision.reasons:
        print(f"reason={reason}")
    print(decision.status)
    return 0 if decision.status == EXECUTION_CANDIDATE else 1


if __name__ == "__main__":
    raise SystemExit(main())
