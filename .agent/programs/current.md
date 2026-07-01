# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

## 当前状态

`.agent/programs/` 当前没有 active program。最近完成并归档的 program 是 Program 1B / V2：

- `zuno-enterprise-document-ingestion-platform-v2`
- 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

该 program 属于 `zuno-enterprise-agentic-graphrag-production-suite-v1`。

该 program 已完成企业级文档输入与持久化平台雏形：local source object、SQLite durable store、workspace file metadata、parse job / snapshot、document version / block / IR、index manifest / chunk / citation lineage、workspace task / event / artifact / feedback 和 restart recovery focused tests。成熟度展开以 `docs/architecture/production-readiness.md` 为准。

## 后续 queued program

Program 3-5 仍为 queued，不是当前 active program：

1. `zuno-runtime-subsystems-parallel-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`
2. `zuno-agent-planning-integration-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`
3. `zuno-enterprise-knowledge-eval-benchmark-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`

## 最近完成归档

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`：完成 PHASE01-PHASE08 的 Program 1B / V2 durable ingestion closure。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 Program 1A 文档解析、Document IR、parser worker lifecycle、native parser、adapter boundary、index handoff、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成 PHASE01-PHASE12。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。

## 当前执行规则

- no-active 状态下，`.agent/programs/` 根目录只保留 `current.md`、`README.md`、`implementation-roadmap.md`、`closure-checklist.md` 和 `queued-programs/`。
- 新 program 必须从 `PHASE01` 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- Program 3-5 启动前必须重新确认 Codex UI 目标模式、worktree、branch、允许范围、禁止范围和验证闸门。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
