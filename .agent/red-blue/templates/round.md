# Red / Blue Round Manifest

> 每一轮复制本模板到临时 active workspace；不要把运行状态写回模板。

## Identity

```text
round_id:
created_at:
mode: CHATGPT_AUTO | AGENT_AUTO
zuno_base_sha:
```

## Candidate Input

```text
resume_repository:
resume_commit_sha:
resume_path:
resume_status: verified-main | historical | user-selected
```

禁止自动选择标记为“待核验包装稿”的简历。

## Interview / Review Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
scenario_scope:
max_turns:
```

## Red Configuration

```text
primary_persona:
cross_persona:
calibration: kernel-only | calibrated
calibration_sources:
  -
```

Red calibration 只用于 private pressure model，不进入 Blue context。

## Blue Closed-book Allowlist

```text
- exact resume snapshot
- AGENTS.md
- docs/project/
- docs/architecture/
- docs/modules/
- docs/decisions/
- docs/evidence/
- selected docs/governance/ provenance facts
```

运行中不得临时扩大 allowlist。

## Scenario / Claim Inventory

优先从真实业务场景和简历高风险 Claim 进入，不从题库开始。

| Scenario or Claim | Risk | Why It Matters | Expected Evidence | Priority |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Attack Coverage

```text
business causality:
baseline_and_replaceability:
ownership:
authority_and_state:
failure_recovery:
external_effect:
continuous_authorization:
build_buy_extend_delete:
scale_performance_cost:
evaluation_evidence:
current_target:
simplification:
```

不要求平均覆盖；按业务和 Claim 风险选择。

## Stop Conditions

```text
- max turns reached
- target scenario / claim sufficiently tested
- stable high-severity finding found
- information exhausted
- next questions would only add trivia
- user intervenes to close
```

## Outputs

```text
transcript: docs/red-blue/rounds/<round-id>/transcript.md
findings: docs/red-blue/rounds/<round-id>/findings.md
archive_target: docs/red-blue/rounds/<round-id>/
```

Round 完成后恢复 `.agent/red-blue/current.md` 为 `no-active`。