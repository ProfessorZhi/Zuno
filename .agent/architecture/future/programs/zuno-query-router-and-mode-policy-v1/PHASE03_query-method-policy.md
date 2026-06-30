# PHASE03：Query Method Policy
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

固定 `query_method = basic | local | global | drift` 的选择、降级和手动覆盖规则。

## 验收

`auto` 只记录 requested router；resolved method 必须落到 basic、local、global 或 drift；global / drift 未准备好时 trace 写清 fallback reason。
