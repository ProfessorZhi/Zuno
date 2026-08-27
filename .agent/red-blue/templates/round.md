# Red / Blue Round Manifest

> 每一轮都复制本模板到临时 active workspace；不要直接修改模板本身保存运行状态。

## Identity

```text
round_id:
created_at:
mode: human-candidate | chatgpt-duel | autonomous-agent
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

## Interview Target

```text
target_role:
company_or_persona:
interview_stage:
jd_source:
time_budget:
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

Red calibration sources 只用于构建 private pressure model，不进入 Blue context。

## Blue Closed-book Allowlist

```text
- exact resume snapshot
- AGENTS.md
- docs/project/
- docs/architecture/
- docs/modules/
- docs/decisions/
- docs/evidence/
- docs/governance/project-fact-provenance.md
```

如本轮需要不同 allowlist，必须在开始前显式写出；运行中不得临时扩大。

## Claim Inventory

先从简历抽取，不从题库开始。

| Claim | Claim Type | Why Risky | Resume Location | Priority |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

选择 3–5 条本轮主攻 Claim。

## Attack Coverage Intention

本栏是 Red / Judge 私有配置，不给 Blue：

```text
business causality:
ownership:
architecture:
build_buy:
implementation:
failure_recovery:
concurrency_idempotency:
security:
scale_performance_cost:
evaluation_evidence:
current_target:
simplification:
fundamentals_from_project:
```

不要求每轮平均覆盖；按岗位和 Claim 风险动态选择。

## Stop Conditions

```text
- max turns reached
- target claim coverage reached
- two stable high-severity gaps found
- information exhausted
- user ends the round
```

## Outputs

```text
transcript:
judge_report:
gap_summary:
archive_target: docs/maintenance/history/red-blue/<round-id>.md
```

Round 完成后恢复 `.agent/red-blue/current.md` 为 `no-active`。