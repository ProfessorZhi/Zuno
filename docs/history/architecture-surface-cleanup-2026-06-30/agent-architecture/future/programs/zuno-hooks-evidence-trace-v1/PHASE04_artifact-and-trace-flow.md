# PHASE04：Artifact And Trace Flow
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

把 Markdown / PDF / file artifact 与 session workspace、download path、trace event 和 permission 边界串起来。

## 验收

Artifact 创建、列表、下载和 trace summary 有一致 contract；路径越界检查进入 tests。
