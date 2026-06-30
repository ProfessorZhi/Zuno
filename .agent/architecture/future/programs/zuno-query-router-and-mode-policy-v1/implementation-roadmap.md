# Zuno Query Router And Mode Policy V1
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

把产品三模式和内部四个 `query_method` 固定成 runtime contract：普通模式、增强模式、自动模式；`basic / local / global / drift`；`auto` 只作为 router。

## Phase

1. [PHASE01：Current router audit](PHASE01_current-router-audit.md)
2. [PHASE02：Product mode contract](PHASE02_product-mode-contract.md)
3. [PHASE03：Query method policy](PHASE03_query-method-policy.md)
4. [PHASE04：Trace and eval slices](PHASE04_trace-and-eval-slices.md)
5. [PHASE05：Program closure](PHASE05_program-closure.md)

## 禁止范围

不重写 GeneralAgent 主循环；不改 API response shape；不把 auto 写成第五种 GraphRAG query mode。
