# Current Red / Blue Round

state: `active-red-blue`
active_round: `rb-2026-09-15-formal-019`
mode: `CHATGPT_AUTO`
execution_mode: `BATCH_DUEL`
stage: `BATCH_CHECKPOINT_BLUE_1`
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
red_questions_status: `COMPLETE`
red_wave_1_status: `COMPLETE`
blue_wave_1_status: `COMPLETE`
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
last_consumed_head_sha: `847f35e1ba7bafaa8ef5316317932293d2e1d150`
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

当前：formal round #019 active；Blue Wave 1 已完成 100 答与 sealed architecture notes，停在 `BATCH_CHECKPOINT_BLUE_1`；Red Wave 2 尚未开始。
