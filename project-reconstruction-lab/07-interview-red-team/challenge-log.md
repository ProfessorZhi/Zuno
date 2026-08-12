# Interview Challenge Log

## Record Template

```yaml
challenge_id: INT-YYYY-NNN
question:
expected_depth: REALITY | CODE | ARCHITECTURE | FAILURE | COUNTERFACTUAL
current_answer:
evidence_ids: []
weakness:
risk: P0 | P1 | P2 | P3
fact_gap:
architecture_gap:
action:
architecture_impact:
status: OPEN | RESEARCHING | USER_CONFIRMATION_REQUIRED | CLOSED
```

## Risk

- `P0`：一问就穿，存在虚假或 Current/Target 混淆。
- `P1`：核心设计、个人贡献或失败语义无法解释。
- `P2`：工程细节不足，但不击穿主线。
- `P3`：表达可优化。

目标是逐步将 P0 降到 0，而不是把所有问题都包装成已知。
