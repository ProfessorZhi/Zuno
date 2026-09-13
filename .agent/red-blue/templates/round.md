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

每个 stage 从 GitHub live branch HEAD 读取允许输入，并在 transcript 写 `input_head_sha`。`last_consumed_head_sha` 只记录最近完成 stage 真正读取的 HEAD，不作为 live ref 的替代品。

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED` 且不能声明严格 blind Red；`AGENT_AUTO` 只有在 Red 使用独立 context 时才使用 `PHYSICAL_CONTEXT_ISOLATION`。

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
question_count: 100
primary_path_target: 30
reserve_target: 70
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

`01_simulated_resume.md` 冻结并提交以后，Red 不得把上述 build sources 作为正式出题输入。

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

## Red Question Suite

```text
red_questions_status: NOT_STARTED | DRAFT_REVIEW | REVISION_REQUESTED | FROZEN
primary_path_count:
reserve_count:
kill_switches_present: false | true
user_red_review_status: PENDING | APPROVED | REVISION_REQUESTED | ABORTED | NOT_REQUIRED
```

`02_red_questions.md` 默认包含 25–40 条 `PRIMARY_PATH` 与其余 `RESERVE_FOLLOWUP`。总问题数默认 100，但真实面试执行不机械问完 100 题。

当 `red_review_gate: REQUIRED`：

```text
RED_QUESTIONS commit
→ USER_RED_REVIEW
→ APPROVE: red_questions_status=FROZEN
→ REQUEST_REVISION: feedback commit → RED_REVISION → USER_RED_REVIEW
→ ABORT: close/supersede
```

Red Revision 只能读取原 Red allowlist、当前题单和已提交的 Red-quality user feedback；仍不得读取 Zuno docs。旧题单由 Git history 保留。

## Blue Input Allowlist

只有 `red_questions_status: FROZEN` 才允许 Blue：

```text
- 01_simulated_resume.md
- 02_red_questions.md
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
question_budget_notes:
```

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

Round 启动前已经知道的用户流程约束、Red 质量反馈和校准目标必须在第一笔 Round transaction 中进入 `07_user_feedback.md` 与 `08_session_transcript.md`。不能等到 Workflow Retrospective 再补录。

## Close Conditions

Round 可以关闭的必要条件：

```text
- round branch and Draft PR exist
- every stage used commit-then-reread handoff
- simulated resume frozen before Red questions
- Red formal inputs followed the allowlist
- if red_review_gate=REQUIRED, user approved frozen Red questions before Blue
- Blue answered from allowed docs only
- Red evaluation completed without Zuno docs as formal input
- Blue architecture reflection completed
- workflow retrospective evaluated Red quality
- user feedback file exists
- observable session transcript is complete
- workspace folder is archived into rounds/<round-id>/ before merge
```

Retest 不在同一 Round 继续追加第二批问题；创建新的 round-id，并重新生成与当时 docs 对应的模拟简历。
