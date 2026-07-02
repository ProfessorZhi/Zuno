# Agent 执行计划

`.agent/programs/` 当前处于 no-active 状态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

最近完成并归档的 Program 3 Mega 已完成本地可验证的 launchable enterprise Agentic GraphRAG product baseline。归档入口：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

## 当前文件

- `current.md`：当前 no-active 状态、最近完成 program 和下一轮规则。
- `implementation-roadmap.md`：Program 1 / 2 / 3 completed 与 no-active 状态。
- `closure-checklist.md`：最近完成 program 的最终验收摘要和下一轮检查入口。
- `queued-programs/README.md`：当前没有 queued program；旧 Program 4-6 已随 Program 3 Mega 归档为 merged inputs。

## 最近完成口径

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

这表示所有关键层都有 local runnable implementation、adapter boundary、dependency probe / target-blocked evidence、focused tests、E2E 闭环、trace/eval/cost 记录和文档成熟度边界。它不表示已经部署真实 PostgreSQL / RabbitMQ / Redis / MinIO / OCR / VLM / external index 集群。

## 使用规则

- no-active 状态下，不在 `.agent/programs/` 根目录保留 PHASE 文件。
- completed program 的 phase、closure summary 和 merged queued inputs 必须留在 `docs/history/programs/`。
- 新 program 必须从 `PHASE01` 开始，并同步 `AGENTS.md`、README、`.agent/references/current-program.md`、verifier 和 repo tests。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 多线程执行必须由当前主线程先确认真实 UI 目标模式和独立 worktree / branch；提示词目标模式不等于 Codex UI 目标模式。
