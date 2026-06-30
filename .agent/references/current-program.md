# 当前 Program 状态

## Current Truth

Active program: `zuno-eight-deliverables-full-realization-v1`
state: active
current_phase: `.agent/programs/PHASE01_program-boot-baseline.md`

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

本轮执行模式是主线程目标模式，默认开启线程内多 agent 协作；不是多线程模式，不生成 `.agent/programs/thread-prompts/` 子线程提示词。

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
