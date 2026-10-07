# 模拟简历 — rb-2026-09-15-formal-019

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，持续参与 Tool/MCP、知识检索与 Context/Memory 等核心链路研发；项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- 重构单 Agent Tool Calling：针对 MCP Tool 需经子 Agent 转发、用户配置跨层传递的问题，将具体 MCP Tools 直接绑定主 Agent，并在调用时按 Tool–Server 映射注入用户级配置。
- 完善 Workspace Tool 路由：目标与参数明确的一步请求走 direct route，复杂或参数不完整任务回落 ReAct；修复自定义 MCP 名称递归与天气自然语言参数抽取问题，并用回归测试固定路由边界。
- 定位 GraphRAG 排序回退：在 HotpotQA development smoke 中发现 graph candidates 会将 baseline 已命中文档挤出 Top-K；实现 baseline-preserving fusion，保留 Vector/BM25 原始 rank，并按图证据强度分层晋升候选。
- 继续优化多跳图检索：实现 candidate-aware seed expansion、实体别名归一化与 path-aware ranking，改善 seed 覆盖、实体匹配和路径证据利用；5-query smoke 修复后恢复到 baseline 水平。
- 构建 scoped Context / Memory V2：统一 typed contracts 与 scope 约束，接入 Agent 调用前读取、回合后写入和轻量 ContextOrchestrator，使上下文组装由统一入口按作用域完成。
- 收紧 Memory readback：仅将同 scope 的 task summary 与审核通过的 structured memory 注入 `prepare_context()`，增加 source trace、review / provenance 约束及 focused tests。
