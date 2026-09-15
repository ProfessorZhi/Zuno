# Current Red / Blue Round

state: `active-red-blue`
active_round: `rb-2026-09-15-formal-019`
mode: `CHATGPT_AUTO`
execution_mode: `BATCH_DUEL`
stage: `USER_RESUME_REVIEW`
workspace_path: `docs/red-blue/workspace/rb-2026-09-15-formal-019/`
simulated_resume: `docs/red-blue/workspace/rb-2026-09-15-formal-019/01_simulated_resume.md`
target_role: `Agent 开发工程师 / 大模型应用工程师 / AI 应用工程师`
interview_stage: `技术一面 / 项目深挖`
pressure_suite_count: `100`
seed_question_target: `8`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
red_wave_1_question_target: `100`
blue_wave_1_answer_target: `100`
red_wave_2_question_target: `100`
blue_wave_2_answer_target: `100`
batch_checkpoint_policy: `LINK_ONLY_PAUSE`
resume_review_gate: `REQUIRED`
red_review_gate: `optional-compatibility`
improvement_review_gate: `REQUIRED`
red_questions_status: `NOT_STARTED`
red_wave_1_status: `NOT_STARTED`
blue_wave_1_status: `NOT_STARTED`
red_wave_2_status: `NOT_STARTED`
blue_wave_2_status: `NOT_STARTED`
live_interview_status: `NOT_STARTED`
live_turn_index: `0`
next_actor: `NONE`
red_evaluation_status: `NOT_STARTED`
blue_reflection_status: `NOT_STARTED`
workflow_retrospective_status: `NOT_STARTED`
improvement_ledger_status: `NOT_STARTED`
round_report_status: `NOT_STARTED`
next_resume_candidate_status: `NOT_STARTED`
round_branch: `red-blue/rb-2026-09-15-formal-019`
round_pr: `239`
last_consumed_head_sha: `a8b0e540d9c138071ba671733e88a4142bd77a60`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED`
strict_blind_red_certification: `false`
transcript_policy: `full-observable-role-io`
archive_live: `true`

正式 Round 在独立 GitHub branch 和 Draft PR 上执行：

```text
docs/red-blue/workspace/<round-id>/
```

## 默认 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `CHATGPT_AUTO | AGENT_AUTO`
execution_mode: `BATCH_DUEL | LIVE_INTERVIEW`
stage: `BUILD_SIMULATED_RESUME | USER_RESUME_REVIEW | RESUME_REVISION | RED_WAVE_1 | BATCH_CHECKPOINT_RED_1 | BLUE_WAVE_1 | BATCH_CHECKPOINT_BLUE_1 | RED_WAVE_2 | BATCH_CHECKPOINT_RED_2 | BLUE_WAVE_2 | BATCH_CHECKPOINT_BLUE_2 | RED_EVALUATION | BLUE_ARCHITECTURE_REFLECTION | WORKFLOW_RETROSPECTIVE | IMPROVEMENT_SYNTHESIS | ROUND_REPORT | USER_IMPROVEMENT_REVIEW | IMPROVEMENT_REVISION | APPLY_IMPROVEMENTS | BUILD_NEXT_RESUME_CANDIDATE | USER_FEEDBACK | CLOSE | LIVE_INTERVIEW | RED_TURN | BLUE_TURN`
workspace_path: `docs/red-blue/workspace/<round-id>/`
simulated_resume: `docs/red-blue/workspace/<round-id>/01_simulated_resume.md`
target_role: `<role>`
interview_stage: `<stage>`
pressure_suite_count: `100`
seed_question_target: `8`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
red_wave_1_question_target: `100`
blue_wave_1_answer_target: `100`
red_wave_2_question_target: `100`
blue_wave_2_answer_target: `100`
batch_checkpoint_policy: `LINK_ONLY_PAUSE`
resume_review_gate: `REQUIRED | OPTIONAL | SKIP`
red_review_gate: `OPTIONAL | SKIP`
improvement_review_gate: `REQUIRED | OPTIONAL | SKIP`
red_questions_status: `NOT_STARTED | COMPLETE | INVALIDATED_BY_RESUME_CHANGE`
red_wave_1_status: `NOT_STARTED | RUNNING | COMPLETE`
blue_wave_1_status: `NOT_STARTED | RUNNING | COMPLETE`
red_wave_2_status: `NOT_STARTED | RUNNING | COMPLETE`
blue_wave_2_status: `NOT_STARTED | RUNNING | COMPLETE`
live_interview_status: `NOT_STARTED | RUNNING | COMPLETE | ABORTED`
next_actor: `RED | BLUE | NONE`
improvement_ledger_status: `NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED`
next_resume_candidate_status: `NOT_STARTED | BUILT | BLOCKED`
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

## BATCH_DUEL invariant

```text
Frozen Resume
→ Red Wave 1: exactly 100 questions
→ Blue Wave 1: exactly 100 answers + sealed architecture notes
→ Red Wave 2: blind Blue-1 evaluation + exactly 100 targeted follow-ups
→ Blue Wave 2: exactly 100 answers + sealed architecture notes
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Controller Workflow Retrospective
→ Improvement Ledger + Round Report
→ User Improvement Gate
→ NEXT_ROUND_ONLY changes
→ Next Resume Candidate
```

Red Wave 2 和 Red Final 不能读取 Blue architecture notes。Blue Wave 2 的 Candidate answers 也不能把 Wave 1 architecture notes 当 coaching。

每个 Batch Checkpoint 默认只向用户发送对应 GitHub 文档链接，不要求用户逐题回答。

## Live interview invariant

`LIVE_INTERVIEW` 仍保留为可选模式：

```text
RED_TURN commit
→ BLUE_TURN commit
→ RED_TURN commit
→ BLUE_TURN commit
```

Red 不能在 Blue answer 尚未提交时预生成正式 follow-up；Blue 不能看到未来问题。

## Core artifacts

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

BATCH_DUEL additional artifacts:

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

当前：formal round #019 active；等待 USER_RESUME_REVIEW，Red Wave 1 尚未开始。
