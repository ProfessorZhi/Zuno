# Current Test Baseline

状态：`CURRENT / SELECTED_VERIFICATION_AVAILABLE / QUALITY_NOT_ESTABLISHED`

## 当前 HEAD 的 Selected Verification

当前已经恢复一条 GitHub-native 的 **selected code verification**。它绑定具体 commit、lockfile 依赖、测试集合和 GitHub Actions run，可以作为当前代码中这些被覆盖行为的 Current Evidence；它仍然不是 Full CI、真实 PostgreSQL integration、正式 benchmark 或 Production Qualification。

```text
verified_head: 4736cf4409658e43af6e129e34dadbd97a5866ad
workflow: Current code selected verification
workflow_run: 34497460461
event: push / main
runner: ubuntu-24.04
python: 3.12.14
dependency_source: poetry.lock
selected_suite: 189 passed, 1 skipped, 1 warning
compileall: PASS
model_gateway_strict_boundary: PASS
postgresql_integration: BLOCKED / SKIPPED
full_ci: NOT_RUN / NOT_ESTABLISHED
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
```

GitHub run `34497460461` checkout 的就是 `4736cf4409658e43af6e129e34dadbd97a5866ad`，不是 PR synthetic merge ref。Selected pytest 在该 SHA 上得到 `189 passed, 1 skipped, 1 warning in 10.76s`；唯一已知 skip 来自 `tests/domain/test_domain_mutation_sqlalchemy.py` 中受 `ZUNO_TEST_DATABASE_URL` 控制的 PostgreSQL integration test。当前 workflow 没有配置真实 PostgreSQL service，因此不能把 SQLite / SQLAlchemy tests 或这条 skip 写成 PostgreSQL 已验证。

同一 run 还完成：

- `python -m compileall -q src/backend/zuno tests`；
- strict Model Gateway provider-SDK bypass scan；
- Model Gateway boundary verification；
- Knowledge runtime batch：`ARCH-KNOW-001..030`；
- Capability runtime batch：`ARCH-CAP-001..080`；
- Tool runtime batch：`ARCH-TOOL-001..080`；
- Model Gateway runtime batch：`ARCH-MODEL-001..088`；
- Security runtime batch：`ARCH-SEC-001..060`。

Selected behavior suite 覆盖 Domain mutation / idempotency、Citation provenance、Wave-001 migration contract、P0 recovery、Product Application boundary、Runtime plan / interrupt / restart / replan / tool idempotency / model roles、Knowledge / Capability / Tool / Security runtime contracts、Observability、Retrieval composition 与 Eval contract。具体文件集合由 [`.github/workflows/current-code-selected-verification.yml`](../../.github/workflows/current-code-selected-verification.yml) 固定。

这份证明的正确读法是：**上述 selected behavior 在 `4736cf4...` 的 GitHub runner 上通过。** 它不证明没有被 selected suite 覆盖的代码，也不证明真实 Redis / RabbitMQ / MinIO / Model Provider / 外围法院系统、HA / DR、负载、法院质量或生产运维已经通过。

## 当前仍未建立的验证

当前仓库保留两类不同 GitHub gate：

- `Architecture document set`：验证 Project / Architecture / Modules / Governance / Evidence 文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；
- `Current code selected verification`：验证 lockfile 可安装性、选定代码边界、runtime-batch contracts 与 selected behavior tests。

两者组合后仍不等于 Full Project CI。尤其以下内容继续保持未证明：

- 真实 PostgreSQL integration / race / migration apply-rollback；
- Redis、RabbitMQ、Object Store 等真实依赖的系统级故障测试；
- 外部 Model / Tool Provider 的 outage、timeout、billing、egress 和 reconciliation；
- 全项目 test suite、前端/浏览器、真实 Host E2E；
- 固定业务 Dataset benchmark、法院 QA、capacity、SLA、HA / DR 与 production qualification。

## 历史 selected verification

下面结果仍是有效的历史工程记录，但它绑定的是旧快照，不能覆盖当前 HEAD：

```text
historical_verified_head: 1ea56a5d61afa27ebda8f8745a6dbc6584796d05
repository_gates: PASS
canonical_runtime_tests: 67 passed
closure_documentation_tests: 23 passed
final_selected_suite: 90 passed
full_ci: NOT_RUN / NO_GITHUB_STATUS
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
```

当时的 selected checks 包括 Product Application / API layering、Agent Run runtime behavior、Retrieval composition、Multihop evaluator 和 compile。它们用于解释历史验证范围；当前判断优先使用上面的 `4736cf4...` GitHub run。

## 后续 Evidence Gate

下一道高价值验证不再是继续扩 selected unit-test 数量，而是补足 Module Detail Freeze 依赖的真实跨边界 evidence。优先级见 [`../governance/module-detail-freeze-readiness-review.md`](../governance/module-detail-freeze-readiness-review.md)：先进入 **Slice B — Domain ↔ Runtime crash authority**，其中真实 PostgreSQL transaction / concurrency 是当前最直接的 blocked 项之一。
