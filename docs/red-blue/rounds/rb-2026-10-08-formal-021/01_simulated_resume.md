# Simulated Resume — rb-2026-10-08-formal-021

```text
status: FROZEN
frozen_against_main: cdd2063b341e6919fafaa1395d1f3bdc837329f6
promoted_from: docs/red-blue/rounds/rb-2026-10-07-formal-020/10_next_resume_candidate.md
user_resume_review_status: DELEGATED
```

---

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，持续参与 Tool/MCP、知识检索与 Context/Memory 等核心链路研发；项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- **重构单 Agent Tool Calling 与 Workspace 路由**：针对 MCP Tool 需经子 Agent 转发、用户配置跨层传递的问题，将具体 MCP Tools 直接绑定主 Agent，并在调用时按 Tool–Server 映射注入用户级配置；同时收紧 Workspace Tool 准入——目标与参数明确的一步请求走 direct route，复杂请求进入 ReAct 路径，并用回归测试固定 direct route 一侧的准入与工具参数抽取边界（含自定义 MCP 名称递归），ReAct 一侧暂无回归断言。
- **定位并修复 GraphRAG 排序回退**：在 HotpotQA `limit=5` retrieval-only `real_runtime` smoke 中发现 graph candidates 会把 baseline 已命中的文档挤出 Top-K（`Ed Wood`、`Shirley Temple` 被挤出 top5）；实现 baseline-preserving fusion，保留 Vector/BM25 原始 rank，并按图证据强度分层晋升候选；同日 rerun 在该 5-query 样本上不再低于 baseline。
- **继续完善多跳图检索**：实现 candidate-aware seed expansion、实体别名归一化与 path-aware ranking，补齐 seed 覆盖、实体匹配与路径证据利用；每个机制有单元测试，但质量收益目前只在 5-query smoke 上观察到 —— 独立 holdout 与 leave-one-out ablation 尚未执行。
- **构建 scoped Context / Memory V2**：统一 typed contracts 与 scope 约束（ContextOrchestrator），接入 Agent 调用前读取与回合后写入，使上下文组装按作用域在统一入口完成。
- **收紧 Memory readback**：仅将同 scope 的 task summary 与审核通过的 structured memory 注入调用前读取路径，增加 source trace 与 review / provenance 约束及 focused tests。
