# ADR 0001: Domain Pack Binding

## Status

Superseded.

This decision is retained as History because Phase 11A/11B and the target
architecture replaced Domain Pack as the mainline with GraphRAG Project
contracts. Remaining `domain_pack_id` fields are migration compatibility, not
the target binding model.

## Original Decision

优先把 `domain_pack_id` 绑定到 `knowledge`，并允许 `agent` 声明默认值。

## Original Reason

- schema 首先依赖知识材料
- 多知识库场景需要按 knowledge 维度区分领域
- agent 默认值可以降低配置成本

## Original Result

- GraphRAG 抽取和检索以 knowledge 绑定为主
- agent 作为默认入口，而不是唯一来源
