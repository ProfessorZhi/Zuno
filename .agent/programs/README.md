# Agent 执行计划

`.agent/programs/` 当前只保存一个 active program：`zuno-master-architecture-implementation-v1`。

## 当前状态

- State: active
- Active program: `zuno-master-architecture-implementation-v1`
- 当前阶段：[PHASE07_tool-control-plane-mcp-approval.md](PHASE07_tool-control-plane-mcp-approval.md)
- 当前入口：[current.md](current.md)

## Program 目标

本 program 是 Zuno 从“架构文档已经成型”进入“目标架构分阶段落地”的大型执行计划。它先整理项目文件夹、代码 ownership 和兼容边界，再按八个方面交付产品级能力，最后同步正式架构 Markdown、架构 HTML、README、verifier、tests 和历史归档。

本 program 不把 Target 写成 Current。每个 phase 只有在代码、测试、文档和可复现验证同时闭合后，才允许把对应能力写入 Current。

## 八个方面产物

1. 项目文件夹与代码布局治理。
2. 企业私有知识库场景与产品闭环。
3. 多格式 Document Ingestion / Parse Gateway。
4. Single Controller Agent Runtime / LangGraph 落地。
5. Context / Memory write-manage-read 系统。
6. Tool Control Plane / MCP / Approval / Sandbox。
7. RAG / GraphRAG / Evidence / Citation 知识系统。
8. Security / Eval / Observability / Architecture Docs / HTML 展示闭环。

## 前台文件

- [current.md](current.md)：当前 active program、边界和阶段状态。
- [implementation-roadmap.md](implementation-roadmap.md)：大型执行计划总图、产物矩阵、phase 顺序和验收门。
- [closure-checklist.md](closure-checklist.md)：program 收口前必须完成的检查。
- [PHASE01_program-baseline-and-previous-closure.md](PHASE01_program-baseline-and-previous-closure.md)：completed，收口上一轮架构计划状态，固定新 program 基线。
- [PHASE02_project-folder-and-code-layout-cleanup.md](PHASE02_project-folder-and-code-layout-cleanup.md)：completed，项目文件夹、代码 ownership、compat/vendor 边界治理。
- [PHASE03_enterprise-scenario-and-product-loop.md](PHASE03_enterprise-scenario-and-product-loop.md)：completed，企业知识库主场景、workspace、task/session、artifact、event flow。
- [PHASE04_document-ingestion-parse-gateway.md](PHASE04_document-ingestion-parse-gateway.md)：completed，多格式解析 contract、Canonical Document IR、parser router、index handoff 和 parser golden fixtures。
- [PHASE05_agent-runtime-langgraph-harness.md](PHASE05_agent-runtime-langgraph-harness.md)：completed，Single Controller runtime harness contract、node table、checkpoint、interrupt/resume 和 stream event bridge。
- [PHASE06_context-memory-system.md](PHASE06_context-memory-system.md)：completed，MemoryEngine、九类 taxonomy、read/write/manage API、Context Pack renderer 和 memory eval policy。
- [PHASE07_tool-control-plane-mcp-approval.md](PHASE07_tool-control-plane-mcp-approval.md)：active，ToolCard、manifest、selector、executor adapter、MCP、approval、sandbox。
- [PHASE08_rag-graphrag-evidence-citation.md](PHASE08_rag-graphrag-evidence-citation.md)：basic/local/global/drift、retrieval fusion、GraphRAG indexing/query、citation。
- [PHASE09_security-governance-sandbox.md](PHASE09_security-governance-sandbox.md)：输入、检索、工具、输出四道安全闸和沙箱治理。
- [PHASE10_eval-observability-langsmith.md](PHASE10_eval-observability-langsmith.md)：trace schema、LangSmith adapter、offline/online eval、CI regression gate。
- [PHASE11_architecture-docs-html-refresh.md](PHASE11_architecture-docs-html-refresh.md)：正式架构 Markdown、Agent 镜像、HTML 展示和图集更新。
- [PHASE12_validation-release-closure.md](PHASE12_validation-release-closure.md)：全量验证、归档、README 状态和发布证据。

## 最近归档

- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
- `docs/history/programs/zuno-six-layer-internalization-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

## 使用规则

- 每次只打开一个 active program。
- 每个新 program 从 `PHASE01` 开始。
- active phase 文件必须平铺在 `.agent/programs/` 根目录。
- completed program 必须归档到 `docs/history/programs/`。
- 任何 runtime 能力落地，都必须同时更新 architecture docs、verifier/tests 和 README 状态面。
