# CC-C PHASE22 Four Profile Runtime / Benchmark Harness

WORKER_TASK_ID: CC-C-PHASE22-FOUR-PROFILE-RUNTIME-BENCHMARK
Base SHA: 95e17fc522591e7ee543b40b5b568d71963b6aa0

## Goal

让 Standard RAG、Local GraphRAG、Deep GraphRAG、Agentic GraphRAG 使用同一 Synthetic Snapshot 走四条正式不同路径，并输出真实指标和 synthetic release decision。

## Current Gap

当前 canonical adapters 只能到 `RUNTIME_OBSERVED` 或 blocked；没有同 Snapshot 四 Profile 真实 measured run ids。

## Allowed Paths

- `tools/evals/zuno/rag_eval/**`
- `tools/evals/zuno/synthetic_benchmark/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/agent/**`
- `tests/evals/**`
- `tests/integration/**`
- `docs/evidence/goal05-phase22-machine-attested-synthetic-regression/**`

## Forbidden Paths

- 不使用 substring/in-memory runtime。
- Runtime request 不得携带 `expected_answer`、gold documents、gold spans、gold citations、expected path 或 expected behavior。
- 不让四个 profile 实际调用同一个实现只改 profile name。
- 不输出 public fixed benchmark passed 或 production release passed。

## Contracts

四个 profile 必须绑定相同：`dataset_hash`、`corpus_hash`、`knowledge_version_id`、`snapshot_id`、`embedding_provider`、`embedding_model`、`embedding_config_hash`、`reranker_config`、`security_epoch`、`principal set`、`budget policy`、`answer policy`、`evaluation config`。

## Owner

Eval / Benchmark Harness owns measurement；runtime owners produce traces, receipts and RunOutcome.

## State Transitions

`snapshot_selected -> profile_request_built_without_gold -> runtime_executed -> output_frozen -> evaluator_reads_gold -> metrics_computed -> synthetic_release_decision`

## Failure Semantics

Gold leakage invalidates the whole profile run；missing receipt blocks measured；missing RunOutcome blocks Agentic measured；profile failure counts into release decision。

## Retry / Recovery / Idempotency

Re-run with same snapshot/config must produce comparable artifact hashes or explain variance；failed profile retry must keep original trace refs。

## Security

Security principal set and epoch must be frozen；retriever must enforce tenant/workspace filters。

## Required Tests

```powershell
python -m pytest -q tests/evals -k "phase22 or synthetic or canonical_profile or release_decision" -p no:cacheprovider
python -m pytest -q tests/integration -k "profile or benchmark or agentic" -p no:cacheprovider
```

## Acceptance Criteria

Four profile run ids exist；runtime traces contain no gold；metrics include non-zero thresholds；release decision is `PASSED`、`FAILED`、`BLOCKED` or `INCOMPARABLE` scoped only to `machine_attested_synthetic_regression`。

## Commit Contract

普通 commit，禁止 amend/force-push；提交信息包含 `[worker=CC-C]`。

## Handoff Format

提交 `git show <WORKER_SHA>` 摘要、profile run ids、trace refs、metrics、thresholds、release decision 和 gold isolation proof。
