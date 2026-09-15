# Red / Blue Round Manifest

> 每一轮复制本模板到 `docs/red-blue/workspace/<round-id>/00_manifest.yaml`。Round 关闭前整个 workspace 原样归档。

## Identity

```text
round_id:
created_at:
mode: CHATGPT_AUTO | AGENT_AUTO
execution_mode: BATCH_DUEL | LIVE_INTERVIEW
zuno_base_sha:
state: ACTIVE | CLOSED | SUPERSEDED | INVALID_CALIBRATION
counts_as_formal_round: true | false
```

自动架构校准默认：

```text
execution_mode: BATCH_DUEL
counts_as_formal_round: true
```

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
resume_review_gate: REQUIRED | OPTIONAL | SKIP
improvement_review_gate: REQUIRED | OPTIONAL | SKIP
batch_checkpoint_policy: LINK_ONLY_PAUSE
red_wave_1_question_count: 100
blue_wave_1_answer_count: 100
red_wave_2_question_count: 100
blue_wave_2_answer_count: 100
one_question_one_intent: true
```

## Pinned Skills

Skill 在 Round Init 固定。本轮末可以修改，但只对下一轮生效。

```text
attack_skill_version: <sha>:.agent/red-blue/attack-model.md
defense_skill_version: <sha>:.agent/red-blue/defense-model.md
judge_version: <sha>:.agent/red-blue/judge.md
protocol_version: <sha>:.agent/red-blue/protocol.md
```

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

Resume Builder 优先写真实工程问题、个人动作、技术决策和可信结果；默认约 4–6 条。

## Red Wave 1

只有 Resume `FROZEN` 才允许开始。

```text
red_wave_1_status: NOT_STARTED | RUNNING | COMPLETE | INVALIDATED_BY_RESUME_CHANGE
red_wave_1_question_count: 0..100
red_wave_1_path: docs/red-blue/workspace/<round-id>/02_red_questions.md
red_wave_1_commit_sha:
red_wave_1_user_checkpoint: PENDING | CONTINUE | REVISION_REQUESTED | ABORTED
```

Red 输入：Frozen Resume + target/JD/stage + pinned Attack Skill + general knowledge。禁止读取 Zuno docs / source / Evidence。

## Blue Wave 1

```text
blue_wave_1_status: NOT_STARTED | RUNNING | COMPLETE
blue_wave_1_answer_count: 0..100
blue_wave_1_answers_path: docs/red-blue/workspace/<round-id>/03_blue_answers.md
blue_wave_1_architecture_notes_path: docs/red-blue/workspace/<round-id>/03_blue_architecture_notes.md
blue_wave_1_commit_sha:
blue_wave_1_user_checkpoint: PENDING | CONTINUE | REVISION_REQUESTED | ABORTED
```

Blue 回答 100 题，同时生成架构初诊。Architecture notes 对 Red 封存。

## Red Wave 2

```text
red_wave_2_status: NOT_STARTED | RUNNING | COMPLETE
blue_wave_1_blind_evaluation_present: false | true
red_wave_2_question_count: 0..100
red_wave_2_path: docs/red-blue/workspace/<round-id>/04_red_wave2_review_and_questions.md
red_wave_2_commit_sha:
red_wave_2_user_checkpoint: PENDING | CONTINUE | REVISION_REQUESTED | ABORTED
```

### RED_WAVE_2 allowlist

```text
- frozen 01_simulated_resume.md
- 02_red_questions.md
- 03_blue_answers.md
- pinned attack-model.md
- target / JD / stage
```

明确禁止：

```text
- 03_blue_architecture_notes.md
- canonical Zuno docs / source / Evidence
```

Red 2 必须先评价 Blue 1，再生成恰好 100 个 answer-driven follow-ups。

## Blue Wave 2

```text
blue_wave_2_status: NOT_STARTED | RUNNING | COMPLETE
blue_wave_2_answer_count: 0..100
blue_wave_2_answers_path: docs/red-blue/workspace/<round-id>/04_blue_wave2_answers.md
blue_wave_2_architecture_notes_path: docs/red-blue/workspace/<round-id>/04_blue_wave2_architecture_notes.md
blue_wave_2_commit_sha:
blue_wave_2_user_checkpoint: PENDING | CONTINUE | REVISION_REQUESTED | ABORTED
```

Blue 2 读取 Red 2 的公开评价和问题，但 Candidate answer generation 不读取 Wave 1 architecture notes。

## Red Evaluation

```text
red_evaluation_status: NOT_STARTED | COMPLETE
```

Formal input：Frozen Resume + 两轮 Red questions + 两轮 Blue answers + pinned Attack Skill。不得读 Zuno docs 或 Blue architecture notes。

## Blue Architecture Reflection

```text
blue_reflection_status: NOT_STARTED | COMPLETE
```

读取全部面试产物 + 两份 provisional architecture notes + canonical docs / Evidence @ `zuno_base_sha`。

必须判断 Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals / No-change，并允许提出 Multi-Agent、Subgraph、Generic Host、删复杂度等替代方案。

## Workflow Retrospective

```text
workflow_retrospective_status: NOT_STARTED | COMPLETE
resume_builder_reviewed: false
red_thinking_framework_reviewed: false
blue_candidate_framework_reviewed: false
blue_architecture_framework_reviewed: false
harness_reviewed: false
```

必须审 Resume Builder、Red 思维框架、Blue 候选回答框架、Blue 架构诊断框架、Harness。

## Improvement Ledger / Round Report

```text
improvement_ledger_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED
round_report_status: NOT_STARTED | BUILT
round_report_path: docs/red-blue/workspace/<round-id>/09_round_report.md
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

