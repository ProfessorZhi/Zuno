# PHASE22 CC-D Fault Security Resume Evidence

WORKER_TASK_ID: CC-D

## Recommended Provider / Model
MiniMax 做测试矩阵、日志归档、Docker/env 探测和 evidence；DeepSeek 做 fault/resume/idempotency 根因修复。

## Base SHA
origin/main `c9d099d64a1af28102231751ce55df8217173e89`；PR #106 head `95e17fc522591e7ee543b40b5b568d71963b6aa0`；PR #107 handoff source `6c9c75eaea16a047107e20fa156824bce068ee4c`。

## Goal
围绕 CC-B/CC-C 真实 runtime，完成 Fault、Security、Resume、Idempotency 和 Evidence Matrix；可提前准备矩阵，完整运行必须等待真实 snapshot/profile。

## Current Facts
fault_security_resume_matrix=NOT_RUN；live runtime evidence bundle=absent；snapshot_id=null；profile_run_ids=[]；production_readiness=not_established。

## Current Gap
未证明部分索引失败禁止 Snapshot、缺 credential fail-closed、Neo4j mismatch 拒绝 receipt、缺 receipt 阻塞 activation、重复摄取幂等、跨 tenant/workspace 隔离、未知副作用 reconciliation。

## Allowed Paths
`tests/integration/**`、`tests/evals/**`、`infra/docker/**`、`tools/scripts/**`、`docs/evidence/**`、`.agent/programs/work-products/**`。

## Forbidden Paths
不得盲目 retry unknown side effect；不得泄露 secret；不得用端口可达冒充写读验证；不得删除失败断言；不得改 PHASE22 completed 或 program no-active。

## Canonical Owner
Security、Runtime Recovery、Knowledge Indexing、Eval Evidence owner 共同提供证据；跨 owner 语义变更交回 Codex / Architecture review。

## Contracts
Evidence 必须包含 command、exit code、服务版本、namespace、IDs、cleanup、失败分类、not-run 和 artifact hash；Receipt 必须来自 owner builder。

## State Transitions
覆盖 `index_partially_failed`、`index_visibility_failed`、`credential_blocked`、`snapshot_activation_blocked`、`reconciliation_required`。

## Failure Semantics
ES 成功 Milvus 失败不得激活 Snapshot；缺 Embedding Credential 必须 credential_blocked；Neo4j mismatch 不得生成 receipt；未知副作用必须 reconciliation_required。

## Retry / Recovery / Idempotency
重复摄取不得重复创建 Source、KnowledgeVersion、Node、Edge、Chunk；resume 不得重复执行已提交副作用。

## Security Requirements
跨 tenant/workspace 必须拒绝或隔离；Evidence redacted。

## Gold Isolation Requirements
四 Profile trace 必须证明 runtime 未读取 expected answer、gold span、derivation spec 或 world model。

## Required Tests
`git diff --check`
`python tools/scripts/verify_phase22_synthetic_regression_track.py`
`python tools/scripts/verify_phase22_completion_blockers.py`

## Acceptance Criteria
矩阵有真实命令和 exit code；每个失败有分类和 owner；cleanup 完成或残留明确；不泄露 secret；只提交 completion_candidate。

## Commit Contract
仅提交 CC-D 范围，message 前缀 `test(phase22):` 或 `docs(phase22):`。

## Worker Result Schema
```yaml
worker_task_id: CC-D
status: completion_candidate | blocked
commit_sha: null
matrix_status: NOT_RUN_DEPENDENCY_BLOCKED
tests_run: []
tests_not_run: []
cleanup: []
remaining_gaps: []
```

## Handoff Format
返回 exact commit SHA、矩阵行结果、命令、exit code、环境版本、cleanup、not-run reason 和风险。

## Stop Conditions
缺 CC-B/CC-C runtime evidence、需要改变 security/recovery/state machine contract、或只能伪造 evidence 通过时停止。
