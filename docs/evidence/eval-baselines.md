# Eval Baselines

## 用途

记录 Zuno Target Architecture Migration V1 closure 的正式 Eval baseline 状态，不暗示本页重新运行了测试或 eval。

## 当前状态

Zuno Target Architecture Migration V1 已关闭并归档。

本页记录的是 `ffa3add` closure evidence；它不是本轮文档同步重新执行出来的测试或 eval 结果。

Phase 11C active runtime cleanup 已完成。Phase 12 已通过 target migration closure evidence 关闭。

## Closure Evidence

- full pytest closure evidence：`714 passed, 3 warnings`
- Contract Review eval：
  - `dev_offline`：status=`ok`
  - `dev_local`：status=`ok`
- Stackless baseline comparison：
  - 核心 acceptance 通过。
  - `prefer_rerank_when_tied=no` 记录为 tuning signal，不包装为失败。
- Trace closure 已完成。eval JSONL 包含：
  - `trace_id`
  - `graphrag_project_id`
  - requested/resolved query method
  - evidence bundle
  - citation coverage
  - prompt version
  - query prompt version
  - index version
  - community version
  - latency
  - `cost=null`
- Legacy grep closure：
  - 457 hits
  - 全部 classified as `history_archive` or `migration_retirement_guard`
  - `needs_review=0`

## 当前边界

Context Orchestrator full product behavior 仍是 Target，不是成熟 Current。

Production-grade memory extraction、retrieval、consolidation 仍是 Target。

Product-level dynamic capability orchestration 仍是 Target。

`domain_pack_id` 仍可能存在于 migration alias、existing database-column compatibility、eval CLI compatibility、retirement/history tests。它不是 active mainline public architecture。
