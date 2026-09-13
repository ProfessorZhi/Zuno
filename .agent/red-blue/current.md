# Current Red / Blue Round

state: `no-active`
active_round: `none`
mode: `none`
stage: `none`
workspace_path: `none`
simulated_resume: `none`
target_role: `none`
interview_stage: `none`
pressure_suite_count: `100`
seed_question_target: `8`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
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

正式 Round 在独立 GitHub branch 和 Draft PR 上执行。Active Workspace 位于：

```text
docs/red-blue/workspace/<round-id>/
```

Round 关闭前归档到 `docs/red-blue/rounds/<round-id>/`。

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
pressure_suite_count: `<positive integer; default 100>`
seed_question_target: `<6-10; default 8>`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
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

每个阶段从 GitHub live branch HEAD 重新读取允许输入，并在 transcript 记录 `input_head_sha`。

模拟简历冻结后，Red 的正式业务输入只能来自已提交的模拟简历、岗位 / JD、`.agent/red-blue/attack-model.md` 和模型通用知识。

校准 Round 默认 `red_review_gate: REQUIRED`。Red 第一轮产物由少量自然 `SPOKEN_SEEDS`、动态 Follow-up Policy、Branch Examples 和离线 Pressure Suite 组成；不再预写固定 30 问 Primary Path。用户未 `APPROVE` 前 Blue 不得开始。

Round Init 必须把启动前已经知道、且影响本轮流程或 Red 质量的用户反馈写入 `07_user_feedback.md` 和 transcript。

一轮固定保存：

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

当前：没有 active Round。
