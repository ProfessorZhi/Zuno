# V4.2 ChatGPT Review Template

## Review Identity

```yaml
workflow_id: ZUNO-RED-BLUE-WORKFLOW-V4.2
execution_profile: BATCH_ADVERSARIAL
review_status: WAITING_FOR_CHATGPT_REVIEW
external_reviewed_sha: NOT_PROVIDED
```

## Required Review Package

- BASE Part A；
- Complete Q/A Ledger；
- Blue Architecture Decisions；
- Canonical Delta；
- Final Part A / Part B；
- Candidate SHA；
- Profile-specific Session IDs and BASE Snapshot mapping；
- `adaptive_followup_ratio`；
- `pregenerated_question_violation`；
- `chain_stop_quality`；
- `highest_depth_chains` / `weakest_chains`；
- `part_a_gap_triggered_questions`；
- `term_dependent_questions`；
- `canonical_rewrite_mapping`；
- `counter_retest_results`。

Batch Profile 还必须附带：完整 100Q/Answer coverage、Counter 到原始 Blue Answer 的引用、
Synthesis/Counter/Judge 顺序、Fresh Judge 证据、Candidate branch 与 Main 的差异，以及
`main_merge_status`。Live Profile 则附带 append-only rolling ledger、动态 follow-up ratio、
question freeze 顺序和 pre-generated question violation 检查。

## Verdict

```yaml
verdict: NOT_PROVIDED
repair_required: UNKNOWN
external_reviewed_sha: NOT_PROVIDED
```

只有 `ACCEPT` 或 `ACCEPT_WITH_DEBT` 可以进入 Main Merge Gate。Bootstrap 不代表真实
Fresh Session、Context Isolation、Red-only Calibration 或 Merge 已经运行。
