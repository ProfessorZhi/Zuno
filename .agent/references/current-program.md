# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-production-document-ingestion-and-thread-foundation-v1
current_phase: PHASE01_program-truth-source-and-parser-current-audit.md
latest_completed_program: zuno-production-architecture-and-deliverables-completion-v1

`.agent/programs/` 当前处于 active program 状态。当前 active program 是：

- `zuno-production-document-ingestion-and-thread-foundation-v1`

该 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1。它负责把企业知识库文档解析与索引交接地基做清楚、做扎实，并准备 Program 2 多线程施工的目标模式提示词、分支边界和验收闸门。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。本轮继续保留 runtime-first / vertical-slice-first 验收规则：只写 contract、schema 或 README 不能关闭 runtime phase。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。

## 当前 Active Program 文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_program-truth-source-and-parser-current-audit.md`
- `.agent/programs/PHASE02_document-ir-and-parser-contract-freeze.md`
- `.agent/programs/PHASE03_parser-worker-runtime-and-job-lifecycle.md`
- `.agent/programs/PHASE04_native-text-and-structured-file-parsers.md`
- `.agent/programs/PHASE05_pdf-office-ocr-adapter-boundaries.md`
- `.agent/programs/PHASE06_index-handoff-provenance-and-fixtures.md`
- `.agent/programs/PHASE07_program2-thread-prompts-and-branch-plan.md`
- `.agent/programs/PHASE08_verification-doc-sync-and-closure.md`

## Program Suite 顺序

1. `zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：active。
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

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 当前 active program 必须按 PHASE01 -> PHASE08 顺序推进。
- active phase 文件只在有 active program 时平铺在 `.agent/programs/` 根目录。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是 Program 4 的评测对照组，不是最终产品模式。

## 最近完成归档

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成 PHASE01-PHASE12、四大总交付物、八类 runtime-first 交付物、release closure、full verification 和 no-active closure，把 Zuno 推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`：完成架构文档、架构图、HTML 和后续执行计划细化。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成上一轮八大治理交付物闭环，范围是 PHASE01-PHASE10。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：完成六层内部第一批 foundation surfaces。
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`：完成顶层六层目录和 final alias surface closure；旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
