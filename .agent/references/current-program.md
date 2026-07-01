# 当前 Program 状态

## Current Truth

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-production-document-ingestion-and-thread-foundation-v1

`.agent/programs/` 当前处于 no-active 等待态。最近完成并归档的 program 是：

- `zuno-production-document-ingestion-and-thread-foundation-v1`
- 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

该 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1。它已完成企业知识库文档解析与索引交接地基：Document IR、parser worker、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 闭环、Program 2 thread prompts 和 no-active closure。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。本轮继续保留 runtime-first / vertical-slice-first 验收规则：只写 contract、schema 或 README 不能关闭 runtime phase。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。

## 当前 Front Path 文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/README.md`
- `.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`
- `.agent/programs/queued-programs/PROGRAM03_agent-planning-integration.md`
- `.agent/programs/queued-programs/PROGRAM04_enterprise-knowledge-eval-benchmark.md`

no-active 状态下，`.agent/programs/` 根目录不得保留 `PHASE*.md` 或旧 `thread-prompts/`。completed program 的 phase 和 prompt evidence 必须在 `docs/history/programs/` 归档。

## Program Suite 顺序

1. `zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 范围：Document Ingestion、Document IR、parser worker、index handoff、fixtures、Program 2 thread prompts。
2. `zuno-runtime-subsystems-parallel-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`。
   - 范围：Memory / Context、Tool / Sandbox、Security / Governance、GraphRAG / Index 四线程并行。
3. `zuno-agent-planning-integration-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM03_agent-planning-integration.md`。
   - 范围：合并 Program 2，落地真实 planning / ReAct / reflection / replan。
4. `zuno-enterprise-knowledge-eval-benchmark-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM04_enterprise-knowledge-eval-benchmark.md`。
   - 范围：企业知识库问答自动化评测、baseline 对比、LangSmith / OTel trace bridge、release gate。

## 最近完成归档

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 PHASE01-PHASE08、workspace ingest -> ParseGateway、Program 2 prompts、验证和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成 PHASE01-PHASE12、四大总交付物、八类 runtime-first 交付物、release closure、full verification 和 no-active closure，把 Zuno 推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大治理交付物闭环，范围是 PHASE01-PHASE10。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 final alias surface closure；旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 当前没有 active program；新 program 必须按 PHASE01 -> closure 顺序推进。
- active phase 文件只在有 active program 时平铺在 `.agent/programs/` 根目录。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是 Program 4 的评测对照组，不是最终产品模式。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
