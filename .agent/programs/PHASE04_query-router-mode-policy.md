# PHASE04 Query Router Mode Policy

Program: `zuno-eight-deliverables-full-realization-v1`
status: active

## 为什么

普通 / 增强 / 自动三种产品模式如果没有 runtime contract，会让 Agentic RAG、GraphRAG 和 fallback 都变成 prompt 习惯。先固定模式和内部方法，后续 memory、tool、knowledge 才有稳定入口。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- 产品模式：`normal`、`enhanced`、`auto`。
- 内部方法：`basic`、`local`、`global`、`drift`。
- `auto` 只做 router，不成为第五种 retrieval 方法。

## 执行步骤

1. 审计现有请求 DTO、AgentRuntime、GeneralAgent 和 knowledge query path。
2. 设计 mode / query_method / fallback / budget / evidence coverage contract。
3. 实现最小破坏的 router policy 和 trace 字段。
4. 增加 focused tests，证明旧请求兼容、新模式可解释。
5. 同步 architecture docs 和 eval contract。

## 验收

- 模式选择和内部 query_method 能在 trace 中解释。
- `auto` 的路由结果可测试，fallback 可追踪。
- 不改变既有 API response shape，除非本 phase 明确补 contract 和兼容测试。
- docs 只把已实现字段写入 Current。

## PR 边界

建议拆成 contract/docs PR、runtime policy PR、trace/eval PR。
