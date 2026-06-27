# PHASE01：Repo Layout 审计
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

审计根目录、`src/backend/zuno`、`docs`、`.agent`、`tools`、`tests` 的杂乱点。

## 可并行线程

- root/docs audit
- backend layout audit
- tools/tests/generated artifacts audit

## 验收

给出清理表和迁移风险，不直接移动 runtime。
