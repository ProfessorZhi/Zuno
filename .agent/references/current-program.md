# 当前 Program 状态

## Current Truth

Active program: `zuno-eight-deliverables-full-realization-v1`
state: active
current_phase: `.agent/programs/PHASE06_capability-toolcard-mcp-system.md`

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
