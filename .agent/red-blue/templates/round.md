# Red / Blue Round Manifest

> 每一轮复制本模板到 Round branch 的 `docs/red-blue/workspace/<round-id>/00_manifest.yaml`。Round 关闭前整个文件夹归档到 `docs/red-blue/rounds/<round-id>/`。

## Identity

```text
round_id:
created_at:
mode: CHATGPT_AUTO | AGENT_AUTO
execution_mode: BATCH_DUEL | LIVE_INTERVIEW
zuno_base_sha:
state: ACTIVE | CLOSED | SUPERSEDED
```

自动校准 Round 默认 `execution_mode: BATCH_DUEL`。只有用户明确要求逐题真人模拟时才使用 `LIVE_INTERVIEW`。

## GitHub Runtime

```text
github_state_bus: REQUIRED
stage_handoff: COMMIT_THEN_REREAD
round_branch: red-blue/<round-id>
round_pr:
last_consumed_head_sha:
firewall_strength: LOGICAL_GITHUB_MEDIATED | PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: false | true
```

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
time_budget_minutes:
minimum_live_threads:
resume_review_gate: REQUIRED | OPTIONAL | SKIP
red_review_gate: REQUIRED | OPTIONAL | SKIP
improvement_review_gate: REQUIRED | OPTIONAL | SKIP
pressure_suite_count: 100
seed_question_target: 8
batch_wave1_question_target: 20-40
batch_wave2_question_target: 10-30
live_followups: DYNAMIC
one_question_one_intent: true
```

校准 Round 默认三个 gate 都是 `REQUIRED`。

## Pinned Skills

```text
attack_skill_version: <sha>:.agent/red-blue/attack-model.md
defense_skill_version: <sha>:.agent/red-blue/defense-model.md
judge_version: <sha>:.agent/red-blue/judge.md
protocol_version: <sha>:.agent/red-blue/protocol.md
```

Skill 在 Round Init 固定。轮末可以修改，但只对下一轮生效。

## Simulated Resume

```text
resume_style_reference:
resume_build_sources:
  - docs/project/
  - docs/architecture/
  - docs/modules/
  - docs/evidence/
  - selected docs/governance/ provenance
