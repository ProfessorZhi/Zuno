# PHASE20 Observability Eval, Benchmark and Release Gate

phase_id: PHASE20
status: planned
depends_on: PHASE06, PHASE18, PHASE19
owner: Module 10 Observability & Eval

## Phase 目标

在完整 Trace 基础上实现 EvalDataset/Version/Case、EvalRun/CaseExecution、RAG Core Five、GraphRAG Trace、Agent Efficiency、Failure Bucket、BenchmarkComparison、MeasurementStatus、ReleaseGateEvaluation 和 EvidenceRecord。此 Phase 建立真实评测能力，但最终固定数据集运行和生产就绪结论在 PHASE22。

## Minimal Read Set

- `docs/modules/10-observability-eval.md`
- PHASE06 Trace/Audit
- PHASE18 GraphRAG inner loop
- PHASE19 FinalCandidate/RunOutcome
- 当前 tools/evals/zuno runners/datasets/reports

## Current Anchors

```text
tools/evals/zuno/**
src/backend/zuno/platform/observability/**
current benchmark/profile/release gate helpers
task observability snapshot and GraphRAG trace
sample-8/sample-80 references
```

## Allowed Paths

```text
src/backend/zuno/platform/observability/domain/**
src/backend/zuno/platform/observability/application/**
src/backend/zuno/platform/observability/adapters/**
src/backend/zuno/platform/database/observability/**
tools/evals/zuno/**
alembic/**
tests/eval/**
tests/integration/eval/**
tests/fault/eval/**
docs/evidence/**
```

## Forbidden Paths

- Eval 修改源 Run/Evidence/Tool/Memory 事实。
- 缺数据记 0，BLOCKED/UNAVAILABLE/INCOMPARABLE 转 PASS。
- 只比较总平均，掩盖关键 Slice 退化。
- Judge Prompt/Model 未版本化。

## Work Packages

### P20-T01 Eval Dataset, Version and Case Ledger
- Goal：实现 immutable dataset/case set hash、question/reference claims/gold evidence/slices/security scope。
- Tests：hash drift、duplicate case、missing reference、unauthorized dataset、supersession。
- Acceptance：数据集和 Case Version 可重现。

### P20-T02 EvalRun, CaseExecution and Recovery
- Goal：实现 pinned corpus/snapshot/index/model/runtime/judge/metric config，case lease/checkpoint/attempt/retry。
- Tests：worker crash、duplicate case、partial run、resume、cancel、dataset mismatch。
- Acceptance：Partial/BLOCKED 不发布 measured claim。

### P20-T03 RAG Core Five Metrics
- Goal：实现 Context Precision/Recall、Faithfulness、Answer Relevancy、Answer Correctness，版本化输入/algorithm/judge/embedding。
- Tests：missing claims、judge timeout/invalid、context rank swap、reference mismatch、metric cache hash。
- Acceptance：MetricStatus 明确 MEASURED/BLOCKED/UNAVAILABLE/INVALID。

### P20-T04 GraphRAG Trace and Diagnostic Metrics
- Goal：记录 route/profile/round/retriever/entity/relation/path/community/fusion/rerank/source grounding 和 failure bucket。
- Tests：entity miss、graph snapshot missing、fusion drops gold、reranker demotes、DRIFT explosion、source mapping loss。
- Acceptance：可定位“哪一步丢失正确证据”。

### P20-T05 Agent Loop and Efficiency Metrics
- Goal：记录 plan/retry/replan/reflection/tool/model/retrieval calls、critical path、parallel efficiency、wasted work、evidence yield、human intervention。
- Tests：hidden model retry、replan churn、partial parallel fail、settled usage delay、missing trace。
- Acceptance：Estimated Cost 不通过 Settled Cost Gate。

### P20-T06 Failure Bucket and Evaluation Slices
- Goal：实现 single-hop/multi-hop/entity/relation/global/temporal/conflict/no-answer/citation-required/security slices 与 failure taxonomy。
- Tests：slice completeness、critical regression、unknown failure、multiple bucket、redaction。
- Acceptance：总平均不能覆盖关键 Slice 退化。

### P20-T07 Benchmark Comparison and Comparability
- Goal：比较 standard/local/deep/agentic，先校验 dataset/snapshot/index/model/judge/embedding/metric/runtime/security scope。
- Tests：config mismatch→INCOMPARABLE、partial profile→BLOCKED、same hash comparable、late revision。
- Acceptance：不对不可比运行计算阈值。

### P20-T08 Release Gate, Evidence Registry and Query API
- Goal：实现 Core Five、Citation/Safety、Critical Slice、Quality-constrained Efficiency Gate，保存 immutable result/evidence hash，并提供 query/report。
- Tests：PASSED/FAILED/BLOCKED/INCOMPARABLE/ERROR、artifact hash mismatch、expired evidence、gate replay。
- Acceptance：Gate 只绑定不可变 Eval Result Set；不声称尚未执行的质量。

## Phase 完成定义

- Eval 数据/运行/指标/比较/Gate/Evidence Runtime 可用。
- Core Five/Graph/Agent Efficiency/Fault Test 通过。
- 真实固定 Benchmark 尚未运行时状态保持 measurement blocked。

## Validation

```bash
git diff --check
python tools/scripts/verify_observability_eval_target_protocols.py
pytest -q tests/eval tests/integration/eval tests/fault/eval -p no:cacheprovider
# run deterministic small eval fixtures, not production quality claim
```
