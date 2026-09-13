# 模拟简历 — rb-2026-09-14-resume-human-017

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目；在已有系统基础上持续参与 Agent、Tool/MCP、GraphRAG、Context/Memory 等方向开发，项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- 重构单 Agent Tool Calling 策略，将 MCPAgent-as-Tool 改为主 Agent 直接绑定具体 MCP Tools，并支持调用期注入用户级 Server 配置。
- 完善 Workspace MCP 调用路由，加入 deterministic direct route / ReAct fallback，修复自定义 MCP 名称递归与天气参数解析问题。
- 优化 GraphRAG 检索质量，在 5 条 HotpotQA smoke 中定位排序回退，改进候选融合、实体归一化和路径排序，Recall@5 由 0.80 恢复至 1.00。
- 落地 Context / Memory V2 基础能力，完善 typed Context / Memory 数据结构、scope、Agent 调用前后读写接入与轻量 ContextOrchestrator。
- 完善 Context / Memory 调用前 readback，将同 scope 的 task summary 与审核通过的 structured memory 注入上下文，并补 review / provenance 约束。
- 围绕 Tool Calling、GraphRAG 与 Context / Memory 补充回归测试和 retrieval smoke，覆盖 direct route、配置注入、structured result、review / provenance 等关键路径。
