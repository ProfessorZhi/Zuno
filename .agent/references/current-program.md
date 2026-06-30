# 当前 Program 状态

## Current Truth

当前 active program：`zuno-architecture-detail-and-execution-plan-v1`

state: active
current_phase: PHASE01_architecture-state-and-program-boot

## Program 目标

本 program 先细化 Zuno 目标架构文档、十类 Mermaid 架构图和生成 HTML，再从细化后的架构图反推出下一阶段执行计划。细化重点包括 Agent Core Runtime、Memory Layer、Document Ingestion、企业知识库场景、安全治理、Trace / Eval 和 LangSmith 适配。

它不是 runtime feature implementation，不新增 API / DB schema / frontend 行为，不把 Target 写成 Current。Memory Layer 的生产级 Raw Event Log、DB-backed memory、read/write path、review / promotion / decay 和 memory eval 仍是 Target。

## 当前执行入口

`.agent/programs/` 当前保存 active program：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_architecture-state-and-program-boot.md`
- `PHASE02_target-architecture-detailing.md`
- `PHASE03_mermaid-html-detail-refresh.md`
- `PHASE04_execution-roadmap-from-architecture.md`
- `PHASE05_validation-and-closure.md`

当前阶段：

- `PHASE01_architecture-state-and-program-boot.md`：active。

## 最近完成事实

最近完成并归档的 program：`zuno-eight-deliverables-full-realization-v1`

- 归档目录：`docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- 范围：PHASE01-PHASE10。
- 状态：completed / archived。
- 执行方式：主线程目标模式 + 默认开启线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构；不是多线程模式。

这个 program 完整落实八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

PHASE04-PHASE09 形成了 query router / mode policy、Context Pack / Memory foundation、Capability ToolCard / MCP policy、Hooks / Evidence / Trace、GraphRAG knowledge runtime contract 和 RuntimeTurnLedger integration 的 foundation slices。它们是当前代码和测试已经证明的事实；生产级 DB schema 迁移、前端 trace panel、完整动态工具编排、完整 model-visible context injection、完整 RRF/rerank 治理、Java / 微服务 / event worker 和 Zuno runtime 多 Agent 架构仍不是 Current。

## 最近完成事实：Program 3

Program 3 / `zuno-repo-layout-cleanup-v1` 已完成 final alias surface closure。`src/backend/zuno` 顶层目录已经收敛为：

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

它让六层内部拥有第一批清晰、可测试、无副作用的目标层入口。它不表示 production-grade memory extraction、retrieval consolidation、Memory DB、dynamic capability orchestration、retrieval fusion 或 full Runtime Architecture Upgrade 已完成。

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

以下 queued drafts 已被 `zuno-eight-deliverables-full-realization-v1` 吸收为近期实现参考，但仍保留为未来参考输入，不是 active 执行入口：

- `zuno-query-router-and-mode-policy-v1`
- `zuno-context-builder-and-memory-v1`
- `zuno-hooks-evidence-trace-v1`
- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
