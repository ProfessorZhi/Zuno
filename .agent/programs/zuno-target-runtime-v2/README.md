# Zuno 目标运行时 V2

## 状态

当前可执行 Agent 程序。

## 目的

在已经关闭的 Zuno Target Architecture Migration V1 基线上，继续推进目标运行时架构的第一个受控实现切片。

这个程序保持当前 Single `GeneralAgent`、GraphRAG Project 主线、`KnowledgeQueryService` 和 `GraphRAGQueryService` 不变，同时把低风险后端所有权逐步移动到目标模块边界，补齐 Context/Memory 基础，再按线性 phase 落地目标运行时。

## 范围

已经完成的基础切片：

- Phase 00：当前状态闸门。
- Phase 01：程序初始化。
- Phase 02：模块边界审计和验证器。
- Phase 03：第一个低风险后端边界移动。
- Phase 04：最小可调用 Context Orchestrator 运行时。

计划执行的阶段：

- Phase 05：Memory Engine。
- Phase 06：Capability / Tool Retrieval。
- Phase 07：Knowledge Retrieval / Fusion。
- Phase 08：GeneralAgent LangGraph Runtime。
- Phase 09：Product Boundary / Trace / Eval Closure。

除非某个 phase 明确打开，否则以下内容不在范围内：

- 数据库 schema 变化。
- 依赖升级。
- Java 服务、微服务、事件 worker 和默认多 Agent 模式。

## 来源参考

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/roadmap.md`

## 当前文件

- `README.md`
- `implementation-roadmap.md`
- `current-phase.md`
- `closure-checklist.md`

Phase 00-04 的详细证据和旧 phase 文件已经归档到：

- `docs/history/programs/zuno-target-runtime-v2/`

## 验证规则

每个 phase 必须运行最小有效验证，并把当前结果记录到 active phase 或 closure checklist。体积较大的 phase 证据放到：

- `docs/history/programs/zuno-target-runtime-v2/`

不要把 Target 行为写成 Current，除非当前代码和测试已经证明它。