previous_round_resume_candidate:
simulated_resume_path: docs/red-blue/workspace/<round-id>/01_simulated_resume.md
resume_status: DRAFT | REVISION_REQUESTED | FROZEN
resume_project_bullet_count:
resume_style_check: PENDING | APPROVED | REVISION_REQUESTED | NOT_REQUIRED
user_resume_review_status: PENDING | APPROVED | REVISION_REQUESTED | ABORTED | NOT_REQUIRED
```

Resume Builder 优先写真实工程问题、个人动作、技术决策和可信结果；默认约 4–6 条，不为凑条数保留功能清单。

## Red Plan

只有 Resume `FROZEN` 才允许 Red 创建 Plan。

```text
red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN | INVALIDATED_BY_RESUME_CHANGE
seed_question_count:
pressure_suite_count: 100
branch_examples_present: false | true
kill_switch_policy_present: false | true
user_red_review_status: PENDING | APPROVED | REVISION_REQUESTED | ABORTED | NOT_REQUIRED
```

Red 正式输入：Frozen Resume + target/JD/stage + pinned Attack Skill + general knowledge。禁止读取 Zuno docs / source / Evidence / prior Blue answer key。

## Batch Duel State

当 `execution_mode=BATCH_DUEL`：

```text
batch_duel_status: NOT_STARTED | RUNNING | COMPLETE | ABORTED
batch_wave_index: 0
next_actor: RED | BLUE | NONE
red_wave1_status: NOT_STARTED | COMMITTED
blue_wave1_status: NOT_STARTED | COMMITTED
red_wave2_status: NOT_STARTED | COMMITTED
blue_wave2_status: NOT_STARTED | COMMITTED
red_wave1_commit_sha:
blue_wave1_commit_sha:
red_wave2_commit_sha:
blue_wave2_commit_sha:
```

执行顺序固定：

```text
RED_WAVE_1
→ commit
→ BLUE_WAVE_1
→ commit
→ RED_WAVE_2
→ commit
→ BLUE_WAVE_2
→ commit
```

### RED_WAVE_1 allowlist

```text
- frozen 01_simulated_resume.md
- frozen 02_red_questions.md plan / Pressure Suite
- pinned attack-model.md
- target / JD / stage
```

### BLUE_WAVE_1 allowlist

```text
- frozen Resume
- committed Red Wave 1
- pinned defense-model.md
- AGENTS.md
- canonical docs / Evidence / selected provenance @ zuno_base_sha
```

### RED_WAVE_2 allowlist

```text
- frozen Resume
- frozen Red Plan
- Red Wave 1
- committed Blue Wave 1 answers
- pinned attack-model.md
- target / JD / stage
```

Red Wave 2 必须明确从 Blue Wave 1 的 observable gaps 产生，不能在 Blue Wave 1 之前预写。

### BLUE_WAVE_2 allowlist

```text
- frozen Resume
- Red Wave 1 + Red Wave 2
- Blue Wave 1
- pinned defense-model.md
- canonical docs / Evidence / selected provenance @ zuno_base_sha
```

Pressure Suite 仍是离线覆盖库，不要求 Blue 机械回答 100 题。

## Live Interview State

当 `execution_mode=LIVE_INTERVIEW` 才使用：

```text
live_interview_status: NOT_STARTED | RUNNING | COMPLETE | ABORTED
live_turn_index: 0
next_actor: RED | BLUE | NONE
active_thread:
threads_completed: 0
interview_started_at:
interview_stop_reason:
last_question_commit_sha:
last_answer_commit_sha:
```

Red question commit 必须先于对应 Blue answer commit；Blue answer commit 必须先于下一 Red follow-up commit。

## Red Evaluation

```text
red_evaluation_status: NOT_STARTED | COMPLETE
```

Formal input: Frozen Resume + Frozen Red Plan + actual batch waves / live exchanges + pinned Attack Skill。不得读 Zuno docs。

## Blue Architecture Reflection

```text
blue_reflection_status: NOT_STARTED | COMPLETE
```

读取本轮面试产物 + canonical docs / Evidence @ `zuno_base_sha`，只判断 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals / No-change。

## Workflow Retrospective

```text
workflow_retrospective_status: NOT_STARTED | COMPLETE
resume_builder_reviewed: false
red_skill_reviewed: false
blue_skill_reviewed: false
harness_reviewed: false
```

必须分别审 Resume Builder、Red Skill、Blue Skill、Harness。

## Improvement Ledger

```text
improvement_ledger_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED
user_improvement_review_status: PENDING | APPROVED | PARTIAL_APPROVED | REVISION_REQUESTED | DEFERRED | NOT_REQUIRED
approved_change_count:
deferred_change_count:
post_improvement_head_sha:
```

Primary classification：

```text
RESUME_GAP
RED_SKILL_GAP
BLUE_SKILL_GAP
HARNESS_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_CHANGE
```

每条 finding 至少记录 signal、root cause、owner、proposed change、evidence needed、risk、status、next-round retest。

用户批准前不能修改 canonical Docs / Architecture 或 pinned Skills；用户已在当前对话明确批准的具体 workflow correction 可以标记为 approved。

## Post-round Apply

```text
change_effective_scope: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
```

Architecture change 仍须 Owner / ADR；Implementation / Evidence / Ownership gap 不能通过改文档或简历伪装解决。

## Next Resume Candidate

```text
next_resume_candidate_path: docs/red-blue/workspace/<round-id>/10_next_resume_candidate.md
next_resume_candidate_status: NOT_STARTED | BUILT | BLOCKED
next_resume_source_head_sha:
next_resume_blockers:
```

候选简历从 post-improvement branch HEAD 构建，只允许吸收已经成立的事实。下一 Round 仍重新校验并经过 USER_RESUME_REVIEW。

## Fixed Round Artifacts

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

BATCH_DUEL 的两波 Red 收敛进 `02_red_questions.md`，两波 Blue 收敛进 `03_blue_answers.md`。迁移旧 Round 时可以临时有 `02b/03b` compatibility artifacts，但 close 前必须说明。

## Stage State

```text
current_stage: ROUND_INIT | BUILD_RESUME | USER_RESUME_REVIEW | RESUME_REVISION | RED_QUESTIONS | USER_RED_REVIEW | RED_REVISION | INTERVIEW_EXECUTION | RED_WAVE_1 | BLUE_WAVE_1 | RED_WAVE_2 | BLUE_WAVE_2 | LIVE_INTERVIEW | RED_TURN | BLUE_TURN | RED_EVALUATION | BLUE_REFLECTION | WORKFLOW_RETROSPECTIVE | IMPROVEMENT_SYNTHESIS | USER_IMPROVEMENT_REVIEW | IMPROVEMENT_REVISION | APPLY_IMPROVEMENTS | BUILD_NEXT_RESUME | USER_FEEDBACK | CLOSE
resume_status: DRAFT | REVISION_REQUESTED | FROZEN
red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN | INVALIDATED_BY_RESUME_CHANGE
batch_duel_status: NOT_STARTED | RUNNING | COMPLETE | ABORTED
live_interview_status: NOT_STARTED | RUNNING | COMPLETE | ABORTED
red_evaluation_status: NOT_STARTED | COMPLETE
blue_reflection_status: NOT_STARTED | COMPLETE
workflow_retrospective_status: NOT_STARTED | COMPLETE
improvement_ledger_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED
next_resume_candidate_status: NOT_STARTED | BUILT | BLOCKED
```

## Close Conditions

正常完成 Round 必须满足：

```text
- branch + Draft PR exist
- every stage / wave / turn used commit-then-reread
- Resume frozen before Red
- Red Plan frozen before interview execution when gate required
- BATCH_DUEL: Wave 2 Red was generated only after committed Blue Wave 1
- LIVE_INTERVIEW: actual Red/Blue turns alternated
- Red Evaluation used actual executed answers, not Pressure Suite completion
- Blue Architecture Reflection completed against pinned base SHA
- Workflow Retrospective reviewed Resume Builder + Red Skill + Blue Skill + Harness
- Improvement Ledger exists and user review decision recorded
- approved changes are applied or explicitly deferred
- current-round verdict was not recomputed after post-round changes
- next Resume Candidate is built or blocked with explicit reason
- user feedback + session transcript complete
- workspace archived before merge
```

一个 Round 可以以 FAIL 结束；只要 failure 被正确路由并留下下一轮复测条件，它仍是有效 Round。
