# Red / Blue Round Manifest

> 每一轮复制本模板到 `docs/red-blue/workspace/<round-id>/00_manifest.yaml`。Round 关闭后整个文件夹原样归档到 `docs/red-blue/rounds/<round-id>/`。

## Identity

```text
round_id:
created_at:
mode: CHATGPT_AUTO | AGENT_AUTO
zuno_base_sha:
state: ACTIVE | CLOSED | SUPERSEDED
```

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
question_count: 100
```

## Simulated Resume Build

Controller / Resume Builder 可以读取当前 Zuno canonical docs 与已有简历风格，只用于生成本轮模拟简历。

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

`01_simulated_resume.md` 冻结以后，Red 不得读取上述 build sources。

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

Blue does not read `04_red_evaluation.md` before producing `03_blue_answers.md`.

## Red Evaluation Input

```text
- 01_simulated_resume.md
- 02_red_questions.md
- 03_blue_answers.md
- .agent/red-blue/attack-model.md
```

Red Evaluation still cannot read Zuno canonical docs.

## Blue Architecture Reflection Input

```text
- 01_simulated_resume.md
- 02_red_questions.md
- 03_blue_answers.md
- 04_red_evaluation.md
- Zuno canonical docs / evidence allowlist
```

## Workflow Retrospective Input

```text
- all observable round artifacts
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
- simulated resume frozen before Red questions
- Red did not read Zuno docs
- Blue answered from allowed docs only
- Red evaluation completed without Zuno docs
- Blue architecture reflection completed
- workflow retrospective evaluated Red quality
- user feedback file exists, even if it says no additional feedback
- observable session transcript is complete
```

Retest 不在同一 Round 继续追加第二批问题；创建一个新的 round-id，并重新生成与当时 docs 对应的模拟简历。