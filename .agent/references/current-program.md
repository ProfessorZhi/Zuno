# 当前 Program 状态

## Current Truth

Active program: `zuno-eight-deliverables-full-realization-v1`
state: active
current_phase: `.agent/programs/PHASE09_runtime-upgrade-integration.md`

## 最近完成事实：PHASE08

PHASE08 / GraphRAG Knowledge Runtime System 已完成 foundation slice。当前代码和测试证明：

- `GraphRAGExtractorConfig` 已进入 GraphRAG contract，能表达 LLM-first extractor mode、rule fallback、model / prompt / schema / policy / eval refs。
- `KnowledgeQueryService.build_project_snapshot()` 会把现有 `knowledge_config` JSON 转成 `GraphRAGProjectSnapshot.extractor_config`，不新增 DB schema。
- `GraphRAGQueryService` 和 `RetrievalOrchestrator` 会在 trace metadata 中暴露 `query_method_contract`、`citation_contract` 和 `retrieval_fusion_contract`。
- 显式 `global` 当前走 `community_global`，不与 vector / BM25 chunk-level retrievers 扁平混榜；缺少 chunk/span grounding 时 citation contract 保持 `missing`。
- `GeneralAgent` 知识库工具返回文本会暴露 `query_method_contract: <method> via <internal_route>`，旧 `zuno.services.*` import path 继续可用。
- Contract Review eval comparison 已用 `dev_offline,dev_local,demo` 三 profile 跑通；缺少 `.local` contract-review corpus manifest 的 stackless matrix 和依赖本地模型 registry 的 real-runtime multihop runner 不写成 Current。
- 这些事实不表示生产级 schema-constrained LLM extraction、完整 RRF/rerank 治理、多套 extractor orchestration、DB schema 迁移或前端 trace 面板已经完成。

`.agent/programs/` 当前保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_program-boot-baseline.md`
- `PHASE02_workflow-self-maintenance-system.md`
- `PHASE03_architecture-docs-html-system.md`
- `PHASE04_query-router-mode-policy.md`
- `PHASE05_context-builder-memory-system.md`
- `PHASE06_capability-toolcard-mcp-system.md`
- `PHASE07_hooks-evidence-trace-artifact-system.md`
- `PHASE08_graphrag-knowledge-runtime-system.md`
- `PHASE09_runtime-upgrade-integration.md`
- `PHASE10_validation-release-closure.md`

本轮执行模式是主线程目标模式，默认开启线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构；不是多线程模式，不生成 `.agent/programs/thread-prompts/` 子线程提示词。

## Program 目标

`zuno-eight-deliverables-full-realization-v1` 要完整落实八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

该 program 吸收以下 queued drafts 的近期实现内容：

- `zuno-query-router-and-mode-policy-v1`
- `zuno-context-builder-and-memory-v1`
- `zuno-hooks-evidence-trace-v1`
- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`

这些草案仍是参考输入，不是 active 执行入口。

## 最近完成事实：Program 3

