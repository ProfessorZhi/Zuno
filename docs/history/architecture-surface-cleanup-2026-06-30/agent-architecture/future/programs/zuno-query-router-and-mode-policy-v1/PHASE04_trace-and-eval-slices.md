# PHASE04：Trace And Eval Slices
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

让 mode、query_method、fallback、budget、retrievers used 和 evidence coverage 进入 trace / eval slice。

## 验收

有 focused tests、trace fixture 和最小 eval 切片，能区分普通、增强、自动以及四个 query_method。
