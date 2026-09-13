# 模拟简历 — rb-2026-09-13-resume-first-014

求职方向：Agent 开发工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台

2026.03－至今

**项目简介：** 南京大学 LIPLAB 智慧司法研究与工程化背景下、面向天津法院智慧平台相关场景的法律智能 Agent 项目，曾经历内部 Demo、客户侧 / 法院侧测试与 Pilot Validation；在已有系统基础上参与 Agent / Tool Calling、Context / Memory、GraphRAG 检索质量优化，并持续参与后续架构与工程证据复盘。

**技术栈：** Python、LangGraph、RAG / GraphRAG、Tool Calling、MCP、PostgreSQL、Pytest

1. **Agent 与 Tool Calling：** 在单 Agent 调用链中，将 MCP Server 从 MCPAgent-as-Tool 的嵌套路径收口为 `GeneralAgent` 直接绑定具体 MCP Tools，并在调用期按 tool → server 映射注入用户级 MCP 配置；在 Workspace 调用层保留 deterministic direct route / ReAct fallback，修复 custom MCP 名称递归和高德天气自然语言参数解析，并补 direct-route、config gate、structured-result 等 regression test artifact。
2. **GraphRAG 检索质量：** 在 HotpotQA `limit=5` retrieval smoke 中定位 local GraphRAG 的 sampled regression：graph-added documents 挤出 baseline 已命中的 gold-like documents，`Recall@5` 从 baseline `1.00` 降到 local `0.80`；随后实现 baseline-preserving fusion、candidate-aware seed expansion、entity alias normalization 与 path-aware ranking，同日 rerun 恢复到 `Recall@5=1.00`、`MRR@10=1.00`、`FullChainHit@5=1.00`。该结果只代表这组小样本研发 smoke，不扩写为正式 benchmark。
3. **Context / Memory：** 参与 Context / Memory V2 工程链，落 typed Context / Memory contracts、scoped memory foundation、最小 `GeneralAgent.prepare_context()` / post-turn integration 与 `ContextOrchestrator`；后续在 PR #8 中为 Context Pack 增加 policy / source-id trace，将同 scope task summary 与仅 `APPROVED` 的 structured memory 接入 pre-call readback，并补 review / provenance contract，PR 记录 focused tests `32 passed`。
4. **架构与工程复盘：** 基于项目历史、代码 / 测试与后续架构设计，参与梳理通用 Agent Host / 受控 RAG 的复用边界，以及材料版本、机器候选与正式工作成果、长任务恢复、权限变化和外部副作用等长期法律任务约束；复杂的 GraphRAG、Memory、Multi-Agent 与原生 Runtime 只有在任务与评测证据支持时才保留，而不是默认自研或默认开启。
