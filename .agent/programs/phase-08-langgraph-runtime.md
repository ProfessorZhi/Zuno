# Phase 08：GeneralAgent LangGraph 运行时

## 目标

显式化 runtime graph，同时保持单一 `GeneralAgent` 聊天主线。

## 范围

- `prepare_context -> agent_loop -> post_turn_commit` 的显式状态图。
- checkpoint、interrupt、resume、stream 兼容性。
- LangChain message / model / tool / structured output 抽象继续通过 Agent runtime 进入。
- LangGraph 管状态循环，不负责业务知识检索策略。

## 不在范围内

- 默认多 Agent supervisor。
- 第二套 GraphRAG chat runtime。
- 产品级自动任务编排。

## 退出标准

- 单次聊天路径只进入一个 GeneralAgent runtime。
- state、checkpoint、interrupt、resume、stream 有聚焦测试。
- Context/Memory、Capability、Knowledge trace 在 runtime graph 内可见。

## 验证

- 聚焦 GeneralAgent runtime 测试。
- 受影响 API/SSE 测试。
- Agent/doc 边界验证。
