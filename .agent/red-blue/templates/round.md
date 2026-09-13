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
stage_head_sha:
firewall_strength: LOGICAL_GITHUB_MEDIATED | PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: false | true
```

`CHATGPT_AUTO` 使用 `LOGICAL_GITHUB_MEDIATED` 且不能声明严格 blind Red；`AGENT_AUTO` 只有在 Red 使用独立 context 时才使用 `PHYSICAL_CONTEXT_ISOLATION`。

每个 stage 从 `stage_head_sha` 对应 GitHub HEAD 读取允许输入。本阶段 artifact、manifest state 和 `08_session_transcript.md` 提交后，才允许推进下一阶段。

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
question_count: 100
```

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

## Blue Input Allowlist

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
- 02_red_questions.md
- 03_blue_answers.md
- .agent/red-blue/attack-model.md
```

Red Evaluation still cannot read Zuno canonical docs as formal evaluation input.

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

Raw external interview corpus is not a default per-round Red input. It is used when refreshing the Attack Skill in a separate task.

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
resume_built: false
resume_frozen: false
red_questions_archived: false
blue_answers_archived: false
red_evaluation_archived: false
blue_reflection_archived: false
workflow_retrospective_archived: false
user_feedback_archived: false
transcript_complete: false
```

## Close Conditions

Round 可以关闭的必要条件：

```text
- round branch and Draft PR exist
- every stage used commit-then-reread handoff
- simulated resume frozen before Red questions
- Red formal inputs followed the allowlist
- Blue answered from allowed docs only
- Red evaluation completed without Zuno docs as formal input
- Blue architecture reflection completed
- workflow retrospective evaluated Red quality
- user feedback file exists, even if it says no additional feedback
- observable session transcript is complete
- workspace folder is archived into rounds/<round-id>/ before merge
```

Retest 不在同一 Round 继续追加第二批问题；创建一个新的 round-id，并重新生成与当时 docs 对应的模拟简历。