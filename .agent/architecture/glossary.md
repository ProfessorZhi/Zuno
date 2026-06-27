# 架构术语表

## 知识库（Knowledge Base）

用户可见的知识集合，包含文件、chunk、索引和检索设置。

## GraphRAG 项目（GraphRAG Project）

目标 GraphRAG 单元，承载 settings、prompt、input、output、cache、index、community assets、query method 和 trace metadata。

## 提示词调优（Prompt Tuning）

索引阶段根据项目数据调整图谱生成 prompt 的过程。

## 索引版本（Index Version）

vector、BM25、graph 和 community assets 的版本标识。

## 提示词版本（Prompt Version）

extraction、indexing 或 query prompt 的版本标识。

## 查询方法（Query Method）

回答策略，包括 `auto`、`basic`、`local`、`global`、`drift`。

## 检索器（Retriever）

召回通道，例如 BM25、dense vector、graph、community report search 或 requery。

## 证据包（Evidence Bundle）

用于支撑答案的文档、图路径、community report、citation 和 support verdict。

## 引用（Citation）

答案内容到 source chunk、file 或 graph-supported evidence 的引用。

## 重新查询（Requery）

使用改写 query 或 follow-up query 做的有条件二次检索。

## 社区报告（Community Report）

GraphRAG 资产，用于总结图社区。它支撑 `global` 和 `drift`，不是第一层 query method。

## Basic 查询模式

近期强非图 RAG baseline：BM25、dense vector、fusion、rerank、evidence check、requery 和 citation。

## Local 查询模式

GraphRAG query method，用于实体相关问题，依赖 graph paths / neighbors 和 raw chunks。

## Global 查询模式

基于 community reports 的 GraphRAG query method，通常是 map-reduce 风格。

## DRIFT 查询模式

GraphRAG query method，使用 community context 生成后续 local 或 basic retrieval。

## 已退休的 Domain Pack

旧 domain-specific packaging surface。当前主线不再把 Domain Pack 当作 active product/runtime 架构，但迁移 alias、DB compatibility、eval CLI compatibility、retirement/history tests 中可能保留相关字段。
