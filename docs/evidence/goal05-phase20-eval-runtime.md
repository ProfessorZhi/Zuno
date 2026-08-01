# Goal05 PHASE20 Eval Runtime Evidence

status: completed
date: 2026-07-29
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据证明 PHASE20 Observability Eval Runtime 已进入代码、migration、真实 Postgres 默认路径、API query surface、fault suite 和 closure 状态。它不声明 fixed production benchmark、quality proven、PHASE21、PHASE22、22/22 completed 或 production ready。

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
- 新增 Alembic migration `20260729_54_phase20_eval_query_scope.py`，为 eval run 增加 tenant/workspace query authorization scope。
- 新增 Alembic migration `20260729_55_phase20_release_gate_query_identity.py`，保证 `gate_id` 查询身份唯一。
- 新增 Eval Query / Report surface：`/api/v1/eval/runs/{eval_run_id}` 与 `/api/v1/eval/release-gates/{gate_id}`。
- Query API 返回 projection freshness、authorization scope、redaction status、trace completeness、measurement status、case/metric status counts、failure buckets、comparison/evidence hashes。
- 新增 fault suite 覆盖 worker crash partial attempt、recovered attempt、cancelled case、dataset/model mismatch、incomparable gate 和 gate replay hash stability。
- 新增 Alembic migration `20260729_56_phase20_eval_result_revisions.py`，保存 late trace / late eval 的 append-only result revision。
- EvidenceRecord 支持真实 artifact hash readback、expired evidence 和 hash mismatch 判定。
- FixedProfileReplayPlan 验证 standard/local/deep/agentic 等固定 profile replay 是否完整。
- Release Gate 覆盖 `ERROR` 状态，且不会折算为 PASS 或 FAILED。

边界：

- 固定 benchmark 数据集运行和 production readiness 判定属于 PHASE22，不在本证据中声明。

## Verification

```text
python -m py_compile src/backend/zuno/platform/observability/eval_runtime.py src/backend/zuno/platform/observability/__init__.py src/backend/zuno/api/services/product/projection_service.py src/backend/zuno/api/services/product/__init__.py src/backend/zuno/api/v1/observability.py tests/api/test_phase06_observability_query_route.py tests/api/test_phase06_observability_query_surface.py tests/eval/test_phase20_observability_eval_runtime.py tests/fault/eval/test_phase20_eval_fault_semantics.py tests/integration/eval/test_phase20_observability_eval_persistence.py tests/repo/test_goal03_wave_b_migration_contract.py
pytest -q tests/api/test_phase06_observability_query_route.py tests/api/test_phase06_observability_query_surface.py tests/eval/test_phase20_observability_eval_runtime.py tests/fault/eval/test_phase20_eval_fault_semantics.py tests/repo/test_goal03_wave_b_migration_contract.py -p no:cacheprovider
ZUNO_CONFIG=.local/config/zuno/config.local.yaml ZUNO_TEST_POSTGRES_URL=postgresql+psycopg://postgres:postgres@localhost:5432/zuno_goal05_phase15?connect_timeout=5 pytest -q tests/integration/eval/test_phase20_observability_eval_persistence.py -p no:cacheprovider
python tools/scripts/verify_observability_eval_target_protocols.py
alembic -c infra/db/alembic.ini upgrade head
alembic -c infra/db/alembic.ini current
```

Result:

```text
38 passed
1 passed
observability/eval single-document target protocol verification passed
alembic current: 20260729_56 (head)
```

## Closure Decision

PHASE20 completed. 本轮证据证明 Eval Runtime、Query / Report surface、fault semantics、late revision、expired evidence、artifact hash readback、fixed profile replay 和 release gate error state 已进入真实代码、migration、unit/fault/API test 和 Postgres integration。固定生产 benchmark、PHASE21 E2E/Fault/Cutover、PHASE22 closure 与 production readiness 不在本证据中声明。
