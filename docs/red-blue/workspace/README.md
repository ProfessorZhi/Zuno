# Red / Blue Active Workspace

这里保存**正在执行的一轮** Red / Blue 面试模拟。长期历史进入 [`../rounds/`](../rounds/README.md)。

## Active Round 以 GitHub 为运行容器

正式 Round 从固定 `main` SHA 创建独立 branch：

```text
red-blue/<round-id>
```

并创建 `docs/red-blue/workspace/<round-id>/`。当前协议固定十一份 artifact：

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
09_improvement_ledger.md
10_next_resume_candidate.md
```

Draft PR 是活动 Round 的 GitHub 入口。`main` 不保存半完成 workspace。

## GitHub 是 stage 和 live turn 的交接面

```text
读取 live Round branch HEAD
→ 核对 manifest stage / allowlist
→ 当前 actor 只执行一个 stage / turn
→ 更新 artifact + manifest + transcript
→ commit
→ 下一个 actor 重新读取 HEAD
```

## Resume-first

`01_simulated_resume.md` 先由用户 review，再冻结。Red 只能读取 Frozen Resume、岗位 / JD、pinned Red Skill 和模型通用知识。

Resume bullet 优先表达真实工程问题和技术决策，不以框架名、模块名或漂亮数字代替贡献。

## Red Plan 不是现场脚本

`02_red_questions.md` 保存：

```text
6–10 条 SPOKEN_SEEDS
DYNAMIC FOLLOWUP_POLICY
BRANCH_EXAMPLES
100 问 PRESSURE_SUITE
```

Pressure Suite 只做离线覆盖。

## Live Interview 真正 Red ↔ Blue 交替

`03_blue_answers.md` 是实际 Q/A ledger：

```text
Red 问一个问题
→ commit
→ Blue 回答
→ commit
→ Red 根据刚才回答追问
→ commit
→ Blue 回答
→ ...
```

Red 不能一次把后续追问全部预生成；Blue 不能提前看到未来问题。

Blue 使用 pinned `.agent/red-blue/defense-model.md` 控制回答方式，并使用固定 `zuno_base_sha` 的 canonical sources 控制事实边界。

## Round 后半不是“写总结”，而是做归因

面试完成后依次产生：

```text
04 Red Evaluation
05 Blue Architecture Reflection
06 Resume / Red Skill / Blue Skill / Harness Retrospective
09 Improvement Ledger
```

`09_improvement_ledger.md` 必须给每个问题一个 primary owner：Resume、Red Skill、Blue Skill、Harness、Narrative、Docs、Architecture、Implementation、Evidence、Ownership、Fundamentals 或 No Change。

用户批准前不能因为一次面试信号直接修改 canonical Zuno Truth。

## NEXT_ROUND_ONLY

批准的 Skill / Harness / Docs / Architecture 变更可以在 Round branch 后半段落地，但只对下一轮生效。本轮 Frozen Resume、pinned Skill 和 Evaluation 不回头改写。

## 下一版简历

完成批准的改进后，Resume Builder 生成 `10_next_resume_candidate.md`。它只是下一轮候选稿：Round merge 后，下一轮从新 main HEAD 重新校验，并再次进入 USER_RESUME_REVIEW。

未解决的 Implementation / Evidence / Ownership gap 不能因为写进 candidate 就升级成事实。

## 两种模式

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED`；`AGENT_AUTO` 在角色真正使用独立 context 时可以声明 `PHYSICAL_CONTEXT_ISOLATION`。

## 关闭一轮

完成 Improvement Gate、应用或明确 defer 改进、构建 Next Resume Candidate 后，才把 workspace 原样移动到 `docs/red-blue/rounds/<round-id>/`。Required CI 通过后 merge。

坏问题、弱回答、用户批评、被拒绝的改进和未解决 blocker 都必须保留。