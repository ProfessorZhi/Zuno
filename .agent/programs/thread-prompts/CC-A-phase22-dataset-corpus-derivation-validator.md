# CC-A PHASE22 Dataset / Corpus / Derivation Validator

WORKER_TASK_ID: CC-A-PHASE22-DATASET-CORPUS-DERIVATION
Base SHA: 95e17fc522591e7ee543b40b5b568d71963b6aa0

## Goal

完成 machine-attested synthetic regression 的 80 Case Dataset、完整 Corpus、World Model、Derivation Validator、Dataset Hash 和 Corpus Hash。

## Current Gap

当前只有 public review pack 和被 invalidated 的 PR #100 历史资产；没有 Current 分支内 80/80 独立推导校验通过的 synthetic regression dataset。

## Allowed Paths

- `tools/evals/zuno/synthetic_benchmark/**`
- `tests/evals/synthetic_benchmark/**`
- `docs/evidence/goal05-phase22-machine-attested-synthetic-regression/**`

## Forbidden Paths

- 不修改 production runtime。
- 不读取 `expected_answer` 作为推导输入。
- 不继承 PR #100 的 substring retrieval、in-memory profile、gold citation 注入、手写 Trace/Receipt/RunOutcome。
- 不修改 public benchmark 的 `reviewer_approved_count` 或 `benchmark_eligible_count`。

## Contracts

每个 case 必须包含：`case_id`、`question`、`question_type`、`expected_answer`、`derivation_spec`、`source_document_refs`、`source_span_refs`、`security_principal`、`tenant_id`、`workspace_id`、`security_epoch_ref`、`expected_behavior`、`failure_expectation`、`generation_seed`、`input_hash`、`case_hash`。

## Owner

Eval / Benchmark dataset owner；不得写入 Knowledge Runtime 领域事实。

## State Transitions

`draft_case -> schema_valid -> derivation_valid -> source_evidence_valid -> synthetic_regression_eligible`

## Failure Semantics

无法独立推导、source span 不闭合、relation direction 不精确、时间版本不闭合、gold 泄漏、重复问题、hard negative 不成立时，该 case 必须 rejected 或 replaced。

## Retry / Recovery / Idempotency

同 seed 重建必须得到相同 `input_hash` 和 `case_hash`；替换 case 必须记录旧 case id 和替换原因。

## Security

Security case 必须验证 principal / role / scope / epoch；no-answer 必须扫描授权 corpus。

## Required Tests

```powershell
python -m pytest -q tests/evals/synthetic_benchmark -p no:cacheprovider
python tools/evals/zuno/synthetic_benchmark/validate_cases.py --cases <cases> --corpus <corpus> --world-model <world_model>
```

## Acceptance Criteria

- 80/80 schema valid
- 80/80 derivation valid
- 80/80 source evidence valid
- 0 duplicate
- 0 gold leakage
- 0 unsupported answer
- dataset hash and corpus hash recorded

## Commit Contract

普通 commit，禁止 amend/force-push；提交信息包含 `[worker=CC-A]`。

## Handoff Format

提交 `git show <WORKER_SHA>` 摘要、验证命令、exit code、dataset hash、corpus hash、case distribution 和 failure list。
