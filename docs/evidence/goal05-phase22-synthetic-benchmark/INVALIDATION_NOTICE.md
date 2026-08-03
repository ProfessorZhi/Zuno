# INVALIDATION NOTICE — d7566624 substring MEASURED/PASSED

## Status

The commit `d7566624 chore(phase22-synthetic): re-run benchmark with full infra (6/6 deps)`
on branch `claude-minimax/phase22-synthetic-benchmark` is **INVALIDATED** as
non-canonical simulation.

## What it claimed

- `runtime_dependencies: {"elasticsearch": true, "milvus": true, "neo4j": true, ...}`
- 4 profiles with `measurement_state: MEASURED`
- `release_decision.verdict: PASSED`

## Why it is invalidated

The `ingest_and_run.py` script at that commit used **in-process deterministic
substring matching** against an in-memory copy of the corpus. It did NOT:

1. Submit the 62 documents through the canonical Zuno Ingestion Application
   Service.
2. Produce Canonical Document IR via the formal parser pipeline.
3. Persist Chunk / Entity / Relation through the formal UoW / Repository
   path with ownership / version / effective_at.
4. Write to Elasticsearch BM25, Milvus Vector, or Neo4j Graph through the
   production index adapter contracts.
5. Build a real KnowledgeVersion / Snapshot and activate it.
6. Trigger Index Visibility and Snapshot Activation through the formal
   orchestration path.

The `runtime_dependencies` flags were TCP-connect probes of the live Docker
stack; the script did not require any of those services to perform the
measurement. **Port reachable ≠ Index Ready**.

The script also used `expected_answer` from the case set to fabricate the
final answer text and produced citation/answer rows without going through
the Zuno answer-synthesis path. This violates the PHASE22 contract that
benchmark tooling must not fabricate Trace / Receipt / RunOutcome /
BudgetSettlement / MeasurementAttestation.

## What replaces it

This evidence records the invalidation and requires the synthetic benchmark
track to stay `NOT_RUN` / `blocked_not_measured` with
`release_decision.verdict = BLOCKED` until a real canonical runtime ingestion
round proves otherwise.

Required blocked reason: `canonical_runtime_not_executed`.

WP3 ("Real Knowledge Base Ingestion & Three-Index Construction") is the
round that will exercise the real ingestion path. Until that round's
verifier records `SUCCESS_REAL_INGESTION`, no MEASURED value or PASSED
release decision is valid for this track.

## History preservation

- `d7566624` is preserved in git history.
- Tag `phase22-syn-d756-invalidated` marks the pre-substring-sim commit
  (`166de87b`) for reference.
- This file documents the invalidation; it does not rewrite history.

## Who owns this notice

Claude Code + MiniMax (this branch).
Final reviewer: ChatGPT.
