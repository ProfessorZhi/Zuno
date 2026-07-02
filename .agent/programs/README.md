# Agent 执行计划

`.agent/programs/` 当前处于 active 状态。

## 当前状态

- State: active
- Active program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- Current phase: `PHASE13_eval-trace-cost-benchmark.md`
- Latest completed program: `zuno-enterprise-document-ingestion-platform-v2`

当前 Program 3 Mega 合并原 active Program 3 与 queued Program 4-6，目标是在一个 program 内完成 Zuno 可上线企业知识库 Agentic GraphRAG product baseline 的全链路闭环计划。

PHASE12 End-to-End Product Runtime 已完成本地 E2E product baseline；当前 PHASE13 负责把 scenario / trace 输出汇总为 Eval / Trace / Cost / Benchmark baseline。

## 当前文件

- `current.md`：当前 active mega program、phase、workstream 和 superseded queued program。
- `implementation-roadmap.md`：Program 1 / 2 completed 与 Program 3 Mega active 的顺序、依赖和状态。
- `closure-checklist.md`：mega program 从 open 到 closure 的验收清单。
- `PHASE01_*.md` 到 `PHASE15_*.md`：mega program 平铺 phase gate 计划。
- `queued-programs/`：原 Program 4-6 的 superseded 输入文件，不是当前 active phase。

## Program 3 Mega 完成口径

Program 完成时必须能说：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

它至少要证明：

```text
upload/register -> local object store -> async ingest -> parse/document/index
  -> standard/deep retrieval -> planning/control -> skill/capability
  -> cited artifact -> trace/eval/cost -> feedback -> restart rehydrate
```

## 使用规则

- active 状态下，`.agent/programs/` 根目录只保留当前 mega program 的 PHASE 文件。
- superseded queued program 只能留在 `queued-programs/`，不得写成 active 或 completed。
- PHASE01 和 PHASE02 是顺序闸门；中间 workstream 可以并行；PHASE12-PHASE15 必须由 Coordinator 集成收口。
- 每个 runtime phase 必须有真实 API / service / worker 路径和 focused tests；只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