## Post-round Apply

批准的改进可以在 Round branch 后半段应用，但必须：

```text
change_effective_scope: NEXT_ROUND_ONLY
current_round_verdict_recomputed: false
```

Architecture change 仍须 Owner / ADR；Implementation / Evidence / Ownership gap 不能靠改文档或改简历伪装解决。

## Next Resume Candidate

```text
next_resume_candidate_path: docs/red-blue/workspace/<round-id>/10_next_resume_candidate.md
next_resume_candidate_status: NOT_STARTED | BUILT | BLOCKED
next_resume_source_head_sha:
next_resume_blockers:
```

## Core Round Artifacts

为历史兼容，core 仍保留：

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

BATCH_DUEL 额外要求：

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

## Stage State

```text
current_stage: ROUND_INIT | BUILD_SIMULATED_RESUME | USER_RESUME_REVIEW | RESUME_REVISION | RED_WAVE_1 | BATCH_CHECKPOINT_RED_1 | BLUE_WAVE_1 | BATCH_CHECKPOINT_BLUE_1 | RED_WAVE_2 | BATCH_CHECKPOINT_RED_2 | BLUE_WAVE_2 | BATCH_CHECKPOINT_BLUE_2 | RED_EVALUATION | BLUE_ARCHITECTURE_REFLECTION | WORKFLOW_RETROSPECTIVE | IMPROVEMENT_SYNTHESIS | ROUND_REPORT | USER_IMPROVEMENT_REVIEW | IMPROVEMENT_REVISION | APPLY_IMPROVEMENTS | BUILD_NEXT_RESUME_CANDIDATE | USER_FEEDBACK | CLOSE | LIVE_INTERVIEW | RED_TURN | BLUE_TURN
resume_status: DRAFT | REVISION_REQUESTED | FROZEN
red_wave_1_status: NOT_STARTED | RUNNING | COMPLETE
blue_wave_1_status: NOT_STARTED | RUNNING | COMPLETE
red_wave_2_status: NOT_STARTED | RUNNING | COMPLETE
blue_wave_2_status: NOT_STARTED | RUNNING | COMPLETE
red_evaluation_status: NOT_STARTED | COMPLETE
blue_reflection_status: NOT_STARTED | COMPLETE
workflow_retrospective_status: NOT_STARTED | COMPLETE
improvement_ledger_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | APPROVED | PARTIAL_APPROVED | DEFERRED
next_resume_candidate_status: NOT_STARTED | BUILT | BLOCKED
```

## LIVE_INTERVIEW State（可选模式）

若显式使用 `LIVE_INTERVIEW`：

```text
live_interview_status: NOT_STARTED | RUNNING | COMPLETE | ABORTED
live_turn_index: 0
next_actor: RED | BLUE | NONE
```

### RED_TURN allowlist

```text
- frozen Resume
- pinned attack-model.md
- observable exchanges so far
```

### BLUE_TURN allowlist

```text
- frozen Resume
- current committed Red question
- observable exchanges so far
- pinned defense-model.md
- allowed canonical sources @ zuno_base_sha
```

Red question commit 必须先于对应 Blue answer commit。Blue answer commit 必须先于下一 Red follow-up commit。

## Close Conditions

正式 BATCH_DUEL Round 正常完成必须满足：

```text
- branch + Draft PR exist
- Resume frozen before Red
- Red Wave 1 == 100 questions
- Blue Wave 1 == 100 answers
- Blue Wave 1 architecture notes sealed from Red
- Red Wave 2 contains Blue-1 blind evaluation + exactly 100 new questions
- Blue Wave 2 == 100 answers
- Red Final did not read canonical docs / Blue architecture notes
- Blue Final Architecture Reflection completed against pinned base SHA
- Workflow Retrospective reviewed Resume + Red framework + Blue candidate framework + Blue architecture framework + Harness
- Improvement Ledger + Round Report exist
- user improvement decision recorded
- approved changes applied or explicitly deferred
- current-round verdict was not recomputed after post-round changes
- next Resume Candidate built or blocked with explicit reason
- workspace archived before merge
```

一个 Round 可以 FAIL；只要问题被正确归因并形成下一轮复测条件，它仍然有效。