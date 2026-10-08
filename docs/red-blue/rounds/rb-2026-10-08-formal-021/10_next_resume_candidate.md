# Next Resume Candidate — rb-2026-10-08-formal-021

```text
status: BUILT_PENDING_USER_RESUME_REVIEW
source_head_sha: 002ab09a（Red Final + Blue Reflection + Retrospective 落盘后）
built_from: 01_simulated_resume.md（本轮 frozen resume）+ Blue Reflection §9.2（G-01..G-08）+ IMP-021-08
scope: NEXT_ROUND_ONLY
change_effective_scope: NEXT_ROUND_ONLY
```

**只有已发生的事实可以进入简历。** 未实现的 Target、未补的 Evidence、未恢复的 Personal Ownership 不因为「讨论过」而升级。

**本文件与 `01_simulated_resume.md` 的关系：** 本轮 frozen resume **全程未改**（verdict immutable）。
`G-01` / `G-08` 指向的那处方向错误由本文件承载修正，**不回写**本轮简历。

## 本轮变更摘要（依据 Blue Reflection §9.2 + `09_improvement_ledger.md` E 组）

| ID | bullet | 处置 | 改了什么 |
| --- | --- | --- | --- |
| `G-01` + `G-08` | 第 1 条 | **改方向** | 「复杂请求进入 ReAct 路径」**与 Current 互斥** —— shipped composition 下 `dynamic_dag_planner=None`，复杂请求在**准入层 fail closed**。改为可复核措辞，删掉不存在的「回落」语义 |
| `G-04` | 第 2 条 | **收窄** | 「baseline-preserving」被读成**全局不变量**；实际是排序阶段约束，图层护栏（`fusion.py:922`）会**按设计**覆盖个别下限 |
| `G-03` | 第 3 条 | **合并** | `别名归一化 → seed expansion` 是**同一条链**，原文并列成两个独立机制 |
| `G-02` + `G-06` | 第 4 条 | **降位** | `ContextOrchestrator` 在 `src/` **无生产调用点**（只有 re-export），降为 typed contract 层；真实组装入口在 `build_context` 节点 → `build_context_pack(scope=…)` |
| `G-06` | 第 5 条 | **补边界** | focused tests 覆盖的是**过滤逻辑**，跨 scope 泄漏隔离**无负向测试** |
| `G-05` | 项目简介 | **删** | 「Pilot Validation」近零信息（Pilot 全 Unknown），删除 |

**删除 0 条 bullet。** 五条核心事实都有 commit 支撑；本轮漂的是**方向、范围与集成点**，不是事实存在性。

---

求职方向：Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师

## 项目经历

### Zuno：法律智能 Agent 平台　2026.03－至今

**项目简介：** 面向天津法院智慧平台相关场景的法律智能 Agent 项目，持续参与 Tool/MCP、知识检索与 Context/Memory 等核心链路研发；项目经历内部 Demo 与法院侧测试。

**技术栈：** Python / LangGraph / MCP / RAG / GraphRAG / PostgreSQL / Pytest

