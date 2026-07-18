# ADR 0005: 引入官方 LangGraph PostgreSQL Checkpointer

status: accepted
date: 2026-07-18

## Context

PHASE04 的完成定义要求真实 LangGraph PostgreSQL Checkpointer，不允许用 `infra_checkpoints` primitive、SQLite store 或自定义 bridge 代替。`phase04-readiness.yaml` 将 P04-T06 标记为 blocked，原因是新增官方关键依赖需要 Coordinator Decision。

当前仓库已有 `langgraph` 和 `langgraph-prebuilt`，但没有官方 PostgreSQL Checkpointer 包。`pip index versions langgraph-checkpoint-postgres` 显示当前可用版本为 `3.1.0`。

## Decision

允许在 PHASE04 范围内引入 `langgraph-checkpoint-postgres = "3.1.0"`，并以 `langgraph.checkpoint.postgres.PostgresSaver` 作为官方 Checkpointer adapter 的唯一基础。

`PostgresSaver.setup()` 创建的官方 `checkpoint_*` 表属于 LangGraph Checkpointer schema，不归 Zuno 领域事实 Owner，不得被解释为 Agent、Product、Knowledge、Memory 或 Tool 的领域成功。Zuno 自有 `infra_checkpoints` 仍只保留为 Infrastructure primitive receipt / boundary evidence，不能替代官方 saver。

## Consequences

- PHASE04 可以从“官方依赖未安装”推进到“官方 saver 基础路径可验证”。
- 仍必须补齐 official Checkpointer interrupt/resume、thread isolation、generation/schema、restore/recovery、domain/checkpoint reconcile 和 combined-service fault 证据后，PHASE04 才能关闭。
- Unknown adapter/schema major version 仍必须 fail closed。
- 本 ADR 不批准永久 dual checkpointer runtime，也不批准把 checkpoint receipt 当作领域成功。
