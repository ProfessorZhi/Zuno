# Zuno Hooks Evidence Trace V1
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

把 Hooks / Policy / Budget / Fallback / Evidence Check / Citation Coverage / Trace Event 固定为 runtime governance contract。

## Phase

1. [PHASE01：Hooks and evidence audit](PHASE01_hooks-and-evidence-audit.md)
2. [PHASE02：Runtime event contract](PHASE02_runtime-event-contract.md)
3. [PHASE03：Evidence check policy](PHASE03_evidence-check-policy.md)
4. [PHASE04：Artifact and trace flow](PHASE04_artifact-and-trace-flow.md)
5. [PHASE05：Program closure](PHASE05_program-closure.md)

## 禁止范围

不把 WebSocket/SSE monitor 写成业务层；不把异常捕获包装成完整 observability；不绕过 permission policy。
