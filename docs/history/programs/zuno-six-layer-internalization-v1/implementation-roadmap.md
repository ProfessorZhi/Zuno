# Program Roadmap

## 总目标

让六层内部从纯 facade 或旧路径拼图，推进为可解释、可测试、无副作用的目标层薄入口，同时保持现有 runtime 语义和旧 public import path。

## 总边界

允许：

- 增加 thin facade、contracts、policy、selector、retrieval、rendering、trace、storage、observability 等目标层入口。
- 保留旧 public import path，并证明新旧入口对象一致。
- 修正文档中 Current / Target 混淆。
- 增加 focused tests 和 verifier guard。

禁止：

- 改 API response shape。
- 改 DB schema。
- 改 frontend。
- 改 eval baseline。
- 重写 `GeneralAgent` 主循环。
- 删除 `zuno.services.*`、`zuno.core.*`、`zuno.database.*` 等旧 public import path。
- 把未完成的 production runtime 能力写成 Current。

## Phase Plan

1. `PHASE01_six-layer-current-inventory.md`：盘点六层内部成熟度，确认 Program 3 只完成顶层封口。
2. `PHASE02_memory-layer-foundation-surfaces.md`：让 `memory/` 从纯 facade 变成 contract / store / policy / review / retrieval / rendering / engine 薄入口。
3. `PHASE03_capability-layer-foundation-surfaces.md`：按 contracts / registry / selector / policy / execution / trace / mcp / tools 收口 capability 入口。
4. `PHASE04_knowledge-layer-foundation-surfaces.md`：按 query_service / contracts / evidence / citation / retrieval / fusion / graphrag 收口 knowledge 入口。
5. `PHASE05_agent-runtime-boundary-surfaces.md`：在不重写 GeneralAgent 的前提下，把 agent 层入口拆成 runtime / context / post_turn / state / streaming / tool_bridge。
6. `PHASE06_platform-boundary-hardening.md`：收紧 platform 的 model_gateway / security / observability / storage 边界。
7. `PHASE07_docs-verifier-and-closure.md`：同步 docs、AGENTS、verifier、tests，并归档当前 program。

## 完成状态

Phase 01-07 均 completed。
