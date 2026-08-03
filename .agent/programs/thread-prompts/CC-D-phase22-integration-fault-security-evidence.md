# CC-D PHASE22 Integration / Fault / Security / Resume / Evidence

WORKER_TASK_ID: CC-D-PHASE22-INTEGRATION-FAULT-SECURITY-EVIDENCE
Base SHA: 95e17fc522591e7ee543b40b5b568d71963b6aa0

## Goal

执行并记录 machine-attested synthetic regression 的 Integration、Fault、Security、Resume、Idempotency、Benchmark Matrix 和可复现 Evidence。

## Current Gap

当前没有完整 fault/security/resume/idempotency matrix，也没有最终 Synthetic Track readiness report。

## Allowed Paths

- `tests/integration/**`
- `tests/fault/**`
- `tests/security/**`
- `tools/evals/zuno/synthetic_benchmark/**`
- `tools/scripts/**phase22**`
- `docs/evidence/goal05-phase22-machine-attested-synthetic-regression/**`

## Forbidden Paths

- 不降低阈值。
- 不把健康检查或端口连通写成 write/read verified。
- 不伪造 credentials、vectors、receipts、trace refs 或 RunOutcome。
- 不修改 PHASE22 为 completed。

## Contracts

每项 fault 记录：`trigger`、`state_before`、`state_after`、`owner`、`propagation`、`retryability`、`recovery`、`idempotency_key`、`receipt`、`trace_ref`、`test_command`、`exit_code`。

## Owner

Fault evidence owner；不得改变 runtime owner contract，发现 contract gap 必须标为 Codex/Architecture candidate。

## State Transitions

故障测试必须验证正常路径和 fail-closed 路径，不得只验证 happy path。

## Failure Semantics

MinIO/Postgres/RabbitMQ/ES/Milvus/Neo4j/Embedding/Worker/Snapshot/Security/Cancel/Deadline/Resume/UNKNOWN side effect 均必须有明确状态和 owner。

## Retry / Recovery / Idempotency

同一失败最多按任务说明重试；重复摄取、重复消息和 resume 必须验证不重复领域事实。

## Security

Tenant 越权、Workspace 越权、Security Epoch 过期必须 fail-closed 且留下 trace/evidence。

## Required Tests

```powershell
git diff --check
python tools/scripts/verify_phase22_synthetic_regression_track.py
python tools/scripts/verify_phase22_completion_blockers.py
python -m pytest -q tests/integration tests/evals -p no:cacheprovider
```

## Acceptance Criteria

完整矩阵记录 PASSED / FAILED / BLOCKED / NOT_RUN；所有真实服务验证区分 SERVICE_REACHABLE 和 SERVICE_WRITE_READ_VERIFIED；Evidence 可复现；未运行项明确 NOT_RUN。

## Commit Contract

普通 commit，禁止 amend/force-push；提交信息包含 `[worker=CC-D]`。

## Handoff Format

提交 `git show <WORKER_SHA>` 摘要、matrix、service versions、commands、exit codes、cleanup、blockers 和 final readiness recommendation。
