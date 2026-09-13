# Current Red / Blue Round

state: `no-active`
active_round: `none`
mode: `none`
stage: `none`
workspace_path: `none`
simulated_resume: `none`
target_role: `none`
interview_stage: `none`
question_count: `100`
primary_path_target: `30`
reserve_target: `70`
red_review_gate: `none`
red_questions_status: `none`
round_branch: `none`
round_pr: `none`
last_consumed_head_sha: `none`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `none`
strict_blind_red_certification: `false`
transcript_policy: `full-observable-role-io`
archive_live: `true`

正式 Round 在独立 GitHub branch 和 Draft PR 上执行。Round branch 中的 Active Workspace 位于：

```text
docs/red-blue/workspace/<round-id>/
```

Round 关闭前归档到：

```text
docs/red-blue/rounds/<round-id>/
```

## 允许的 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `CHATGPT_AUTO | AGENT_AUTO`
stage: `BUILD_RESUME | RED_QUESTIONS | USER_RED_REVIEW | RED_REVISION | BLUE_ANSWERS | RED_EVALUATION | BLUE_REFLECTION | WORKFLOW_RETROSPECTIVE | USER_FEEDBACK | CLOSE`
workspace_path: `docs/red-blue/workspace/<round-id>/`
simulated_resume: `docs/red-blue/workspace/<round-id>/01_simulated_resume.md`
target_role: `<role>`
interview_stage: `<stage>`
question_count: `<positive integer; default 100>`
primary_path_target: `<25-40; default 30>`
reserve_target: `<question_count-primary_path_target>`
red_review_gate: `REQUIRED | OPTIONAL | SKIP`
red_questions_status: `NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN`
round_branch: `red-blue/<round-id>`
round_pr: `<GitHub PR number>`
last_consumed_head_sha: `<HEAD actually read by the last completed stage>`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED | PHYSICAL_CONTEXT_ISOLATION`
strict_blind_red_certification: `false | true`
transcript_policy: `full-observable-role-io`
archive_live: `true`
```

模式映射：

```text
CHATGPT_AUTO -> LOGICAL_GITHUB_MEDIATED -> strict_blind_red_certification: false
AGENT_AUTO   -> PHYSICAL_CONTEXT_ISOLATION -> strict_blind_red_certification: true
```

每个阶段开始前都必须从 GitHub live branch HEAD 重新读取 manifest 和本阶段允许输入，并在 transcript 记录 `input_head_sha`。`last_consumed_head_sha` 只表示最近完成阶段实际消费的输入 HEAD，不代表当前 branch HEAD。

模拟简历冻结后，Red 的正式业务输入只能来自已提交的模拟简历、岗位 / JD、`.agent/red-blue/attack-model.md` 和模型通用知识。

校准 Round 默认 `red_review_gate: REQUIRED`。Red 第一轮产出提交后进入 `USER_RED_REVIEW`；用户未 `APPROVE` 前 `red_questions_status` 不能变成 `FROZEN`，Blue 不得开始。用户请求修订时，反馈先提交，Red Revision 更新同一 `02_red_questions.md`，Git 历史保留前一版。

Round Init 必须把启动前已经知道、且影响本轮流程或 Red 质量的用户反馈写入 `07_user_feedback.md` 和 transcript，不能等到 retrospective 再补。

无论哪种模式，一轮固定保存：

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
```

当前：没有 active Round。Round #014 已按 GitHub-mediated protocol 归档；后续校准 Round 使用 Primary Path + Reserve + USER_RED_REVIEW。
