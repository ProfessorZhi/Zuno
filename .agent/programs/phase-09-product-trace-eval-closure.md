# Phase 09：产品边界、Trace 与 Eval 收口

## 目标

用用户可理解的产品边界、trace evidence 和文档归档关闭 V2 实施。

## 范围

- API 和前端展示 memory/capability/evidence 状态的边界。
- 知识库页面展示 GraphRAG 建图配置边界，包括实体抽取 LLM、社区报告 LLM、Embedding、Rerank 和重建影响。
- trace JSONL 字段完整性。
- eval baseline 是否需要更新由 evidence gate 决定。
- 前台文档只保留 Current、Target、Roadmap、Evidence、Terminology。
- 旧计划、旧 evidence、截图和临时产物归档或排除出前台。

## 不在范围内

- 完整前端重设计。
- 生产级动态 capability 市场。
- 把 Future 方向提升为 Current。

## 退出标准

- 产品/API 文档明确区分 Current、Foundation、Target、Future 和 History。
- `.agent/` 保持精简：可执行 workflow、target design、references、scripts、templates 和归档指针。
- `docs/` 保持精简：正式文档、证据、术语和 history index。
- 完成 trace/eval closure evidence。

## 验证

- 完整 Agent/doc/repo hygiene 验证。
- 受影响 API/frontend contract 测试。
- 必要时运行 eval closure 命令。
