# PHASE04：Compression And Extraction Policy
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

实现 Summary Compression + Structured Extraction 的 policy contract。

## 验收

summary 保留 `source_event_ids`；structured memory candidate 有审批/拒绝路径；Prompt Caching 不被写成 memory compression。
