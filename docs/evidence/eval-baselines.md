# Eval Baselines

## Purpose

Record the formal Eval baseline status for the Zuno Target Architecture
Migration V1 closure without implying this page reran tests or evals.

## Current Status

Zuno Target Architecture Migration V1 is closed and archived. This page records
the `ffa3add` closure evidence; it is not a fresh test or eval execution from
this documentation-sync round.

Phase 11C active runtime cleanup is complete. Phase 12 is closed through the
target migration closure evidence.

## Closure Evidence

- Full pytest closure evidence: `714 passed, 3 warnings`.
- Contract Review eval:
  - `dev_offline`: status=`ok`.
  - `dev_local`: status=`ok`.
- Stackless baseline comparison:
  - Core acceptance passed.
  - `prefer_rerank_when_tied=no` is recorded as a tuning signal, not a failure.
- Trace closure is complete. Eval JSONL includes `trace_id`,
  `graphrag_project_id`, requested/resolved query method, evidence bundle,
  citation coverage, prompt version, query prompt version, index version,
  community version, latency, and `cost=null`.
- Legacy grep closure:
  - 457 hits.
  - All hits are classified as `history_archive` or
    `migration_retirement_guard`.
  - `needs_review=0`.

## Current Boundaries

Context Orchestrator full product behavior remains Target, not mature Current.
Production-grade memory extraction, retrieval, and consolidation remain Target.
Product-level dynamic capability orchestration remains Target.

`domain_pack_id` may still appear as a migration alias, existing database-column
compatibility, eval CLI compatibility, and retirement/history tests. It is not
the active mainline public architecture.
