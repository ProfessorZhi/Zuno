# 当前 Program 状态

## Current Truth

当前 active program：`zuno-master-architecture-implementation-v1`

state: active
current_phase: PHASE12_validation-release-closure

## Program 目标

本 program 不是再做一轮单纯架构说明，而是把 Zuno 从“架构文档和图已经成型”推进到“目标架构按阶段落地”。它先整理项目文件夹和代码分布，再围绕企业私有知识库与多功能 Agent 助手交付八个方面产物，并同步正式架构 Markdown、架构 HTML、README、verifier、tests 和历史归档。

八个方面产物：

1. 项目文件夹与代码布局治理。
2. 企业私有知识库场景与产品闭环。
3. Document Ingestion / Parse Gateway。
4. Single Controller Agent Runtime。
5. Context / Memory 系统。
6. Tool Control Plane。
7. RAG / GraphRAG 知识系统。
8. 安全、评测、观测、文档展示闭环。

它仍然遵守 Current / Target / Future / History 边界：未由代码、测试、trace、eval 或 verifier 证明的能力不能写成 Current。生产级 Parse Gateway runtime、production-grade durable LangGraph runtime、production-grade Memory DB、完整 Tool approval / sandbox 平台、生产级 GraphRAG extraction / fusion / index job、生产级 LangSmith trace / eval 平台、rootless / gVisor / Firecracker sandbox 和完整 credential broker 仍是 Target。

## 当前执行入口

`.agent/programs/` 当前保存 active program：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `PHASE01_program-baseline-and-previous-closure.md`
- `PHASE02_project-folder-and-code-layout-cleanup.md`
- `PHASE03_enterprise-scenario-and-product-loop.md`
- `PHASE04_document-ingestion-parse-gateway.md`
- `PHASE05_agent-runtime-langgraph-harness.md`
- `PHASE06_context-memory-system.md`
- `PHASE07_tool-control-plane-mcp-approval.md`
- `PHASE08_rag-graphrag-evidence-citation.md`
- `PHASE09_security-governance-sandbox.md`
- `PHASE10_eval-observability-langsmith.md`
- `PHASE11_architecture-docs-html-refresh.md`
- `PHASE12_validation-release-closure.md`

当前阶段：

- `PHASE01_program-baseline-and-previous-closure.md`：completed，已通过 program-state verifier 和 focused repo tests 证明基线一致。
- `PHASE02_project-folder-and-code-layout-cleanup.md`：completed。
- `PHASE03_enterprise-scenario-and-product-loop.md`：completed。
- `PHASE04_document-ingestion-parse-gateway.md`：completed。
- `PHASE05_agent-runtime-langgraph-harness.md`：completed。
- `PHASE06_context-memory-system.md`：completed。
- `PHASE07_tool-control-plane-mcp-approval.md`：completed。
- `PHASE08_rag-graphrag-evidence-citation.md`：completed。
- `PHASE09_security-governance-sandbox.md`：completed。
- `PHASE10_eval-observability-langsmith.md`：completed。
- `PHASE11_architecture-docs-html-refresh.md`：completed。
- `PHASE12_validation-release-closure.md`：active。

## 本轮研究输入

用户提供的高质量 ChatGPT 研究模式架构报告已归档到：

- `docs/history/research/chatgpt-research-mode-artifacts/`

其中 PDF 原件和 Markdown 抽取版都是 research input，不是 Current 事实源。最新详细度基准是：

- `zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`
- `zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md`

吸收其结论时必须重新区分 Current、Target、Future 和 History；正式结论进入 `docs/architecture/architecture.md`，并通过 `python tools/agent/render_architecture.py --write` 同步 `.agent/architecture/architecture.md` 与两份 HTML。为了方便人类读者，最新 PDF 也复制到 `docs/architecture/assets/`；该附件不替代正式架构源。

## 最近完成归档

上一轮完成并归档的 program：`zuno-architecture-detail-and-execution-plan-v1`

- 归档目录：`docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`
- 范围：PHASE01-PHASE05。
- 状态：completed / archived。
- 产物：正式架构 Markdown、十类 Mermaid 图、架构 HTML、后续大型执行计划。

八大交付物闭环 program：`zuno-eight-deliverables-full-realization-v1`

- 归档目录：`docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- 范围：PHASE01-PHASE10。
- 状态：completed / archived。
- 执行方式：主线程目标模式 + 默认开启线程内多 agent 协作；这是 Codex 执行协作，不是 Zuno runtime 架构，也不是多线程 runtime。

这个 program 完整落实八大交付物：

1. Agent 工作流文档系统。
2. 元工作流自我维护系统。
3. 模板与执行计划系统。
4. 正式架构文档系统。
5. 架构 HTML 展示系统。
6. 完善的 Zuno 目标架构。
7. 清晰干净的代码和目录。
8. 一致性与验证系统。

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

Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档到：

- `docs/history/programs/zuno-six-layer-internalization-v1/`

它让六层内部拥有第一批清晰、可测试、无副作用的目标层入口。它不表示 production-grade memory extraction、retrieval consolidation、Memory DB、dynamic capability orchestration、retrieval fusion 或 full Runtime Architecture Upgrade 已完成。

## 当前工作流治理事实

Architecture Documentation Governance 和 Agent Workflow Self-Maintenance 已登记为当前工作流规则：

- `docs/architecture/` 是 human-facing formal architecture source。
- `docs/architecture/architecture.md` 是文字总架构文档。
- `docs/architecture/architecture.html` 是生成展示页，不是唯一事实来源。
- `.agent/architecture/architecture.md` 是 Agent 侧总架构维护文档。
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
