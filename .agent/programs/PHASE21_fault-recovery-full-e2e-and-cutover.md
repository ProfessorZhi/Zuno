# PHASE21 Fault Recovery, Full E2E and Cutover

phase_id: PHASE21
status: planned
depends_on: PHASE10, PHASE19, PHASE20
owner: Coordinator / Cross-module Integration

## Phase 目标

在完整新架构上执行跨模块 Fault Injection、Security Attack、Backup/Restore、Web/Desktop E2E、Load/Soak 和 Canary Cutover，证明恢复、幂等、隔离和产品体验。此 Phase 将新架构切为默认主路径，并进入有限 Rollback Window；旧代码仍不能永久保留。

## Minimal Read Set

- 全部相关 Phase Completion Evidence
- 十一模块 Failure/Recovery 章节
- PHASE02 Rollback Playbook
- PHASE20 Eval/Gate
- 当前 deployment/infra/CI/e2e scripts

## Current Anchors

```text
infra/**
backend entrypoints
apps/web and apps/desktop
tests/e2e/**
tests/fault/**
tests/security/**
feature flags and rollout config
backup/restore scripts
```

## Allowed Paths

```text
integration/fault/e2e test code
infra/**
deployment/config rollout files
runbooks/** or docs/evidence/**
apps/web e2e fixtures
apps/desktop smoke fixtures
tools/scripts/cutover*.py
```

## Forbidden Paths

- 为通过 E2E 降低 Security/Final/Release Gate。
- 发现故障后直接删除失败场景。
- 未验证 Rollback 就默认新路径。
- 将 Rollback Window 变成永久旧架构。

## Work Packages

### P21-T01 Domain/Checkpoint/Queue Crash Matrix
- Goal：在关键 commit/send/checkpoint/ack 点注入 crash，验证 generation reconcile、outbox/inbox、orphan、resume。
- Scenarios：domain commit before checkpoint、dispatch commit before send、result before reducer、publisher/consumer restart。
- Acceptance：无丢失终态、无重复副作用、晚到结果被拒绝。

### P21-T02 Tool Effect UNKNOWN and Recovery E2E
- Goal：执行真实/可控外部写，注入 response lost、callback replay、status outage、reconciler restart、compensation fail。
- Acceptance：UNKNOWN 不盲重试；UI 显示受控动作；最终事实和 Audit 可追溯。

### P21-T03 Security Revocation and Attack Suite
- Goal：覆盖 epoch during wait、approval replay、cross-tenant、SSRF/DNS rebinding、prompt/tool-output injection、secret leakage、redaction failure。
- Acceptance：旧授权失效，敏感 payload 不持久化/导出，deny/audit 完整。

### P21-T04 Delete, Privacy, Legal Hold and Restore E2E
- Goal：跨 Product/Input/Knowledge/Memory/Tool/Trace/Projection 执行删除、hold、release、backup/restore。
- Acceptance：visibility 先撤销；Audit/legal tombstone 保留；restore 后删除状态不回生。

### P21-T05 Web/Desktop Full Product E2E
- Goal：上传→解析→检索→回答→引用→tool approval→effect/reconcile→publication→feedback；覆盖断线/Resync/多 Interrupt/撤权。
- Acceptance：Web browser E2E、Desktop smoke、build/lint 通过；无字符串猜动作。

### P21-T06 Load, Parallelism and Soak
- Goal：验证并发 Run、DAG branch、queue backlog、DB pool、trace lag、memory/index load、tool worker 和长时间运行。
- Metrics：p50/p95/p99、error、retry/replan churn、lease loss、gap、resource usage。
- Acceptance：无跨租户、死锁、无界队列/内存、重复 effect；阈值按环境诚实记录。

### P21-T07 Canary, Default-new and Rollback Rehearsal
- Goal：按 Feature Flag 状态 shadow→canary→default new，运行 rollback 和 reconciliation。
- Tests：new runtime outage、schema adapter issue、frontend rollback、queue backlog、provider outage。
- Acceptance：默认生产路径为新架构；旧路径仅剩有截止日期的 Rollback Window。

### P21-T08 Full Validation and Removal Candidate List
- Goal：运行完整 backend/frontend/repo/Migration/Fault/E2E/Security suite，生成最终旧代码删除清单和无用目录清单。
- Output：`docs/evidence/phase21-full-validation/` 和 `work-products/phase22-removal-candidates.yaml`。
- Acceptance：每个旧文件有引用搜索、替代 Owner、删除风险和测试；不得为了“兼容”永久保留 Legacy 文件夹。

## Phase 完成定义

- 新架构为默认主路径且 Rollback 演练通过。
- 跨模块 Fault/Security/Delete/Restore/Web E2E 有可重现证据。
- 旧路径进入短期 Rollback Window，删除清单完整。
- 尚未完成 PHASE22 删除时不得归档 Program。

## Validation

```bash
git diff --check
# full backend suite
pytest -q -p no:cacheprovider
# web lint/build/browser E2E
# desktop build/smoke
# alembic upgrade/downgrade verification
# infra fault, backup/restore, load and soak commands from evidence manifest
```
