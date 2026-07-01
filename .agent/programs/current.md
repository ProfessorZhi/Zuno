# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-production-document-ingestion-and-thread-foundation-v1

## 当前状态

`.agent/programs/` 当前处于 no-active 等待态。上一轮 active program 已完成并归档：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

该 program 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的 Program 1，已完成企业知识库文档入口地基：workspace ingest 进入 `ParseGateway.submit_parse_job()`，解析结果进入 `CanonicalDocumentIR`，parser job snapshot 进入 `KnowledgeIndexRuntime.index_document()`，index manifest 和 retrieval chunk 保留 parse lineage、document version、source hash、ACL、sensitivity 和 `citation_lineage`。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准；Program 1 的展开契约以 `docs/architecture/document-ingestion-foundation.md` 和归档 closure summary 为准。

## 下一轮候选

Program 2-4 仍为 queued，不是当前 active program：

1. `zuno-runtime-subsystems-parallel-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM02_runtime-subsystems-parallel.md`
   - 可复用提示词归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`
2. `zuno-agent-planning-integration-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM03_agent-planning-integration.md`
3. `zuno-enterprise-knowledge-eval-benchmark-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM04_enterprise-knowledge-eval-benchmark.md`

## 最近完成归档

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 PHASE01-PHASE08 的文档解析、Document IR、parser worker lifecycle、native parser、adapter boundary、index handoff、Program 2 prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成 PHASE01-PHASE12、四大总交付物、八类 runtime-first deliverables、release closure、full verification 和 no-active closure，把 Zuno 推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。

## 当前执行规则

- no-active 状态下，`.agent/programs/` 根目录只保留 `current.md`、`README.md`、`implementation-roadmap.md` 和 `closure-checklist.md`；active phase 文件必须在 completed program archive 中。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- 启动新 program 必须从 `PHASE01` 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- Program 2 多线程提示词归档为历史交接资产；真正启动子线程时仍必须重新确认 Codex UI 目标模式、worktree、branch、允许范围、禁止范围和验证闸门。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
