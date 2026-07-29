# Goal05 PHASE20 Eval Runtime Evidence

status: implementation_progress
date: 2026-07-29
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据只证明 PHASE20 Observability Eval Runtime 的核心运行时基础已经进入代码、migration 和真实 Postgres 默认路径。它不关闭 PHASE20，也不声明 fixed benchmark、quality proven、PHASE21、PHASE22、22/22 completed 或 production ready。

已完成：

- 新增 `src/backend/zuno/platform/observability/eval_runtime.py`。
- 实现 immutable `EvalDatasetVersion`、`EvalCase` 和 case hash / dataset hash。
- 实现 `EvalRunConfig`，固定 dataset、corpus snapshot、index snapshot、model profile、judge policy、embedding profile、metric config、runtime profile 和 security scope hash。
- 实现 RAG Core Five：`CONTEXT_PRECISION`、`CONTEXT_RECALL`、`FAITHFULNESS`、`ANSWER_RELEVANCY`、`ANSWER_CORRECTNESS`。
- Core Five 明确区分 `MEASURED`、`BLOCKED`、`UNAVAILABLE`、`INVALID`；缺 reference、缺 context、invalid judge output 不会被转换为 0 分 PASS。
- 实现 `GraphRAGDiagnosticTrace`，能够定位 entity、relation、path、community、fusion、rerank 和 source grounding 的 evidence loss bucket。
- 实现 `AgentEfficiencyVector`，区分 estimated cost 与 settled cost，并计算 wasted work 与 parallel efficiency。
- 实现 `BenchmarkComparison`，dataset/snapshot/index/model/judge/embedding/metric/runtime/security scope 不可比时返回 `INCOMPARABLE`，partial profile 返回 `BLOCKED`。
- 实现 `ReleaseGateEvaluation`，绑定不可变 result set hash、comparison hash、evidence hash 和 gate hash。
- Release Gate 覆盖 `PASSED`、`FAILED`、`BLOCKED`、`INCOMPARABLE` 语义；critical slice regression 不能被总平均掩盖；settled cost 缺失时保持 `BLOCKED`。
- 新增 Alembic migration `20260729_53_phase20_observability_eval_runtime.py`。
- migration 新增 Eval Dataset / Case / Run / CaseExecution / MetricResult / GraphRAG Diagnostic / Agent Efficiency / Failure Bucket / Benchmark Comparison / Evidence Record / Release Gate tables。
- 新增 `PostgresEvalRuntimeRepository`，将 dataset、run、case execution、metric、diagnostic、efficiency、comparison、gate 和 evidence 写入 Postgres。

未完成：

- PHASE20 fault suite 尚未完整覆盖 Eval Worker Crash、resume、cancel、dataset mismatch、late revision 和 gate replay。
- Query API / report surface 尚未完成。
- 固定 benchmark 数据集运行和 production readiness 判定属于 PHASE22，不在本证据中声明。

## Verification

```text
python -m py_compile src/backend/zuno/platform/observability/eval_runtime.py src/backend/zuno/platform/observability/__init__.py tests/eval/test_phase20_observability_eval_runtime.py tests/integration/eval/test_phase20_observability_eval_persistence.py tests/repo/test_goal03_wave_b_migration_contract.py
pytest -q tests/eval/test_phase20_observability_eval_runtime.py tests/repo/test_goal03_wave_b_migration_contract.py -p no:cacheprovider
ZUNO_CONFIG=.local/config/zuno/config.local.yaml ZUNO_TEST_POSTGRES_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zuno_goal05_phase15?connect_timeout=5 pytest -q tests/integration/eval/test_phase20_observability_eval_persistence.py -p no:cacheprovider
python tools/scripts/verify_observability_eval_target_protocols.py
alembic -c infra/db/alembic.ini upgrade head
```

Result:

```text
14 passed
1 passed
observability/eval single-document target protocol verification passed
Running upgrade 20260728_52 -> 20260729_53, add phase20 observability eval runtime
```

## Closure Decision

PHASE20 remains `in_progress`. 本轮证据证明 Eval Runtime foundation 已进入真实代码、migration、unit test 和 Postgres integration；PHASE20 仍需 fault / recovery / query / report / closure evidence 后才能进入 completed。
