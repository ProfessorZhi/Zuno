# Interview Question Bank

## Project Reality

- 客户具体是谁？为什么不是一个普通知识库？
- 你们几个人？谁负责什么？你亲自写了哪条关键路径？
- 有 Demo、Pilot 还是 Production？证据是什么？

## Code

- 第一次 clone 后怎么启动？
- 一个 Agent Run 从 API 到数据库、Memory、Tool、Answer 怎么走？
- Memory 写在哪里，何时召回，如何避免污染？
- Tool Call 的输入、Observation、失败和幂等是什么？

## Architecture

- 为什么 LangGraph，不用普通状态机？
- 为什么 GraphRAG，不用 Hybrid RAG？
- 为什么 Multi-Agent，不用一个强 Agent 加并行工具？
- 为什么微服务，不用模块化单体加 Worker？

## Failure / Scale

- MQ 重复消费怎么办？
- Tool 超时但外部副作用未知怎么办？
- 100 个并发 Agent Run 的瓶颈在哪里？
- 如何测质量、延迟、成本和证据充分性？

每个问题都要标事实状态，不能用 Target 回答 Historical。
