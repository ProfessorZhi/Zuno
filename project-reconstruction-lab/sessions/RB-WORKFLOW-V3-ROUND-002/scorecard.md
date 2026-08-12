# Round-002 Scorecard

```yaml
protocol_version: ZUNO-RED-BLUE-WORKFLOW-V3
round_id: RB-WORKFLOW-V3-ROUND-002
question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novelty_status: ASSESSED
novel_question_count: 80
regression_question_count: 20
raw_score: 371
normalized_score: 74.20
grade: Architecture Requires Significant Repair
new_a_p0: 0
p0_count: 8
p1_count: 23
p2_count: 69
p3_count: 0
closure_class_counts:
  A: 0
  I: 5
  E: 3
  X: 0
canonical_sync_status: APPLIED
round_status: COMPLETE
round_003_status: READY_NOT_STARTED
```

| Lens | Questions | Raw Score | Normalized |
|---|---:|---:|---:|
| 00 Overall Architecture | 12 | 45 | 75.00 |
| 01 Product Surface | 6 | 23 | 76.67 |
| 02 Input / Document Ingestion | 7 | 26 | 74.29 |
| 03 Knowledge / Agentic GraphRAG | 11 | 41 | 74.55 |
| 04 Model Gateway | 6 | 23 | 76.67 |
| 05 Memory & Context | 8 | 29 | 72.50 |
| 06 Agent Core / Planning & Control | 14 | 51 | 72.86 |
| 07 Capability / Skill | 6 | 25 | 83.33 |
| 08 Tool Runtime | 10 | 36 | 72.00 |
| 09 Security | 8 | 29 | 72.50 |
| 10 Observability & Eval | 6 | 22 | 73.33 |
| 11 Infrastructure | 6 | 21 | 70.00 |

Total Raw Score: 371/500
Normalized Score: 74.20/100

Score is a defense diagnostic, not Production Readiness.

## Decision summary

- AUTO_APPLY deltas: 11
- ADR Escalation: 0
- User Gate Escalation: 0
- New A-P0: 0
- I/E/X gaps remain open; no P0 is closed by this Round.
