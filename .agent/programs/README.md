# Agent 执行计划

`.agent/programs/` 当前处于 active 状态。

## 当前状态

- State: active
- Active program: `zuno-enterprise-ingestion-async-infrastructure-v1`
- Current phase: `PHASE01_truth-source-and-async-gap-audit.md`
- Latest completed program: `zuno-enterprise-document-ingestion-platform-v2`

Program 3 是 Program 2 之后、Runtime Subsystems 之前的企业文档输入异步基础设施 program。它不改写 Program 1 / Program 2 历史完成事实，而是补齐 Program 2 Remaining Target 中最贴近 ingestion 主链路的基础设施：PostgreSQL-compatible store boundary、ObjectStore binary support、QueueBackend、RabbitMQ boundary、Redis runtime state boundary、ParserWorker / IndexWorker、outbox、dead letter、reconciler、OCR / VLM worker boundary。

## 当前文件

- `current.md`：当前 active program、phase 和后续 queued program。
- `implementation-roadmap.md`：Program 1-6 的顺序、依赖和状态。
- `closure-checklist.md`：Program 3 从 open 到 closure 的验收清单。
- `PHASE01_*.md` 到 `PHASE12_*.md`：Program 3 平铺 phase 计划。
- `queued-programs/`：Program 4-6 的后续计划，不是当前 active phase。

## 已归档 Program 2

`zuno-enterprise-document-ingestion-platform-v2` 已完成 PHASE01-PHASE08：

- truth source and gap audit
- durable storage contract
- workspace file durable input
- parse / document persistence
- index persistence / rehydrate
- workspace product durable closure
- restart recovery end-to-end
- docs / verifier / archive closure

## Program 3 完成口径

Program 3 完成时必须能说：

```text
Enterprise ingestion async infrastructure baseline completed.
```

它至少要证明：

```text
file -> object store -> queued ingest -> parser worker -> document version
     -> index worker -> index chunks / citation lineage
     -> status query -> restart recovery -> reconciler check
```

## 使用规则

- active 状态下，`.agent/programs/` 根目录保留当前 Program 3 的 PHASE 文件。
- queued program 只能放在 `queued-programs/`，不得写成 active 或 completed。
- Program 3 每个 runtime phase 必须有真实 API / service / worker 路径和 focused tests；只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
