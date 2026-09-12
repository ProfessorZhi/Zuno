# Red / Blue Batch Record

> 文件名保留 `turn.md` 以兼容现有 Harness；正式运行单位已改为 batch。

## Identity

```text
round_id:
batch_id:
question_count:
created_at:
```

## Controller — Observable Event Log

按发生顺序追加，不覆盖：

```text
- event_id:
  actor: controller | user
  event:
  payload_summary:
```

## Red — Batch Configuration

```text
interviewer_persona:
cross_persona:
claim_budget:
attack_reweighting_from_prior_batch:
```

## Red — Questions

一批默认 100 问。每道题独立编号，不附给 Blue 的提示、评分点或参考答案。

```text
- question_id: Q001
  claim_under_test:
  attack_angle:
  red_question:
  red_hidden_intent:        # 协议显式攻击元数据，不是模型私有 chain-of-thought
  expected_evidence:
  counterexample_or_failure_injection:
```

Red 输出后立即归档，随后才允许 Blue 开始回答。

## Blue — Closed-book Answers

逐题回答，不合并成一份总答复。

```text
- question_id: Q001
  answer:
  source_trace:
    resume:
    project_part_a:
    architecture_part_a:
    module_part_a:
    engineering_reference:
    adr:
    evidence:
    unknown_or_unsupported:
```

Blue 完成整批后立即归档，Verifier 才开始逐题判断。

## Verifier — Per-question Results

```text
- question_id: Q001
  verdict: PASS | PARTIAL | FAIL | UNSUPPORTED_CLAIM
  severity: S0 | S1 | S2 | S3
  gap_type:
  reason:
  source_support:
  current_target_check:
  ownership_check:
  next_action: DECREASE_WEIGHT | CONTINUE_NEXT_BATCH | REFRAME_NEXT_BATCH | ESCALATE_FINDING | CLOSE_CHAIN
```

Verifier 不生成 Blue 的改进版标准答案。

## Batch Transition

```text
passed_count:
partial_count:
failed_count:
unsupported_count:
new_findings:
attack_reweighting:
next_batch_focus:
batch_status: archived | needs-archive
```

## Archive Invariant

`CHATGPT_AUTO` 与 `AGENT_AUTO` 都必须保存本 batch 的完整可观察 Red / Blue / Verifier 输出和 Controller / user intervention。允许因 GitHub 单文件大小限制将 batch 写入 `transcript-batch-NNN.md`，但不得只留下题单、摘要或 `findings.md`。

这里的“完整”不包含模型私有 chain-of-thought；不得伪造或要求导出不可观察的内部推理。