# 当前 Program 状态

## Current Truth

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

`.agent/programs/` 当前没有 active program。最近完成并归档的 program 是：

- `zuno-enterprise-document-ingestion-platform-v2`
- 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

该 program 属于 `zuno-enterprise-agentic-graphrag-production-suite-v1`。

该 program 是 Program 1B / V2，已把 Program 1A 的 local runtime slice 推进到企业级文档输入与持久化平台雏形，即 Product V1 local durable ingestion baseline：source object、workspace file、parse job、parse snapshot、document version、document blocks、index manifest、index chunks、citation lineage、task、events、artifact content/ref、feedback 和 restart recovery 均有 focused tests。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。Postgres、Redis、MinIO / S3、external OCR / VLM、external index、worker lease 和 production parser worker 仍是 Target / Production Scale Target。

## 当前 Front Path 文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/queued-programs/README.md`
- `.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`
- `.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`
- `.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`

no-active 状态下，`.agent/programs/` 根目录不得保留 `PHASE*.md`。completed program 的 phase 和 closure evidence 必须在 `docs/history/programs/` 归档。

## Program Suite 顺序

1. `zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
2. `zuno-enterprise-document-ingestion-platform-v2`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
3. `zuno-runtime-subsystems-parallel-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM03_runtime-subsystems-parallel.md`
4. `zuno-agent-planning-integration-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM04_agent-planning-integration.md`
5. `zuno-enterprise-knowledge-eval-benchmark-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM05_enterprise-knowledge-eval-benchmark.md`

## 最近完成归档

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`：完成 PHASE01-PHASE08、durable ingestion、restart recovery、验证和 no-active closure。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 Program 1A 的 Document IR、parser worker、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 闭环、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：Program 4 / `zuno-six-layer-internalization-v1` 的六层内部入口、README、focused tests 和 verifier guard 历史完成事实。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成 PHASE01-PHASE10 的上一轮八大治理交付物闭环。
- `zuno-repo-layout-cleanup-v1`：repo layout cleanup 历史完成 program id，前台不恢复旧布局。

## 历史完成事实锚点

- Program 3 final alias surface closure 已完成；旧 public import path 通过 `legacy_aliases.py` 注册兼容，`src/backend/` 前台只保留 `zuno/`。
- `zuno-runtime-architecture-upgrade-v1` 和 `zuno-architecture-visuals-v1` 是旧队列 / 历史方向名称，不是当前 active program；当前 queued program 以 Program 3-5 列表为准。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 新 active program 必须从 PHASE01 开始。
- 新 runtime program 继续遵守 runtime-first / vertical-slice-first；只写 contract、schema 或 README 不能关闭 runtime phase。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是 Program 5 的评测对照组，不是最终产品模式。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`
