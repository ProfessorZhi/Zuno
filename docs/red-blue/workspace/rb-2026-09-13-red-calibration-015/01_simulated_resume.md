# 模拟简历 — rb-2026-09-13-red-calibration-015

求职方向：Agent 开发工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台

2026.03－至今

**项目简介：** 南京大学 LIPLAB 智慧司法研究与工程化背景下、面向天津法院智慧平台相关场景的法律智能 Agent 项目；项目经历过内部 Demo、客户侧 / 法院侧测试与 Pilot Validation。我在已有系统基础上参与 Agent / Tool Calling、GraphRAG 检索优化、Context / Memory 以及后续架构与工程证据复盘。

**技术栈：** Python、LangGraph、RAG / GraphRAG、Tool Calling、MCP、PostgreSQL、Pytest

1. **Agent 与 Tool Calling：** 参与单 Agent Tool Calling Strategy 重构，将 MCP Server 从 MCPAgent-as-Tool 的嵌套路径收口为 `GeneralAgent` 直接绑定具体 MCP Tools，并在调用期按 tool → server 映射注入用户级 MCP 配置；后续在 Workspace 调用层保留 deterministic direct route / ReAct fallback，修复 custom MCP 名称递归和高德天气自然语言参数解析问题，并补 direct-route、config-gate、structured-result 等 regression test artifact。
2. **GraphRAG 检索质量：** 在 HotpotQA `limit=5` retrieval-only `real_runtime` smoke 中定位 local GraphRAG 的 sampled regression：graph-added documents 挤出 baseline 已命中的 gold-like documents，`Recall@5` 从 baseline `1.00` 降到 local `0.80`；随后连续实现 baseline-preserving fusion、candidate-aware seed expansion、entity alias normalization 与 path-aware ranking，同日 rerun 中 local `Recall@5=1.00`、`MRR@10=1.00`、`FullChainHit@5=1.00`，仍有 `fallback_count=1`。该结果只代表这组小样本研发 smoke，不扩写为正式 benchmark 或普遍优于 baseline。
3. **Context / Memory：** 参与 Context / Memory V2 工程链，落 typed Context / Memory contracts、scoped memory foundation、最小 `GeneralAgent.prepare_context()` / post-turn integration 与 `ContextOrchestrator`；后续在 PR #8 中为 Context Pack 增加 policy / source-id trace，将同 scope task summary 与仅 `APPROVED` 的 structured memory 接入 pre-call readback，并补 review / provenance contract，PR 记录 focused tests `32 passed`。
4. **架构与工程复盘：** 基于项目历史、代码 / 测试与后续 Target 设计，参与梳理 Generic Agent Host / 受控 RAG 的复用边界，以及材料版本、机器候选与正式工作成果、长任务恢复、权限变化和外部副作用等长期法律任务约束；GraphRAG、Memory、Multi-Agent 与原生 Runtime 均按任务与 Eval / ablation 证据决定是否保留，不默认自研或默认开启。
