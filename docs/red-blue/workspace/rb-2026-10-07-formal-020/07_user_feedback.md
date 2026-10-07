# User Feedback — rb-2026-10-07-formal-020

## Carry-forward constraints

- Automated Red/Blue uses `BATCH_DUEL`；用户不逐题扮演候选人。
- 正式 loop 是两波已提交的 100 问 / 100 答；Red Wave 2 由 Blue Wave 1 的可观察回答驱动。
- Red Final 对 Blue 架构封存件与 canonical Zuno truth 保持盲态。
- 简历保持真实的一页纸投递语域：项目背景、技术栈、4–6 条强技术故事；避免可疑的 headline 数字，避免把简历写成证据备忘录。
- 每条 bullet 应能被独立追问，并保留个人 ownership 边界。
- 当前架构是基线，不是受保护的答案。Single Agent / Multi-Agent / Supervisor-Specialist / Subgraph / Generic Host / Native Runtime 都是必须挣得自己复杂度的候选。
- 用户的一手面试记录优先于公开面试帖，用于校准 Red 行为。
- 聊天 checkpoint 保持简洁：只给当前阶段产出的 artifact，不给全部 round 文件的索引。
- Simulated Resume 可以在聊天里完整展示。
- Red / Blue 的 100 题 / 100 答批次在聊天里只展示少量高信息量样本，完整批次给一个直接的 GitHub 文档链接。

## 2026-10-07 — 本轮主指令

用户指示「你来进行一轮红蓝队对攻迭代」，并给出自主治理主指令（已固化为 [`docs/governance/interview-acceptance-standard.md`](../../../governance/interview-acceptance-standard.md)，`main@c7971a7c`，PR #278）：

- **优化「任何强 Claim 都能被追到 History / 个人 Ownership / 代码 / 失败窗口 / Evidence / Unknown」，而不是优化「看起来真实」。**
- Red 不再生成 100 个独立知识点，而是约 8–12 条 **Interview Thread**，跨题保持状态并回钩。
- 新增 Architecture Interview Acceptance 循环。
- Blue 候选人第一层 20–60 秒口语。
- Finding 严格路由：**不允许用 Architecture change 修 Candidate 的表达失败**。
- 下一轮必须从最新 `main` HEAD 固定 `zuno_base_sha` 并做 base-alignment。

## 2026-10-07 — 本轮执行中的 Gate 处理

| Gate | 状态 | 说明 |
| --- | --- | --- |
| `resume_review_gate` | `DELEGATED` | 用户在「你来进行一轮红蓝队对攻迭代」的委托下，Resume Gate 由 Controller 代行。简历内容由 019 的 `10_next_resume_candidate.md` 提升而来，**未新增任何 Target 外事实**。用户仍可要求 `RESUME_REVISION` 并重跑本波。 |
| `improvement_review_gate` | **`REQUIRED`（未过）** | 本轮 `09_improvement_ledger.md` 的 15 条提案**不自动应用**，已回到用户面前。 |

## 本轮未经用户批准、以 Controller 权限内做出的决定

均属于主指令 §13 明确允许的范围（narrative / reference / term order / failure explanation / Red-Blue workflow artifacts / Evidence freshness）：

- 以 `AGENT_AUTO` + `PHYSICAL_CONTEXT_ISOLATION` + `strict_blind_red_certification: true` 运行（019 为 `CHATGPT_AUTO`）。
- 把 100 题组织为 10 条 Interview Thread。
- Red Wave 2 的追问编号沿用 `Q101–Q200`、Blue Wave 2 的答用 `A101–A200`（避免与第一批混淆）。
- 在 4 个阶段文件里加入「本次实际打开的文件」隔离审计附录。

## 本轮明确**没有**做的事（禁区）

- 没有新增业务模块、状态机、Receipt、Provider。
- 没有改动 Authority / Security Authority / Recovery 语义 —— IMP-020-02 / 03 / 06 只是**提案**。
- 没有把任何 Target 升级为 Current。
- 没有制造 Personal Ownership（见 `IMP-020-10`：Ownership 不可考古，本轮只提出把该边界写进文档）。
- 没有制造任何 GraphRAG 收益数字。

## 待用户决定

1. `09_improvement_ledger.md` 15 条提案的批准 / 拒绝 / 延后。
2. `10_next_resume_candidate.md` 是否作为下一轮 frozen resume。
3. 是否把 `IMP-020-10`（Ownership 不可考古）写进 `docs/project/README.md` 的已知边界。
