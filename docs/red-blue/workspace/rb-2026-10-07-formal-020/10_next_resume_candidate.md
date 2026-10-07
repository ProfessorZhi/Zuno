# Next Resume Candidate — rb-2026-10-07-formal-020

```text
status: BUILT_PENDING_USER_RESUME_REVIEW
source_head_sha: 0c9e2d82（Red Final + Blue Reflection 落盘后）
built_from: 01_simulated_resume.md（本轮 frozen resume）+ Red Final §4 处置 + IMP-020-09
scope: NEXT_ROUND_ONLY
```

**只有已发生的事实可以进入简历。** 未实现的 Target、未补的 Evidence、未恢复的 Personal Ownership 不因为「讨论过」而升级。

## 本轮变更摘要（依据 Red Final §4）

| # | bullet | 处置 | 改了什么 |
| --- | --- | --- | --- |
| 1 | Tool Calling 与 Workspace 路由 | **降级改写** | 删掉「固定路由边界」的越界动词 —— 实际只固定了 direct-route 一侧（A200 当场改写的那句） |
| 2 | GraphRAG 排序回退 | **保留**（附两条硬上限） | 五条里唯一有回归测试固定住的；上限：不得声称「效果提升」，不得制造 run-to-run 百分比 |
| 3 | 多跳图检索优化 | **降级改写** | 证据只有 5-query smoke；「改善」类动词收回，改为陈述补了什么、在哪测的 |
| 4 | Context / Memory V2 | **降级改写** | `prepare_context()` 今日已不是函数（A24）；第 4 条所在文件**已被删除**，属历史而非 Current（A60） |
| 5 | Memory readback 收紧 | **降级改写** | 与第 4 条同源；动词与机制对应收紧 |

**删除 0 条。** 五条核心事实都有 commit 支撑；漂的是动词强度，不是事实。

---

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，持续参与 Tool/MCP、知识检索与 Context/Memory 等核心链路研发；项目经历内部 Demo、法院侧测试与 Pilot Validation。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- **重构单 Agent Tool Calling 与 Workspace 路由**：针对 MCP Tool 需经子 Agent 转发、用户配置跨层传递的问题，将具体 MCP Tools 直接绑定主 Agent，并在调用时按 Tool–Server 映射注入用户级配置；同时收紧 Workspace Tool 准入——目标与参数明确的一步请求走 direct route，复杂或参数不完整任务回落 ReAct，并用回归测试固定 direct route 一侧的准入与工具参数抽取边界（含自定义 MCP 名称递归），ReAct 回落侧暂无回归断言。
- **定位并修复 GraphRAG 排序回退**：在 HotpotQA `limit=5` retrieval-only `real_runtime` smoke 中发现 graph candidates 会把 baseline 已命中的文档挤出 Top-K（`Ed Wood`、`Shirley Temple` 被挤出 top5）；实现 baseline-preserving fusion，保留 Vector/BM25 原始 rank，并按图证据强度分层晋升候选；同日 rerun 在该 5-query 样本上不再低于 baseline。
- **继续完善多跳图检索**：实现 candidate-aware seed expansion、实体别名归一化与 path-aware ranking，补齐 seed 覆盖、实体匹配与路径证据利用；上述改动在 5-query smoke 上验证。
- **构建 scoped Context / Memory V2**：统一 typed contracts 与 scope 约束，接入 Agent 调用前读取、回合后写入和一个轻量 ContextOrchestrator，使上下文组装由统一入口按作用域完成。
- **收紧 Memory readback**：仅将同 scope 的 task summary 与审核通过的 structured memory 注入调用前读取路径，增加 source trace 与 review / provenance 约束及 focused tests。

---

## 简历边界声明（不进入简历正文）

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行（`docs/evidence/current-eval-baseline.md` 为 `MEASUREMENT_BLOCKED`）。冻结协议见 `docs/governance/rb019-graphrag-ablation-protocol.md`。
- **不写任何 run-to-run 百分比。** `project-fact-provenance.md:96` 明确写着 baseline 的 `MRR@10` 在同日 rerun 中也从 `0.90` 变为 `1.00`，因此「修复前后」这种框架在本样本上不成立。正确说法是 local 与 baseline **打平**，不是超过。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 这些当前全部是 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）。

**必须承认的取证缺口（`IMP-020-10`）：**

本仓库 2161 个 commit 中，人类身份只有 `ProfessorZhi` / `WenHi Huang`(=vince) 及自动化 —— **commit 作者字段区分不出「我」与「团队」**。因此任何「这是我的第一笔改动」的表述都是叙事而非证据。本简历只使用**能指到 commit / 测试 / 文档**的说法，不使用无法取证的归属主张。

## Gate

本文件是 `10_next_resume_candidate.md`，**尚未冻结**，也未经过本轮之后的 `USER_RESUME_REVIEW`。

注意：本轮 `01_simulated_resume.md` 全程冻结未改；候选人在 A200 当场改写的第 1 条措辞**只进入本文件**，不回写本轮 frozen resume。

下一轮必须从新的 exact `main` HEAD 重新固定 `zuno_base_sha`，并对本轮 improvement ledger 做 base-alignment。
