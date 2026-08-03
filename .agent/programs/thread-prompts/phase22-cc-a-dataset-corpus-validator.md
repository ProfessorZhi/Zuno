# PHASE22 CC-A Dataset Corpus Validator

WORKER_TASK_ID: CC-A

## Recommended Provider / Model
MiniMax；适合批量数据检查、manifest、hash、证据和机械 verifier。

## Base SHA
origin/main `c9d099d64a1af28102231751ce55df8217173e89`；PR #106 head `95e17fc522591e7ee543b40b5b568d71963b6aa0`；PR #107 handoff source `6c9c75eaea16a047107e20fa156824bce068ee4c`。

## Goal
复核 80-case candidate dataset、corpus、world model、derivation validator、source evidence、duplicate/gold leakage/hard negative/hash guard。若 80/80 已满足，不得制造第二套数据集。

## Current Facts
case_count=80；derivation_valid_count=80；source_evidence_valid_count=80；unsupported_answer_count=0；reviewer_approved_count=0；benchmark_eligible_count=0；dataset_hash=`b7832e537dbaab14a7d664f334676120f10b86aa8b7efddfc7220bc7bc915f0c`。

## Current Gap
当前只是 machine-attested synthetic candidate，不是 Public Benchmark；缺 reviewer approval 和真实 runtime 链路。

## Allowed Paths
`tools/evals/zuno/synthetic_benchmark/**`、`tests/evals/synthetic_benchmark/**`、`docs/evidence/goal05-phase22-machine-attested-synthetic-regression/**`、`.agent/programs/work-products/**`。

## Forbidden Paths
不得声明 `SYNTHETIC_REGRESSION_TRACK_READY`、`PHASE22_COMPLETED`、`FIXED_PUBLIC_BENCHMARK_PASSED`、`PRODUCTION_READY`；不得把 reviewer approval 写成机器证明；不得让 runtime request 携带 expected answer、gold span、derivation spec 或 world model。

## Canonical Owner
Eval / Benchmark owner；Dataset 和 evidence 是评测输入，不拥有 KnowledgeVersion、Snapshot 或 runtime facts。

## Contracts
保持 candidate dataset schema、case hash、input hash、source span ref、world model derivation 和 runtime forbidden-gold-field contract 稳定。

## State Transitions
只允许 `candidate_prepared -> candidate_validated` 或 `blocked_with_exact_gap`；不得推进到 `benchmark_eligible`。

## Failure Semantics
发现 schema/hash/source evidence/gold leakage/duplicate/hard-negative 问题时，输出 case_id 和根因，不做大规模重写。

## Retry / Recovery / Idempotency
生成器和 validator 必须可重复运行；输入不变时 case hash 不得变化。

## Security Requirements
不得记录 secret、本机敏感路径或 provider credential。

## Gold Isolation Requirements
runtime request forbidden field count 必须为 0；profile runtime 不得读取 gold。

## Required Tests
`python tools/scripts/verify_phase22_synthetic_regression_track.py`
`python -m pytest -q tests/evals/synthetic_benchmark/test_dataset_contract.py tests/repo/test_phase22_synthetic_regression_track.py -p no:cacheprovider`

## Acceptance Criteria
80/80 schema、derivation、source evidence、hash 通过；unsupported=0；duplicate=0；gold leakage=0；只提交 completion_candidate。

## Commit Contract
仅提交允许路径，message 前缀 `test(phase22):` 或 `docs(phase22):`。

## Worker Result Schema
```yaml
worker_task_id: CC-A
status: completion_candidate | blocked
commit_sha: null
tests_run: []
tests_not_run: []
current_facts: {}
remaining_gaps: []
```

## Handoff Format
返回 exact commit SHA、变更文件、命令、exit code、未运行项和残留风险。

## Stop Conditions
需要人工 reviewer approval、改变 dataset contract major version、或必须重写 80 case 时停止交回 Coordinator。
