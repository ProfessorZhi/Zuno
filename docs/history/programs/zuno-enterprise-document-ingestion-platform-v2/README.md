# Agent 执行计划

本目录是 Program 2 `zuno-enterprise-document-ingestion-platform-v2` 的完成归档。

## 当前状态

- State: completed / archived
- Program: `zuno-enterprise-document-ingestion-platform-v2`
- Closed phase range: `PHASE01` - `PHASE08`
- Previous completed program: `zuno-production-document-ingestion-and-thread-foundation-v1`

Program 2 已完成并归档到本目录。Program 1 已归档到：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

## 归档文件

- `current.md`：Program 2 completed state、归档位置、后续 queued program 和历史边界。
- `implementation-roadmap.md`：Program 1-5 总路线、依赖和状态。
- `closure-checklist.md`：Program 2 closure 检查、验证命令和剩余 Target。
- `closure-summary.md`：最终 completion summary、Current evidence 和 Remaining Target。
- `PHASE01_truth-source-and-gap-audit.md`：gap audit 和 PHASE02 输入清单。
- `PHASE02_durable-storage-contract.md`：最小 durable store contract、TDD red / green evidence。
- `PHASE03_workspace-file-durable-input.md`：`/workspace/file` durable input。
- `PHASE04_parse-document-persistence.md`：parse job、snapshot、document version、document blocks 持久化。
- `PHASE05_index-persistence-rehydrate.md`：index manifest / chunks 持久化和 rehydrate。
- `PHASE06_workspace-product-durable-closure.md`：workspace task、events、artifact、feedback 持久化。
- `PHASE07_restart-recovery-end-to-end.md`：restart recovery focused test。
- `PHASE08_docs-verifier-closure.md`：docs、verifier、archive 和 validation closure。

## 已完成 Program 1

`zuno-production-document-ingestion-and-thread-foundation-v1` 已完成 PHASE01-PHASE08：

- parser current audit
- Document IR / parser adapter contract freeze
- parser worker runtime and job lifecycle
- native text and structured file parsers
- PDF / Office / OCR / VLM adapter boundaries
- index handoff provenance and fixtures
- 后续 Runtime Subsystems thread prompts and branch plan
- verification, docs sync and no-active closure

Runtime Subsystems thread prompts 保存在归档目录的 `thread-prompts/` 下。它们是后续 Program 3 可复用输入，不代表 Program 3 已启动。

## Program 2 完成边界

Program 2 已把 Program 1 的 local runtime slice 推进到 Product V1 local durable ingestion baseline：

- `/workspace/file` 保存 local source object、source hash、storage uri 和 workspace file metadata。
- `/workspace/ingest` 继续走 `ParseGateway.submit_parse_job()`，并持久化 parse job、parse snapshot、document version、document blocks、index manifest、index chunks 和 citation lineage。
- `KnowledgeIndexRuntime.rehydrate_index()` 可从持久化 manifest / chunks 恢复本地检索面。
- workspace task、events、artifact content/ref 和 feedback 可从 SQLite rehydrate。
- target-blocked parser diagnostics 可以持久化，不生成假 index。

Postgres、MinIO / S3、Redis / outbox / worker lease、external OCR / VLM、external index、enterprise SSO / RBAC / DLP 仍是 Production Scale Target。

## 使用规则

- no-active 状态下，`.agent/programs/` 根目录只保留 `current.md`、`README.md`、`implementation-roadmap.md`、`closure-checklist.md` 和 `queued-programs/`。
- 后续 queued program 可以放在 `.agent/programs/queued-programs/`，但不得写成 active program。
- 新 program 必须从 PHASE01 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
