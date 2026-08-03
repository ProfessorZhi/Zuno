# PHASE22 CC-C Four Profile Benchmark Runtime

WORKER_TASK_ID: CC-C

## Recommended Provider / Model
DeepSeek；适合四 Profile runtime、Measurement Truth、Release Decision 和 same Snapshot 语义。

## Base SHA
origin/main `c9d099d64a1af28102231751ce55df8217173e89`；PR #106 head `95e17fc522591e7ee543b40b5b568d71963b6aa0`；PR #107 handoff source `6c9c75eaea16a047107e20fa156824bce068ee4c`。

## Goal
等待 CC-B 的真实 snapshot_id 后，运行 Standard、Local GraphRAG、Deep GraphRAG、Agentic GraphRAG 四 Profile，生成 comparable runtime metrics 和 synthetic release decision。

## Current Facts
runtime_request_case_count=80；runtime_request_profile_count=4；runtime_gold_forbidden_field_count=0；profile_run_ids=[]；runtime_metrics_ref=null；release_decision=BLOCKED；snapshot_id=null。

## Current Gap
四 Profile 只有 deterministic test double / blocked_not_measured / contract smoke，不是 formal measured runtime。

## Allowed Paths
`tools/evals/zuno/**`、`src/backend/zuno/agent/**`、`src/backend/zuno/knowledge/**`、`src/backend/zuno/observability/**`、`tests/evals/**`、`docs/evidence/**`。

## Forbidden Paths
不得使用 test double 作为 measured runtime；不得跨 snapshot 比较；不得降低阈值或绕过 MeasurementTruthGate；不得声明 Public Benchmark 或 Production Ready。

## Canonical Owner
Observability / Eval owner 负责 orchestration、metrics、measurement truth 和 release decision；Agent Core / Knowledge 只通过正式 runtime contract 提供能力。

## Contracts
每个 `MEASURED` profile 必须有 serialized measurement attestation，绑定 profile id、measurement status、artifact hash、fingerprint hash 和 evidence ref。

## State Transitions
`snapshot_available -> profile_running -> profile_runtime_observed -> measured | blocked_not_measured -> release_decision_blocked_or_failed_or_passed`。

## Failure Semantics
任一 Profile 缺 runtime evidence、credential、snapshot binding、formal approval 或 receipt 时，保持 BLOCKED/INCOMPARABLE。

## Retry / Recovery / Idempotency
同一 eval_run_id 重跑必须可复现；重复执行记录 rerun variance，不覆盖原 artifact。

## Security Requirements
Profile runtime 不得读取 gold answer、derivation spec 或 world model；credential 必须 redacted。

## Gold Isolation Requirements
扫描四 Profile trace，证明 expected answer、gold spans、derivation spec、world model 未进入 runtime input、retrieval context 或 prompt。

## Required Tests
`python -m pytest -q tests/evals/synthetic_benchmark/test_dataset_contract.py tests/repo/test_phase22_synthetic_regression_track.py -p no:cacheprovider`

## Acceptance Criteria
四 Profile 使用同一 snapshot_id；80 x 4 结果可追踪；Gold Isolation forbidden count=0；runtime metrics 完整；release decision 诚实输出。

## Commit Contract
仅提交 CC-C 范围，message 前缀 `feat(phase22):`、`fix(phase22):` 或 `test(phase22):`；只提交 completion_candidate。

## Worker Result Schema
```yaml
worker_task_id: CC-C
status: completion_candidate | blocked
commit_sha: null
snapshot_id: null
profile_run_ids: []
release_decision: BLOCKED
tests_run: []
tests_not_run: []
remaining_gaps: []
```

## Handoff Format
返回 exact commit SHA、snapshot_id、profile_run_ids、metrics hash、decision hash、命令、exit code 和风险。

## Stop Conditions
缺 CC-B snapshot、需要改变 MeasurementTruthGate contract、需要新 provider credential、或无法证明 gold isolation 时停止。
