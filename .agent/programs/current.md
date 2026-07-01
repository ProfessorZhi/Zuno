# 当前程序

state: active
active_program: zuno-enterprise-document-ingestion-platform-v2
current_phase: PHASE02_durable-storage-contract
latest_completed_program: zuno-production-document-ingestion-and-thread-foundation-v1

## 当前状态

`.agent/programs/` 当前 active program 是 `zuno-enterprise-document-ingestion-platform-v2`，业务口径是 Program 1B / V2。上一轮 Program 1A 已完成并归档：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

Program 1A 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的已完成文档入口地基：workspace ingest 进入 `ParseGateway.submit_parse_job()`，解析结果进入 `CanonicalDocumentIR`，parser job snapshot 进入 `KnowledgeIndexRuntime.index_document()`，index manifest 和 retrieval chunk 保留 parse lineage、document version、source hash、ACL、sensitivity 和 `citation_lineage`。

Program 1B / V2 的目标是把 Program 1A 的 local runtime slice 升级为企业级文档输入与持久化平台雏形。成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准；文档输入层展开契约以 `docs/architecture/document-ingestion-foundation.md`、本 active phase 和归档 closure summary 为准。

## 当前 phase

- `PHASE02_durable-storage-contract.md`
  - 状态：active。
  - 模式：TDD implementation。
  - 目标：定义并实现最小 SQLite-compatible durable storage contract，让 source object、workspace file、parse snapshot、document version、index manifest 和 index chunks 可以 round-trip。

## 已完成 phase evidence

- `PHASE01_truth-source-and-gap-audit.md`
  - 状态：completed。
  - 证据：current gap matrix、storage target matrix、API compatibility map、dependency probe 和 PHASE02 输入清单已完成并推送。

## 后续 queued program

Program 3-5 仍为 queued，不是当前 active program：

1. `zuno-runtime-subsystems-parallel-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`
   - 可复用提示词归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/thread-prompts/`
2. `zuno-agent-planning-integration-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`
3. `zuno-enterprise-knowledge-eval-benchmark-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`

## 最近完成归档

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 PHASE01-PHASE08 的文档解析、Document IR、parser worker lifecycle、native parser、adapter boundary、index handoff、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成 PHASE01-PHASE12、四大总交付物、八类 runtime-first deliverables、release closure、full verification 和 no-active closure，把 Zuno 推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。

## 当前执行规则

- active 状态下，`.agent/programs/` 根目录保留 `current.md`、`README.md`、`implementation-roadmap.md`、`closure-checklist.md`、当前 active phase 文件和本 active program 已完成 phase evidence 文件。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- Program 1B / V2 必须从 PHASE01 只读审计开始；runtime 代码修改从 PHASE02 开始。
- Runtime Subsystems 多线程提示词归档为历史交接资产；真正启动 Program 3 子线程时仍必须重新确认 Codex UI 目标模式、worktree、branch、允许范围、禁止范围和验证闸门。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
