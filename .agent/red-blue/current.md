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
resume_review_gate: `none`
red_review_gate: `none`
improvement_review_gate: `none`
red_questions_status: `none`
live_interview_status: `none`
next_actor: `none`
improvement_ledger_status: `none`
next_resume_candidate_status: `none`
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

## 允许的 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `CHATGPT_AUTO | AGENT_AUTO`
stage: `BUILD_RESUME | USER_RESUME_REVIEW | RESUME_REVISION | RED_QUESTIONS | USER_RED_REVIEW | RED_REVISION | LIVE_INTERVIEW | RED_TURN | BLUE_TURN | RED_EVALUATION | BLUE_REFLECTION | WORKFLOW_RETROSPECTIVE | IMPROVEMENT_SYNTHESIS | USER_IMPROVEMENT_REVIEW | IMPROVEMENT_REVISION | APPLY_IMPROVEMENTS | BUILD_NEXT_RESUME | USER_FEEDBACK | CLOSE`
workspace_path: `docs/red-blue/workspace/<round-id>/`
simulated_resume: `docs/red-blue/workspace/<round-id>/01_simulated_resume.md`
target_role: `<role>`
interview_stage: `<stage>`
pressure_suite_count: `<positive integer; default 100>`
seed_question_target: `<6-10; default 8>`
live_followups: `DYNAMIC`
one_question_one_intent: `true`
resume_review_gate: `REQUIRED | OPTIONAL | SKIP`
red_review_gate: `REQUIRED | OPTIONAL | SKIP`
improvement_review_gate: `REQUIRED | OPTIONAL | SKIP`
red_questions_status: `NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN | INVALIDATED_BY_RESUME_CHANGE`
live_interview_status: `NOT_STARTED | RUNNING | COMPLETE | ABORTED`
next_actor: `RED | BLUE | NONE`
improvement_ledger_status: `NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED`
next_resume_candidate_status: `NOT_STARTED | BUILT | BLOCKED`
round_branch: `red-blue/<round-id>`
round_pr: `<GitHub PR number>`
last_consumed_head_sha: `<HEAD actually read by the last completed stage/turn>`
github_state_bus: `required`
stage_handoff: `commit-then-reread`
firewall_strength: `LOGICAL_GITHUB_MEDIATED | PHYSICAL_CONTEXT_ISOLATION`
strict_blind_red_certification: `false | true`
transcript_policy: `full-observable-role-io`
archive_live: `true`
```

## Live interview invariant

```text
RED_TURN commit
→ BLUE_TURN commit
→ RED_TURN commit
→ BLUE_TURN commit
```

Red 不能在 Blue answer 尚未提交时预生成正式 follow-up；Blue 不能看到未来问题。

## Round-end invariant

```text
Red Evaluation
→ Blue Reflection
→ Resume / Red Skill / Blue Skill / Harness Retrospective
→ Improvement Ledger
→ User Improvement Gate
→ NEXT_ROUND_ONLY changes
→ Next Resume Candidate
```

轮末修改 Skill / Docs / Architecture 不回头重算本轮 verdict。

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
09_improvement_ledger.md
10_next_resume_candidate.md
```

当前：没有 active Round。
