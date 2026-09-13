# Red / Blue Round Manifest

> 每一轮复制本模板到 Round branch 的 `docs/red-blue/workspace/<round-id>/00_manifest.yaml`。Round 关闭前整个文件夹原样归档到 `docs/red-blue/rounds/<round-id>/`。

## Identity

```text
round_id:
created_at:
mode: CHATGPT_AUTO | AGENT_AUTO
zuno_base_sha:
state: ACTIVE | CLOSED | SUPERSEDED
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

每个 stage 从 GitHub live branch HEAD 读取允许输入，并在 transcript 写 `input_head_sha`。`last_consumed_head_sha` 只记录最近完成 stage 真正读取的 HEAD。

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
pressure_suite_count: 100
seed_question_target: 8
live_followups: DYNAMIC
one_question_one_intent: true
red_review_gate: REQUIRED | OPTIONAL | SKIP
```

工作流校准 Round 默认 `red_review_gate: REQUIRED`。

## Simulated Resume Build

Controller / Resume Builder 可以读取 `zuno_base_sha` 固定的 Zuno canonical docs 与已有简历风格，只用于生成本轮模拟简历。

```text
resume_style_reference:
resume_build_sources:
  - docs/project/
  - docs/architecture/
  - docs/modules/
  - docs/evidence/
  - selected docs/governance/ provenance
simulated_resume_path: docs/red-blue/workspace/<round-id>/01_simulated_resume.md
resume_status: DRAFT | FROZEN
```

`01_simulated_resume.md` 冻结并提交以后，Red 不得把上述 build sources 作为正式输入。

## Red Input Allowlist

```text
- 01_simulated_resume.md
- target role / JD / interview stage
- .agent/red-blue/attack-model.md
- model general knowledge
- explicitly approved generic ecosystem facts, if any
```

Explicit denylist:

```text
- docs/project/
- docs/architecture/
- docs/modules/
- docs/evidence/
- docs/decisions/
- docs/governance/
- Zuno source / PR / commit diff
- resume build notes / source trace
- prior Blue answers used as a hidden answer key
```

## Red Interview Plan

```text
red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN
seed_question_count:
pressure_suite_count: 100
live_followups: DYNAMIC
one_question_one_intent: true
branch_examples_present: false | true
kill_switch_policy_present: false | true
user_red_review_status: PENDING | APPROVED | REVISION_REQUESTED | ABORTED | NOT_REQUIRED
```

`02_red_questions.md` 默认包含：Interview Threads、6–10 条 `SPOKEN_SEEDS`、answer-driven `FOLLOWUP_POLICY`、若干 `BRANCH_EXAMPLES` 和 100 问 `PRESSURE_SUITE`。

Pressure Suite 用于离线覆盖，不是现场 45–60 分钟脚本。实际 Live Interview 后续问题必须根据上一答动态生成。

当 `red_review_gate: REQUIRED`：

```text
RED_QUESTIONS commit
→ USER_RED_REVIEW
→ APPROVE: red_questions_status=FROZEN
→ REQUEST_REVISION: feedback commit → RED_REVISION → USER_RED_REVIEW
→ ABORT: close/supersede
```

Red Revision 只能读取原 Red allowlist、当前 Red plan 和已提交的 Red-quality user feedback；仍不得读取 Zuno docs。旧版本由 Git history 保留。

## Blue Input Allowlist

只有 `red_questions_status: FROZEN` 才允许 Blue：

```text
- 01_simulated_resume.md
- 02_red_questions.md
- actual live interview transcript, if execution mode records it
- AGENTS.md
- docs/project/
- docs/architecture/
- docs/modules/
- docs/decisions/
- docs/evidence/
- selected docs/governance/ provenance facts
```

Blue 按 `zuno_base_sha` 读取 Zuno docs，并且在生成 `03_blue_answers.md` 前不读取 `04_red_evaluation.md`。

## Red Evaluation Input

```text
- 01_simulated_resume.md
- frozen 02_red_questions.md
- actual question/answer exchanges
- 03_blue_answers.md
- .agent/red-blue/attack-model.md
```

Red Evaluation 不把 Zuno canonical docs 作为正式评价输入。

## Blue Architecture Reflection Input

```text
- 01_simulated_resume.md
- 02_red_questions.md
- 03_blue_answers.md
- 04_red_evaluation.md
- Zuno canonical docs / evidence allowlist @ zuno_base_sha
```

## Workflow Retrospective Input

```text
- all committed observable round artifacts
- .agent/red-blue/attack-model.md
- 07_user_feedback.md
- prior workflow retrospectives when explicitly selected
```

## Interviewer Configuration

```text
primary_persona:
cross_personas:
  -
attack_skill_version:
interview_behavior_evidence_version:
time_budget_minutes:
```

Raw external interview corpus is upstream Skill evidence, not a default per-round Red input.

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
```

## Stage State

```text
current_stage: ROUND_INIT | BUILD_RESUME | RED_QUESTIONS | USER_RED_REVIEW | RED_REVISION | BLUE_ANSWERS | RED_EVALUATION | BLUE_REFLECTION | WORKFLOW_RETROSPECTIVE | CLOSE
resume_built: false
resume_frozen: false
red_questions_archived: false
red_questions_status: NOT_STARTED
user_red_review_status: PENDING
blue_answers_archived: false
red_evaluation_archived: false
blue_reflection_archived: false
workflow_retrospective_archived: false
user_feedback_archived: false
transcript_complete: false
```

## Round Init Feedback Rule

Round 启动前已经知道的用户流程约束、Red 质量反馈和校准目标必须在第一笔 Round transaction 中进入 `07_user_feedback.md` 与 `08_session_transcript.md`。

## Close Conditions

正常完成 Round 的必要条件：

```text
- round branch and Draft PR exist
- every stage used commit-then-reread handoff
- simulated resume frozen before Red
- Red formal inputs followed allowlist
- if red_review_gate=REQUIRED, user approved frozen Red plan before Blue
- Blue answered from allowed docs only
- Red evaluation completed without Zuno docs as formal input
- Blue architecture reflection completed
- workflow retrospective evaluated Red quality
- user feedback file exists
- observable session transcript is complete
- workspace folder is archived into rounds/<round-id>/ before merge
```

如果用户在 `USER_RED_REVIEW` 判定 Red Skill 本身需要结构性重写，可以把该 Round 标记 `SUPERSEDED`，保留失败的 Red artifact 和 feedback，再用新 Skill 开新 Round；不要强行在旧 Skill version 上继续 Blue。
