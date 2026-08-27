# Red / Blue Turn

## Identity

```text
round_id:
turn_id:
claim_under_test:
```

## Red — Private

```text
interviewer_persona:
attack_angle:
current_hypothesis:
expected_evidence:
counterexample_or_failure_injection:
next_drill_if_weak:
next_drill_if_strong:
```

## Red — User-visible Question

> 一次只写一个主要问题，不附提示、关键词、评分点或参考答案。

```text
question:
```

## Blue — Closed-book Answer

```text
answer:
```

### Blue Source Trace

只记录实际使用的允许来源：

```text
resume:
project_part_a:
architecture_part_a:
module_part_a:
engineering_reference:
adr:
evidence:
unknown_or_unsupported:
```

## Judge — Private

```text
verdict: PASS | PARTIAL | FAIL | UNSUPPORTED_CLAIM
severity: S0 | S1 | S2 | S3
gap_type:
reason:
source_support:
current_target_check:
ownership_check:
next_action: CONTINUE_SAME_CHAIN | REFRAME_SAME_RISK | NEXT_ATTACK_ANGLE | NEXT_CLAIM | CLOSE_ROUND
```

## Round Transition

```text
next_turn_focus:
claim_status: open | passed | failed | unsupported
```

不要在这里写 Blue 的改进版标准答案。修复建议只在 Round 结束后的 Judge Report 中形成，并由独立任务处理。