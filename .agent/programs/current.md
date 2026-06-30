# 当前程序

当前 active program：`zuno-master-architecture-implementation-v1`

state: active
current_phase: PHASE05_agent-runtime-langgraph-harness

## 目标

本 program 把 Zuno 从“目标架构文档与架构图已经成型”推进到“目标架构分阶段实现”。它先整理项目文件夹和代码分布，再围绕企业私有知识库与多功能 Agent 助手计划交付八个方面目标产物，并同步架构 Markdown、架构 HTML、README、verifier、tests 和历史归档。

## 为什么先做文件夹整理

当前 `src/backend/zuno` 顶层已经收口为 `api / agent / memory / capability / knowledge / platform` 六层，但六层内部仍有 facade、旧 implementation、compat import、vendor、provider tools 和平台 services 混住的问题。直接实现 runtime feature 会继续把旧目录越堆越厚，所以本 program 第一段必须先完成 ownership matrix、compat/vendor 边界、可再生成缓存清理和 verifier 固定。

## 八个方面产物（目标产物）

| 编号 | 产物面 | 目标 |
| --- | --- | --- |
| D1 | 项目文件夹与代码布局治理 | 让目录能表达责任边界，减少 platform/services 和 capability/tools 的视觉噪音。 |
| D2 | 企业私有知识库场景与产品闭环 | 明确 workspace、task/session、upload、artifact、SSE/WebSocket、trace panel 的产品链路。 |
| D3 | Document Ingestion / Parse Gateway | 计划支持 PDF、Office、图片、代码、TXT、MD、HTML 等常见文件，统一输出 Canonical Document IR。 |
| D4 | Single Controller Agent Runtime | 计划用 LangGraph-compatible harness 实现 prepare_context、plan、ReAct、reflect、replan、post_turn_commit。 |
| D5 | Context / Memory 系统 | 计划实现 Raw Event Log、Recent Window、Task Summary、Structured Memory、promotion/decay。 |
| D6 | Tool Control Plane | 计划实现 ToolCard manifest、selector、policy、approval、executor adapter、MCP 和 sandbox。 |
| D7 | RAG / GraphRAG 知识系统 | 计划实现 basic/local/global/drift、retrieval fusion、GraphRAG indexing/query、Evidence/Citation。 |
| D8 | 安全、评测、观测、文档展示闭环 | 计划实现 security gates、LangSmith-compatible trace/eval、architecture.md/html 更新和 release gate。 |

这些是本 program 的目标产物，不表示当前已经完成。每个产物只有在对应 phase 的 tests、verifier、eval evidence 或可复现 trace 通过后，才能从 Target 写入 Current。

## 当前阶段

- `PHASE01_program-baseline-and-previous-closure.md`：completed，已用 verifier 和 repo tests 证明当前 program 基线、历史归档和状态面一致。
- `PHASE02_project-folder-and-code-layout-cleanup.md`：completed。
- `PHASE03_enterprise-scenario-and-product-loop.md`：completed。
- `PHASE04_document-ingestion-parse-gateway.md`：completed。
- `PHASE05_agent-runtime-langgraph-harness.md`：active。
- `PHASE06_context-memory-system.md`：pending。
- `PHASE07_tool-control-plane-mcp-approval.md`：pending。
- `PHASE08_rag-graphrag-evidence-citation.md`：pending。
- `PHASE09_security-governance-sandbox.md`：pending。
- `PHASE10_eval-observability-langsmith.md`：pending。
- `PHASE11_architecture-docs-html-refresh.md`：pending。
- `PHASE12_validation-release-closure.md`：pending。

## 当前边界

- 本 program 可以创建和修改计划、文档、verifier、tests，并在对应 phase 中逐步修改 runtime code。
- 任何 runtime phase 必须先写或更新 focused tests，再做实现。
- 兼容路径不能为了视觉清爽直接删除；必须先由 import matrix 和 tests 证明替代路径可用。
- 生产级 Parse Gateway runtime、`LangGraph runtime`、`Memory DB`、`Tool approval`、`GraphRAG extraction/fusion`、`LangSmith trace/eval` 和 `security sandbox` 在对应 phase 完成前仍是 Target。
- 产品 runtime 默认仍是 Single Controller Agent；Codex 多线程和多 worktree 只属于工程交付方式。

## 最近完成归档

- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大交付物闭环。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 legacy alias surface closure。
