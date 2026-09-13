# 模拟简历 — rb-2026-09-14-resume-human-017

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，整合工具调用、知识检索与上下文管理，经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- 参与单 Agent Tool Calling 重构，去掉 MCPAgent-as-Tool 嵌套层，改为主 Agent 直连 Tool，并支持用户级 MCP 配置注入。
- 完善 Workspace 工具路由与回归测试，加入 direct route / ReAct fallback，修复自定义 MCP 名称递归和天气参数解析问题。
- 定位 5 条 HotpotQA smoke 中 GraphRAG 的 Recall@5 回退，优化候选融合与排序，同日复测由 0.80 恢复至 1.00。
- 参与 Context / Memory V2 落地，完善 scope 与调用前 readback，将同 scope 的任务摘要和审核后 memory 接入模型上下文。
