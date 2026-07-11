# Agent 执行计划

`.agent/programs/` 当前处于 active 状态。

## 当前状态

- State: active
- Active program: `zuno-unified-agent-runtime-closure-v1`
- Current phase: `PHASE13_paired-benchmark-release-gate-and-program-closure`
- Latest completed program: `zuno-lean-complete-product-architecture-v1`
- Baseline commit: `72488a25fde59bc5ef86b2b1c84f25d42cb946ca`

## 当前 program

本 program 的目标是把以下三个并存基线收敛为同一条真实、可恢复、可测量的 Single Controller Agent Runtime：

- `GeneralAgent`：真实 LangChain / LangGraph ReAct 与现有模型、工具、知识库入口。
- `StrategySelector + AgentControlRuntime`：Planning、Reflection、Replan、Reflexion 规则与 contract。
- `SingleControllerDurableRuntime`：checkpoint、approval、resume、cancel 的本地 deterministic runtime。

## 当前 phase

当前只执行：

- `.agent/programs/PHASE13_paired-benchmark-release-gate-and-program-closure.md`

PHASE01 已冻结事实源、现状证据、运行命令、失败语义和 benchmark truth source；不修改生产 runtime，也不产生 measured benchmark 结论。PHASE02 已完成 unified runtime contracts and state。PHASE03 已完成 Model Gateway closure 的主入口和边界 verifier。PHASE04 已完成 durable store、trace 和 idempotency baseline。PHASE05 已完成 unified LangGraph runtime skeleton。PHASE06 已完成 Strategy / Plan-and-Execute / ReAct step execution baseline。PHASE07 已完成 Tool Control Plane integration baseline。PHASE08 已完成 corrective Agentic GraphRAG / EvidenceLedger baseline，并通过 `KnowledgeStepExecutor` 接入 runtime 依赖。PHASE09 已完成 Reflection / Replan / Grounded Synthesis runtime loop baseline。PHASE10 已完成 four-layer Memory / Reflexion reuse baseline。PHASE11 已完成 Product API / SSE / recovery cutover baseline。PHASE12 已完成真实 text PDF SourceSpan vertical slice。当前下一步是 PHASE13 的 paired benchmark / release gate / program closure。

## 当前文件

- `current.md`：active program、current phase 和不变边界。
- `implementation-roadmap.md`：PHASE01-PHASE13 依赖顺序和关闭定义。
- `closure-checklist.md`：program 完整关闭条件和禁止虚假关闭。
- `program-decisions.md`：跨 phase 决策。
- `code-architecture-map.md`：当前关键路径和目标 owner。
- `powershell-runbook.md`：Windows PowerShell 5.1 命令规范。
- `test-matrix.md`：测试层级、场景和 release gate。
- `PHASE01_*.md` 到 `PHASE13_*.md`：分阶段执行文件。
- `queued-programs/README.md`：当前没有 queued program。

## 使用规则

- 每轮只执行 `current_phase`，不得提前实现后续 phase。
- 当前代码、测试、trace/eval 和 HEAD 高于 phase 文档中的路径建议。
- 不把 contract、mock、fixture、probe 或 deterministic baseline 写成 runtime completed。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- 生产 runtime 的 Current 只能由真实 API / runtime / UI 路径、focused tests、trace/eval 或 verifier 证明。
- completed program 的 phase、closure summary 和 merged inputs 必须留在 `docs/history/programs/`。
