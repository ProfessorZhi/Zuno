# PHASE22 Release Decision Engine

> work package: `MM-PHASE22-BENCHMARK-RELEASE-DECISION`
> PR: <https://github.com/ProfessorZhi/Zuno/pull/63>
> branch: `agent/minimax/phase22-release-decision-engine`
> base: `docs/phase22-agent-performance-governance` @ `3fa2f4734c88f9e4510cf0c2f3a99d82b06226a1`

This document records the PR for `P22-T02` (Benchmark Comparison and Release
Decision). The work package introduces a deterministic, fail-closed
PHASE22 Benchmark Comparison and Release Decision Engine that consumes only
already-generated four-profile result manifests and emits an immutable
Evidence Pack.

## 1. Goal and Boundary

The Release Decision Engine is intentionally independent:

* it does **not** run benchmarks, call models, generate traces or touch
  Candidates / Datasets;
* it does **not** import `runtime_evidence_binding.py` (PR #60) or
  `benchmark_preflight.py` (PR #61);
* it is consumed via a stable JSON contract (`evaluate_release_decision`)
  plus a CLI (`run_phase22_release_decision.py`) that writes an
  immutable evidence pack;
* Reason codes come from a fixed closed set; raw input values, paths,
  exception text and secrets are never embedded in any output field.

## 2. CLI Exit Code Contract

The CLI maps each decision status to a deterministic exit code. The same
mapping is also exposed as the ``exit_code`` field inside the evidence
pack, so downstream tools can rely on either the integer exit code or
the value in the JSON.

```text
0 -- PASSED
1 -- FAILED
2 -- BLOCKED
3 -- INCOMPARABLE
4 -- ERROR or CLI read/write/parse failure
```

``BLOCKED`` is also returned when the input file is missing or unreadable.
``ERROR`` is returned when the output target cannot be written. The CLI
never prints tracebacks, raw OS errors, absolute paths, or usernames.

## 3. Status semantics

| Status        | Meaning                                                                              |
| ------------- | ------------------------------------------------------------------------------------ |
| PASSED        | comparable, fully measured, every required gate present and passing.                 |
| FAILED        | comparable, fully measured, all required gates present, at least one threshold fails, or a high-risk failure bucket is present. |
| BLOCKED       | missing profile, profile not measured, missing required gate block or evidence.      |
| INCOMPARABLE  | at least one comparability fingerprint dimension differs across profiles.            |
| ERROR         | structural / type / range / hash error in the input.                                 |

Total average never masks critical slice, safety or citation failures;
those failures fire individual closed-set reasons that map to FAILED.

## 4. Required Gates (BLOCKED on absence)

The following top-level blocks are **required**. If any of them is absent
or contains an invalid shape, the decision is ``BLOCKED`` (or ``ERROR``
when the block is the wrong shape) and never silently becomes ``PASSED``.

* ``core_five``                -> ``core_five_block_missing`` / ``core_five_metric_missing``
* ``citation_safety``          -> ``citation_safety_block_missing`` / ``citation_safety_metric_missing``
* ``critical_slice``           -> ``critical_slice_block_missing``
* ``critical_slice_baseline``  -> ``critical_slice_baseline_block_missing``
* ``agent_efficiency``         -> ``agent_efficiency_block_missing`` / ``agent_efficiency_metric_missing``
* ``cost_latency_budget``      -> ``cost_latency_budget_block_missing`` / ``cost_latency_metric_missing``
* ``failure_buckets``          -> ``failure_buckets_block_missing``
* ``evidence_refs``            -> ``evidence_missing``

The comparability fingerprint dimensions are also required; missing
dimensions trigger ``fingerprint_dimension_missing`` and an ``INCOMPARABLE``
decision.

## 5. Comparability Reason Cleanup

Only the dimensions whose value actually differs across profiles emit a
``<dimension>_mismatch`` reason; ``fingerprint_dimension_missing`` is
reserved for genuinely missing dimensions. The gate's reason reflects the
actual mismatch dimension rather than a placeholder string.

## 6. Path Privacy

The evidence pack JSON does **not** contain ``cli_input_path``,
``cli_output_path``, the absolute Windows path of any input / output,
``/Users``, ``/home``, ``/tmp``, ``Alice``, ``Bob`` (test usernames), or
any raw path string. The same input executed from two independent
``tmp_path`` directories produces byte-identical evidence packs.

## 7. Files added or modified

```text
tools/evals/zuno/rag_eval/release_decision.py
tools/evals/zuno/rag_eval/run_phase22_release_decision.py
tools/evals/zuno/rag_eval/__init__.py
tests/evals/test_phase22_release_decision.py
docs/evidence/goal05-phase22-release-decision-engine.md
docs/governance/agent-performance/records/pr-63.json
```

## 8. Commit / Push / PR

* PR: open draft, base ``docs/phase22-agent-performance-governance``.
* Commits use ordinary Commit (no reset, rebase, amend, cherry-pick, force push).
* Commit trailers preserved on every commit:
  ``Agent: Claude-Code``, ``Provider: MiniMax``, ``Model: MiniMax-M3``,
  ``Agent-Mode: Goal``, ``Human-Owner: ProfessorZhi``,
  ``Architecture-Reviewer: ChatGPT``,
  ``Work-Package: MM-PHASE22-BENCHMARK-RELEASE-DECISION``.

## 9. Tests / CI / Verification (executed)

* ``python -m pytest tests/evals/test_phase22_release_decision.py -q -p no:cacheprovider``
  -- 39 passed (the release-decision focused file).
* ``python -m compileall -q tools/evals/zuno/rag_eval/release_decision.py \
  tools/evals/zuno/rag_eval/run_phase22_release_decision.py \
  tools/evals/zuno/rag_eval/__init__.py \
  tests/evals/test_phase22_release_decision.py``.
* ``python tools/scripts/verify_repo_structure.py`` -- passed.
* ``python tools/scripts/verify_current_program.py`` -- passed.
* ``git diff --check`` -- clean.

## 10. Performance log

The focused test file executes in well under one second on the local
Windows / Python 3.12 environment; each ``evaluate_release_decision``
call runs in microseconds and the CLI read / write round trip adds no
measurable overhead. Memory footprint is bounded by input size and the
small deterministic constants declared in ``release_decision.py``.

## 11. Items intentionally not run

* No real model calls, real benchmark runs, Docker, paid provider
  traffic, full-stack frontend build, full pytest of every package.
* No full PHASE22 E2E -- we only ship the deterministic decision engine
  and its CLI / contract; the actual fixed benchmark that consumes this
  engine is owned by P22-T01 / P22-T02 evidence and lives outside this PR.

## 12. Not Claimed

* No claim that the engine determines real release readiness; the engine
  is a deterministic decision computer over already-produced manifests.
  Real "production ready" / "quality proven" claims remain owned by
  PHASE22-T06 and ``docs/status/production-readiness.md``.
* No claim that this engine inherits or replaces PR #60 / PR #61 logic;
  the engine intentionally consumes a stable JSON contract.
* No claim that the Fixture-driven PASSED in tests represents real-world
  PASSED; fixtures only prove that the contract is self-consistent.

## 13. Reproduction template

```bash
python -m tools.evals.zuno.rag_eval.run_phase22_release_decision \
    --input-json <INPUT_JSON_PATH> \
    --output-json <OUTPUT_JSON_PATH>
```

The exact ``reproduce_command_template`` is also emitted inside every
evidence pack so that other tools can replay the same input. The
``exit_code`` field in the evidence pack matches the process exit code.
