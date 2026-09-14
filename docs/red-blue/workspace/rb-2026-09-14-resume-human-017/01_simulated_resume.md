# 模拟简历 — rb-2026-09-14-resume-human-017

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目；在已有系统基础上持续参与 Agent、Tool/MCP、知识检索与 Context/Memory 等方向研发，项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- 重构单 Agent Tool Calling 策略，移除 MCPAgent-as-Tool 的嵌套调用，改为主 Agent 直接绑定具体 MCP Tools，并在调用期按用户配置注入对应 Server 参数，收敛工具绑定与配置链路。
- 完善 Workspace MCP 调用路由，为确定性请求保留 direct route、复杂请求回落 ReAct；修复自定义 MCP 名称递归和天气自然语言参数解析等实际调用问题，并补充对应回归用例。
- 优化 GraphRAG 检索链路，在 5 条 HotpotQA retrieval smoke 中定位 graph candidates 将 baseline 已命中文档挤出 Top-K 的排序回退；围绕候选融合、实体别名归一化和 path-aware ranking 连续修正，使样本结果恢复到 baseline 水平。
- 落地 Context / Memory V2 基础链路，统一 Context / Memory 数据结构与 scope 约束，接入 Agent 调用前读取、回合后写入和轻量 ContextOrchestrator，为后续上下文构建提供统一入口。
- 继续完善调用前 readback，将同 scope 的任务摘要与审核通过的 structured memory 注入模型上下文，并增加 policy / source trace、review / provenance 约束，避免未审核记忆直接参与生成。
- 围绕 Tool Calling、GraphRAG 与 Context / Memory 持续补充回归测试和 retrieval smoke，覆盖路由、用户配置注入、structured result、review / provenance 等关键路径，用可重复测试验证连续改动。