- **重构单 Agent Tool Calling 与 Workspace 路由**：针对 MCP Tool 需经子 Agent 转发、用户配置跨层传递的问题，将具体 MCP Tools 直接绑定主 Agent，并在调用时按 Tool–Server 映射注入用户级配置；同时收紧 Workspace Tool 准入——目标与参数明确的一步请求走 direct route，复杂请求需要绑定动态规划器，而该产品组合下规划器未绑定，这类请求在**准入处 fail closed**、不进入 ReAct 路径。回归测试固定的是 direct route 一侧的准入与工具参数抽取边界（含自定义 MCP 名称递归）。
- **定位并修复 GraphRAG 排序回退**：在 HotpotQA `limit=5` retrieval-only `real_runtime` smoke 中发现 graph candidates 会把 baseline 已命中的文档挤出 Top-K（`Ed Wood`、`Shirley Temple` 被挤出 top5）；实现**排序阶段**的 baseline-preserving 约束——保留 Vector/BM25 原始 rank，并按图证据强度分层晋升候选。该约束作用在排序阶段、不是全局不变量，图证据护栏会按设计覆盖个别下限。同日 rerun 在该 5-query 样本上不再低于 baseline。
- **继续完善多跳图检索**：实现**一条耦合链**——实体别名归一化 → candidate-aware seed expansion——并补 path-aware ranking 使用路径证据；这条链与 path ranking 各有单元测试，但质量收益目前只在 5-query smoke 上观察到 —— 独立 holdout 与 leave-one-out ablation 尚未执行。
- **构建 scoped Context / Memory V2**：以 typed contracts（ContextOrchestrator）统一 scope 约束，按作用域经 `build_context` 生产路径完成上下文组装，并接入 Agent 调用前读取与回合后写入。
- **收紧 Memory readback**：仅将同 scope 的 task summary 与审核通过的 structured memory 注入调用前读取路径，增加 source trace 与 review / provenance 约束；focused tests 覆盖的是过滤逻辑本身，跨 scope 泄漏隔离尚无负向测试。

---

## 简历边界声明（不进入简历正文）

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行
  （冻结协议 `docs/governance/rb019-graphrag-ablation-protocol.md`，状态 `BLOCKED_PENDING_DATA`）。
  注意：`docs/evidence/current-eval-baseline.md` 的 `MEASUREMENT_BLOCKED` 是**整个 eval 层**的状态，
  不要收窄成 GraphRAG 专属结论。
- **不写任何 run-to-run 百分比。** `docs/governance/project-fact-provenance.md:96` 明确记录 baseline 的 `MRR@10`
  在同日 rerun 中也从 `0.90` 变为 `1.00`，因此「修复前后」框架在本样本上不成立。正确说法是 local 与 baseline **打平**。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 全部 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）。

**必须承认的取证缺口（`IMP-020-10`）：**

本仓库的人类身份只有 `ProfessorZhi` / `WenHi Huang`(=vince) 及自动化 —— **commit 作者字段区分不出「我」与「团队」**。
因此任何「这是我的第一笔改动」的表述都是叙事而非证据。本简历只使用**能指到 commit / 测试 / 文档**的说法。

**本轮新增的边界（来自 `G-02` / `G-06`）：**

- `ContextOrchestrator.prepare` 在 `src/` **无生产调用点**，简历已把它降为 typed contract 层，
  不再暗示它是运行时装配器。
- 「命名组件 ≠ 在跑的组件」（`N-01`）：`DeleteRestoreRuntime`、phase08 `PostgresSaver` 桥、
  `escalate` / `record_manual` 等组件在 `src/` 无生产调用方，**不进简历**。

## 待下一轮 Resume Gate 复核的两件事

1. **第 1 条的方向修正**（`G-01` / `G-08`）—— 本文件已按「复杂请求需要绑定动态规划器，未绑定时在准入处 fail closed」改写，
   但该措辞**必须由下一轮 Resume Gate 连同装配侧核验一起确认**（`IMP-021-11`：核验清单新增「装配侧确认」）。
2. **`IMP-021-01` 的 decision record 落点** —— 下一轮一旦把「planner 未绑定时的复杂请求」正式定义为受控拒绝，
   第 1 条的措辞可能需要再对齐一次。

## Gate

本文件是 `10_next_resume_candidate.md`，**尚未冻结**，也未经过下一轮的 `USER_RESUME_REVIEW`。

本轮 `01_simulated_resume.md` 全程冻结未改；本轮所有措辞修正**只进入本文件**。

下一轮必须从新的 exact `main` HEAD 重新固定 `zuno_base_sha`，并对本轮 improvement ledger 做 base-alignment
（注意 `IMP-020-11`..`IMP-020-15` 与 `IMP-021-11`..`IMP-021-19` 有重叠，需去重）。
