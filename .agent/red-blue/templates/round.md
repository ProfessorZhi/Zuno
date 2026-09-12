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
batch_size: 100
max_batches:
```

## Transcript Policy

```text
transcript_policy: full-observable-role-io
archive_live: true
transcript_index: docs/red-blue/rounds/<round-id>/transcript.md
transcript_shards:
  - docs/red-blue/rounds/<round-id>/transcript-batch-001.md
```

`full-observable-role-io` 要求保存 Red / Blue / Verifier / Controller / user intervention 的可观察输入输出与显式协议元数据。它不要求、也不得伪造模型私有 chain-of-thought。

如果单个 `transcript.md` 足够，可以不创建 shard；一旦分片，manifest 必须完整列出全部 shard。

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

| Scenario or Claim | Risk | Why It Matters | Expected Evidence | Priority | Initial Question Budget |
| --- | --- | --- | --- | --- | ---: |
|  |  |  |  |  |  |

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

不要求平均覆盖；按业务和 Claim 风险分配 batch 问题预算。

## Batch Lifecycle

```text
batch-001:
  red_generated: false
  red_archived: false
  blue_answered: false
  blue_archived: false
  verified: false
  verifier_archived: false
  question_count: 0
  next_focus: none
```

每个 batch 的问题在 Red 输出时冻结；基于 Blue 回答产生的新追问进入下一批。

## Stop Conditions

```text
- max_batches reached
- target scenario / claim sufficiently tested
- stable high-severity finding found
- information exhausted
- next batch would only add trivia
- user intervenes to close
```

## Outputs

```text
manifest: docs/red-blue/rounds/<round-id>/manifest.yaml
transcript: docs/red-blue/rounds/<round-id>/transcript.md
transcript_shards: docs/red-blue/rounds/<round-id>/transcript-batch-*.md  # optional
findings: docs/red-blue/rounds/<round-id>/findings.md
archive_target: docs/red-blue/rounds/<round-id>/
```

Round 完成后恢复 `.agent/red-blue/current.md` 为 `no-active`。