Program 3 / `zuno-repo-layout-cleanup-v1` 已完成六层顶层目录收口和 final alias surface closure。`src/backend/zuno` 顶层目录已经收敛为：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`

根目录只保留：

- `__init__.py`
- `main.py`

旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

## 最近完成事实：Program 4

Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档到：

- `docs/history/programs/zuno-six-layer-internalization-v1/`

它让六层内部拥有第一批清晰、可测试、无副作用的目标层入口：

- `agent/`：runtime、context、post_turn、state、streaming、tool_bridge。
- `memory/`：contracts、store、policy、review、retrieval、rendering、engine。
- `capability/`：contracts、registry、selector、policy、execution、trace。
- `knowledge/`：contracts、query_service、evidence、citation、trace、retrieval、fusion、graphrag。
- `platform/`：model_gateway、security、observability、storage。

这些入口复用现有 runtime owner 或 compatibility owner。这不表示 production-grade memory extraction、retrieval consolidation、Memory DB、dynamic capability orchestration、retrieval fusion 或 Runtime Architecture Upgrade 已完成。

## 当前工作流治理事实

Architecture Documentation Governance 和 Agent Workflow Self-Maintenance 已登记为当前工作流规则：

- `docs/architecture/` 是 human-facing formal architecture source。
- `docs/architecture.html` 是生成展示页，不是唯一事实来源。
- `.agent/references/` 是 Agent-facing operating memory。
- `.agent/templates/` 是 generation contract。
- `.agent/programs/` 是 execution state。
- 当前不启用 `.agent/plans/`；如未来启用，必须先更新 AGENTS、system、verifier 和 tests。
- 对外展示时，Zuno 最终成品是五个成熟系统；内部验收时，拆成八大交付物。

## 最近完成事实：PHASE04

PHASE04 / Query Router Mode Policy 已完成。当前代码和测试证明：

- `product_mode = normal | enhanced | auto` 已贯通 completion DTO、AgentConfig、KnowledgeQueryService、GraphRAGQueryService 和 RetrievalPlanner。
- `requested_query_method` 可为 `auto`，但 `resolved_query_method` 只落到 `basic | local | global | drift`。
- Trace metadata 已记录 requested/resolved product mode、router decision、requested/resolved query method、fallback reason、budget policy、fallback policy、pipeline trace 和 citation coverage。
- Eval mode metadata 已保留 `standard_retrieval / enhanced_retrieval` 兼容名，并新增 `normal / enhanced / auto` 产品名。

## 最近完成事实：PHASE05

PHASE05 / Context Builder Memory System 已完成 foundation slice。当前代码和测试证明：

- Context Pack contract 已包含 `ContextPackPolicy`、`ModelContextPacket.context_policy`、token budget、compression / extraction policy 和 source id 覆盖率 trace。
- `ContextOrchestrator` 会为 system prompt、recent messages 和 tool call/result items 生成可复现 `source_event_ids`，并记录缺失 source id 的 memory / task / knowledge item。
- Memory foundation 已区分短期状态、工作记忆、语义记忆、情节记忆和程序性记忆；structured memory candidate 默认 pending review，approval / rejection decision 保留 reviewer、reason、layer 和 source ids。
- `GeneralAgent.prepare_context()` 只接入同 scope task summary 与 approved structured memory 的轻量 readback；`post_turn_commit()` 继续只写 scoped raw event 和 task summary。
- 这些事实不表示 production-grade Memory DB、成熟 long-term memory retrieval / consolidation、完整 PostTurnPipeline 或 mature Context Orchestrator product behavior 已完成。

## 最近完成事实：PHASE06

PHASE06 / Capability ToolCard MCP System 已完成 foundation slice。当前代码和测试证明：

- Capability physical owner 已提供 `ToolCard`、`ToolCardRegistry`、`NativeBM25Retriever`、`NativeBM25SearchResult`、`CapabilityPolicyDecision` 和扩展后的 `CapabilitySelectionTrace`。
- ToolCard 是 compact retrieval metadata，不是 full runtime tool schema；它保留 permissions、side effects、cost/latency hint、health、owner、source、aliases 和 schema summary。
- Dynamic selector 已使用 ToolCard BM25 候选和 type / health / permission / side-effect / cost / relevance filters，并记录 candidate / selected / rejected ToolCard ids、retrieval scores、filter names 和 injected schema ids。
- Capability registry 可从现有 tool / skill / MCP public dict 构造内部 ToolCard，但 `/capability/search` response shape 不新增 `tool_card` 字段。
- `GeneralAgent.prepare_context()` 只把 capability selection trace 写入内部 context item metadata；这不改变 API/SSE 输出、DB schema、frontend contract、MCP config 或 runtime tool wiring。
- 这些事实不表示 production-grade dynamic capability orchestration、optional vector capability search、完整执行层 tool filtering 或 product-facing trace UI 已完成。

## 最近完成事实：PHASE07

PHASE07 / Hooks Evidence Trace Artifact System 已完成 foundation slice。当前代码和测试证明：

- Knowledge trace thin surface 已暴露 `HookPoint`、`RuntimeTraceEvent`、`RuntimeTraceBuilder`、`EvidenceChecker`、`EvidenceVerdict`、`TraceArtifactManifest` 和 trace enrichment helper。
- `GraphRAGQueryService` 会把 enhanced query result 的 trace metadata 补齐为 runtime trace events、evidence verdict 和 artifact manifest；低置信 evidence verdict 会保留 fallback reason，并同步到 `KnowledgeQueryResult.fallback_reason`。
- `GeneralAgent` 的 `search_knowledge_base` tool 会通过既有 custom event 通道发出 additive trace / evidence / artifact payload，并把低置信 evidence status、citation coverage 和 fallback reason 放入工具返回文本。
- `EmitEventAgentMiddleware` 会在既有 START / END / ERROR tool payload 内添加 `runtime_trace_event`，证明 pre-tool / post-tool hook foundation；这不改变 SSE 外层 envelope。
- Multihop eval diagnostics 已能解释 evidence verdict status、artifact manifest trace id 和 runtime trace event count。
- 这些事实不表示完整 artifact storage / download flow、frontend trace panel、production-grade hooks governance、完整 middleware policy 或全部增强请求的产品级 trace UI 已完成。
