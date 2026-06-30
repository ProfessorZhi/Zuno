# 当前 Program 状态

## Current Truth

当前没有 active program。

state: no-active
current_phase: none

最近完成并归档的 program：`zuno-eight-deliverables-full-realization-v1`

- 归档目录：`docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- 范围：PHASE01-PHASE10。
- 状态：completed / archived。
- 执行方式：主线程目标模式 + 默认开启线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构；不是多线程模式。

`.agent/programs/` 当前保留等待态入口：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`

前台没有 `PHASE*.md`。打开下一轮 program 时，必须先迁入新的 roadmap 和 phase 文件，并从 `PHASE01` 开始。

## 最近完成事实：zuno-eight-deliverables-full-realization-v1

这个 program 完整落实八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

PHASE04 / Query Router Mode Policy 已完成。当前代码和测试证明 `product_mode = normal | enhanced | auto` 和 `query_method = auto | basic | local | global | drift` 已进入 DTO、AgentConfig、KnowledgeQueryService、GraphRAGQueryService、RetrievalPlanner、trace metadata 和 eval mode metadata；`auto` 只作为 router，不是第五种最终 query mode。

PHASE05 / Context Builder Memory System 已完成 foundation slice。当前代码和测试证明 Context Pack policy、source id coverage、五类记忆 taxonomy、review contract、同 scope task summary 和 approved structured memory 轻量 readback 已存在；这不表示 production-grade Memory DB、成熟 long-term memory retrieval / consolidation 或完整 PostTurnPipeline 已完成。

PHASE06 / Capability ToolCard MCP System 已完成 foundation slice。当前代码和测试证明 ToolCard compact retrieval metadata、Native BM25 ToolCard retrieval、MCP/local policy trace、candidate / selected / rejected ToolCard trace 和 GeneralAgent internal trace bridge 已存在；这不表示 production-grade dynamic capability orchestration、optional vector capability search 或完整 runtime tool filtering 已完成。

PHASE07 / Hooks Evidence Trace Artifact System 已完成 foundation slice。当前代码和测试证明 Hook event schema、EvidenceVerdict、TraceArtifactManifest、GraphRAG trace enrichment、GeneralAgent additive trace event、tool pre/post hook payload 和 eval diagnostics 已存在；这不表示完整 artifact storage / download flow、frontend trace panel 或 production-grade hooks governance 已完成。

PHASE08 / GraphRAG Knowledge Runtime System 已完成 foundation slice。当前代码和测试证明 `GraphRAGExtractorConfig`、snapshot propagation、query method / citation / retrieval fusion trace contract、显式 global community-only prior、GeneralAgent query method contract 文本和旧 `zuno.services.*` import compatibility 已存在；这不表示生产级 schema-constrained LLM extraction、完整 RRF/rerank 治理、多套 extractor orchestration、DB schema 迁移或前端 trace 面板已完成。

PHASE09 / Runtime Upgrade Integration 已完成 foundation slice。当前代码和测试证明 `RuntimeTurnLedger`、当前轮 trace reset、knowledge/tool/post-turn evidence、六层目标入口 import guard、`prepare_context -> agent_loop -> post_turn_commit` 最小证据链和 eval diagnostics 已存在；这不表示完整产品级 runtime upgrade，也未改 API/SSE/DB/frontend。

PHASE10 / Validation Release Closure 已完成归档、no-active 前台状态、docs / `.agent` / verifier / tests 同步和 release closure PR 边界。

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

这些入口复用现有 runtime owner 或 compatibility owner。这不表示 production-grade memory extraction、retrieval consolidation、Memory DB、dynamic capability orchestration、retrieval fusion 或 full Runtime Architecture Upgrade 已完成。

## 当前工作流治理事实

Architecture Documentation Governance 和 Agent Workflow Self-Maintenance 已登记为当前工作流规则：

- `docs/architecture/` 是 human-facing formal architecture source。
- `docs/architecture.html` 是生成展示页，不是唯一事实来源。
- `.agent/references/` 是 Agent-facing operating memory。
- `.agent/templates/` 是 generation contract。
- `.agent/programs/` 是 execution state。
- 当前不启用 `.agent/plans/`；如未来启用，必须先更新 AGENTS、system、verifier 和 tests。
- 对外展示时，Zuno 最终成品是五个成熟系统；内部验收时，拆成八大交付物。

## 参考输入

以下 queued drafts 已被 `zuno-eight-deliverables-full-realization-v1` 吸收为本轮实现参考，但仍保留为未来参考输入，不是 active 执行入口：

- `zuno-query-router-and-mode-policy-v1`
- `zuno-context-builder-and-memory-v1`
- `zuno-hooks-evidence-trace-v1`
- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
