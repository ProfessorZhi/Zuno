# User Feedback — rb-2026-10-08-formal-021

```text
recorded_at: 2026-10-08
gate: USER_IMPROVEMENT_REVIEW
gate_result: PASSED
decisions_count: 4
applied_this_round: IMP-021-11..IMP-021-19（写入 .agent/red-blue/）
change_effective_scope_for_findings: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
```

## Carry-forward constraints（沿用 020，未改）

- Automated Red/Blue 使用 `BATCH_DUEL`；用户**不**逐题扮演候选人。
- 正式 loop 是两波已提交的 100 问 / 100 答；Red Wave 2 由 Blue Wave 1 的可观察回答驱动。
- Red Final 对 Blue 架构封存件与 canonical Zuno truth 保持盲态。
- 简历保持真实的一页纸投递语域：项目背景、技术栈、4–6 条强技术故事；避免可疑的 headline 数字，避免把简历写成证据备忘录。
- 每条 bullet 应能被独立追问，并保留个人 ownership 边界。
- 当前架构是基线，不是受保护的答案。Single Agent / Multi-Agent / Supervisor-Specialist / Subgraph / Generic Host / Native Runtime 都必须挣得自己的复杂度。
- 用户的一手面试记录优先于公开面试帖，用于校准 Red 行为。
- 聊天 checkpoint 保持简洁：只给当前阶段产出的 artifact，不给全部 round 文件的索引。
- Red / Blue 的 100 题 / 100 答批次在聊天里只展示少量高信息量样本，完整批次给一个直接的 GitHub 文档链接。

## 2026-10-08 — 本轮主指令与 Gate 处理

用户在上一轮（020）收口后指示「再来一轮」，并在 Resume Gate 上选择「照 020 一样委托给 Controller」。本轮因此以 `AGENT_AUTO` +
`PHYSICAL_CONTEXT_ISOLATION` + `strict_blind_red_certification: true` 运行，Resume Gate 为 `DELEGATED`。

| Gate | 状态 | 说明 |
| --- | --- | --- |
| `resume_review_gate` | `DELEGATED` | 用户委托 Controller 代行；简历由 020 的 `10_next_resume_candidate.md` 逐字提升。用户仍可要求 `RESUME_REVISION` 并重跑本波。 |
| `improvement_review_gate` | **`REQUIRED` → `PASSED`（本次）** | 20 条提案中，4 组决定见下。 |

## 2026-10-08 — 用户对 improvement ledger 的决定（`USER_IMPROVEMENT_REVIEW`）

用户对四个问题全部选择推荐方案。逐条记录如下，**措辞为用户看到的选项文本**。

| # | 问题 | 用户选择 | 生效范围 |
| --- | --- | --- | --- |
| 1 | `IMP-021-01`（本轮唯一 `ARCHITECTURE_GAP`）是否批准下一轮落地 | **批准，最小方案** —— 下一轮写 owner + 一份最小 decision record，把「planner 未绑定时的复杂请求」正式定义为受控拒绝。**不新增模块或状态机。** | `NEXT_ROUND_ONLY` |
| 2 | `IMP-021-08` 简历五条的措辞处置（`G-01`..`G-06`、`G-08`） | **按 ledger 全表落地** —— 六条一起改，重点是把第 1 条改成「复杂请求需要绑定动态规划器，未绑定时在准入处 fail closed」这类可复核措辞。 | `NEXT_ROUND_ONLY` |
| 3 | `IMP-021-11`..`IMP-021-19` 共 9 条 Skill / Harness 提案是否授权修改 `.agent/red-blue/` | **全部授权** —— 9 条一起改，下一轮生效（含 3 条 Red/Blue Skill 语义修改）。 | 本次写入 `.agent/red-blue/`；下一轮生效 |
| 4 | 本轮收口方式 | **归档 + 等 CI 绿后 merge** —— 按 019/020 同一方式：归档 workspace、复位 `current.md`、推送，确认 CI 转绿后 merge PR #282。 | `THIS_ROUND`（流程） |

### 决定 1 的展开（架构缺口，下一轮才动）

`IMP-021-01` 的分级**不因批准而改变**：它仍是本轮唯一确认的 `ARCHITECTURE_GAP`，只是从
`NEXT_ROUND_ONLY / proposed` 变为 `NEXT_ROUND_ONLY / approved`。**本轮不写 `docs/architecture/`，不新增 ADR 文件。**

下一轮的最小交付是：

- 给 Workspace 准入边界一个 **owner**；
- 一份**最小 decision record**，把「planner 未绑定时的复杂请求」定义为**受控拒绝**；
- 补一条确定性断言：`complex` + `planner=None` ⇒ `_blocked_request` 产出 `plan_steps=()`（A102 说可写、本轮未写）；
- 判定空 plan run 的下游呈现语义（今天为 Unknown）。

**明确不做**：不新增业务模块、状态机、Receipt、Provider；不改 Authority / Security Authority / Recovery 语义。

### 决定 2 的展开（简历措辞，下一轮 Resume Gate 一起改）

`G-01`..`G-06`、`G-08` 六条全部落地。其中 `G-01` / `G-08` 是**同一处**：
`01_simulated_resume.md` 第 1 条现写「复杂请求进入 ReAct 路径」，方向错了 —— 实际是**准入 fail closed**，
而这句是 **Controller 自己在 Resume Gate 上改错的**（`00_artifact_links.md` 有完整记录）。

**处置纪律**：本轮 frozen resume **不回写**（verdict immutable）；改法只落在 `10_next_resume_candidate.md`，
并由下一轮 Resume Gate 连同核验一起确认。

### 决定 3 的展开（Skill / Harness，本次即写入）

9 条提案本次写入 `.agent/red-blue/`，**下一轮生效**。范围严格限定在 Red/Blue 工作流产物与 Harness 机制，
**不触碰** Zuno 产品代码、架构或 Authority。

**必须记住的时序边界**：本轮 400 条记录是用**旧 Skill** 跑出来的。本轮 verdict、findings 与 ledger **不因 Skill 修改而重算**
（`current_round_verdict_recomputed: false`）。下一轮才用新 Skill 跑 —— 这是一次**跨轮生效**，不是对本轮的事后修补。

## 本轮明确**没有**做的事（禁区）

- 没有新增业务模块、状态机、Receipt、Provider。
- 没有改动 Authority / Security Authority / Recovery 语义 —— `IMP-021-01`..`IMP-021-07`、`IMP-021-20` 均只是**提案或下一轮动作**。
- 没有把任何 Target 升级为 Current。
- 没有制造 Personal Ownership。
- 没有制造任何 GraphRAG 或检索收益数字。
- 没有用 Architecture change 去修任何 Candidate 的表达失败（Finding 路由纪律）。

## 待用户决定（留给下一轮之前）

1. `10_next_resume_candidate.md` 是否作为下一轮 frozen resume（下一轮 Resume Gate）。
2. `IMP-021-01` 的 decision record 具体落点（`docs/architecture/` 还是 `docs/decisions/`）在下一轮开工时确认。
3. 010/020 结转的 10 条（`IMP-020-04`..`08`、`11`..`15`）与本轮 `IMP-021-11`..`19` 有重叠，下一轮需按 base-alignment 去重。
