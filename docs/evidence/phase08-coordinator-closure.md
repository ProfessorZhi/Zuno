# PHASE08 Coordinator Closure Decision

phase_id: PHASE08
date: 2026-07-23
status: superseded_reopened
coordinator_approval: superseded_repair_required
phase08_state: in_progress
production_ready: false

## Closure Decision

本 PHASE08 Coordinator Closure 已被 Goal02 repair 目标 supersede。PHASE08 当前重新打开为 `in_progress`，直到 PostgreSQL Checkpointer、Native Resume、Final Gate、durable step commit、Owner integration 和真实 cutover 重新完成并通过独立审查。

## 审查依据

- PHASE08 Pre-Closure：`docs/evidence/phase08-pre-closure.md`
- Domain facts：`src/backend/zuno/agent/domain/task_contracts.py`
- PostgreSQL repository：`src/backend/zuno/platform/database/agent/domain.py`
- Alembic head：`20260723_23`
- Fixed runtime surface：`src/backend/zuno/agent/runtime/phase08.py`
- Shadow / canary / rollback：`src/backend/zuno/agent/runtime/phase08_cutover.py`
- Focused tests：`tests/agent/test_phase08_*.py`、`tests/integration/agent/test_phase08_*.py`、`tests/agent/runtime/test_phase08_*.py`

## 边界

PHASE08 不拥有 Product Surface、Web/Desktop、Knowledge Version、Tool Side Effect、Benchmark Release Gate 或完整 production operations。旧 `GeneralAgent` 主路径仍只作为后续 PHASE09/PHASE22 的迁移和移除对象；本 Closure 不批准永久双 runtime。

## 下游影响

PHASE08 completed 后，PHASE12 的 PHASE08 依赖已满足，但 PHASE12 仍保持 `planned`，因为 PHASE11 仍为 `reopened/in_progress`。PHASE09 仍不得在本轮实现；Goal02 下一步进入 PHASE11 Package A evidence review 与 P11-T04～T08。
