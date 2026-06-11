# ADR 0001: Domain Pack Binding

## 状态

Accepted

## 决策

优先把 `domain_pack_id` 绑定到 `knowledge`，并允许 `agent` 声明默认值。

## 原因

- schema 首先依赖知识材料
- 多知识库场景需要按 knowledge 维度区分领域
- agent 默认值可以降低配置成本

## 结果

- GraphRAG 抽取和检索以 knowledge 绑定为主
- agent 作为默认入口，而不是唯一来源
