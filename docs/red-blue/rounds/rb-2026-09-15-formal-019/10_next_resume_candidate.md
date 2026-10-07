# Next Resume Candidate — rb-2026-09-15-formal-019

```text
status: BUILT_PENDING_USER_RESUME_REVIEW
source_head_sha: c7971a7c
built_from: 01_simulated_resume.md（本轮 frozen resume）+ 本轮 improvement ledger 的应用结果
scope: NEXT_ROUND_ONLY
```

本轮批准的改动落地后，简历候选更新如下。**只有已发生的事实可以进入简历**；未实现的 Target、未补的 Evidence、未恢复的 Personal Ownership 不因为「讨论过」而升级。

## 本轮变更摘要

| 来源 | 变更 |
| --- | --- |
| `IMP-019-07`（deferred） | direct route 不单独占用一条 bullet，并入 Tool/MCP 的 routing 故事 |
| `IMP-019-05`（applied，measurement blocked） | GraphRAG bullet **保持** regression / baseline-preserving 表述；新增独立 holdout **未执行**，因此不允许出现任何「效果提升」措辞 |
| `IMP-019-08` / `IMP-019-09`（NEXT_ROUND_ONLY） | Red / Blue skill 变更，不改变简历内容 |

---

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，持续参与 Tool/MCP、知识检索与 Context/Memory 等核心链路研发；项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- **重构单 Agent Tool Calling 与 Workspace 路由**：针对 MCP Tool 需经子 Agent 转发、用户配置跨层传递的问题，将具体 MCP Tools 直接绑定主 Agent，并在调用时按 Tool–Server 映射注入用户级配置；同时收紧 Workspace Tool 路由——目标与参数明确的一步请求走 direct route，复杂或参数不完整任务回落 ReAct，并用回归测试固定路由边界（含自定义 MCP 名称递归与自然语言参数抽取）。
- **定位并修复 GraphRAG 排序回退**：在 HotpotQA development smoke 中发现 graph candidates 会把 baseline 已命中文档挤出 Top-K；实现 baseline-preserving fusion，保留 Vector/BM25 原始 rank，并按图证据强度分层晋升候选。
- **继续优化多跳图检索**：实现 candidate-aware seed expansion、实体别名归一化与 path-aware ranking，改善 seed 覆盖、实体匹配和路径证据利用；5-query smoke 修复后恢复到 baseline 水平。
- **构建 scoped Context / Memory V2**：统一 typed contracts 与 scope 约束，接入 Agent 调用前读取、回合后写入和轻量 ContextOrchestrator，使上下文组装由统一入口按作用域完成。
- **收紧 Memory readback**：仅将同 scope 的 task summary 与审核通过的 structured memory 注入 `prepare_context()`，增加 source trace、review / provenance 约束及 focused tests。

---

## 简历边界声明（不进入简历正文）

这些约束来自本轮 improvement ledger 与 `docs/governance/interview-acceptance-standard.md`，用于防止简历、面试回答与架构互相漂移。

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行（`docs/evidence/current-eval-baseline.md` 为 `MEASUREMENT_BLOCKED`）；已记录的只是 regression 修复与 baseline 保持。冻结协议见 `docs/governance/rb019-graphrag-ablation-protocol.md`。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 这些当前全部是 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）；总体架构与九模块文档是后续系统化整理的产物，不能倒推为加入时的历史 Ownership。

**可以写，且经得起追问：**

- Tool/MCP binding、config injection、route boundary、GraphRAG baseline-preserving fusion、seed expansion / alias / path ranking、Context/Memory V2 与 readback 收紧，都有公开提交链支撑。
- 追问到「有没有 holdout」时，正确回答是：没有，测量当前 blocked，因此只是 regression 修复。

## Gate

本文件是 `10_next_resume_candidate.md`，**尚未冻结**。下一轮开始前必须重新经过 `USER_RESUME_REVIEW`；未获批准不得作为下一轮的 frozen resume。

同时，下一轮必须从新的 exact `main` HEAD 重新固定 `zuno_base_sha`，并对本 ledger 做 base-alignment。
