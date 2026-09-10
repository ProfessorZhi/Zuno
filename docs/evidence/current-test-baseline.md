# Current Test Baseline

状态：`CURRENT / SELECTED_VERIFICATION_AVAILABLE / QUALITY_NOT_ESTABLISHED`

## 当前代码快照的 Selected Verification

当前 GitHub-native **selected code verification** 已经同时覆盖基础代码行为和一组真实 PostgreSQL Domain probes。它绑定具体代码 commit、lockfile 依赖、测试集合、PostgreSQL service container 和 GitHub Actions run，可以作为这些被覆盖行为的 Current Evidence；它仍然不是 Full CI、完整 PostgreSQL integration、正式 benchmark 或 Production Qualification。

```text
verified_code_snapshot: 5b51627e43b6abcd940ac63100048171fd7f460c
workflow: Current code selected verification
workflow_run: 34498613045
event: push / main
runner: ubuntu-24.04
python: 3.12.14
dependency_source: poetry.lock
postgresql_service: PostgreSQL 16.15 / healthy
selected_suite: 192 passed
compileall: PASS
model_gateway_strict_boundary: PASS
postgresql_domain_selected_probes: PASS
full_ci: NOT_RUN / NOT_ESTABLISHED
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
artifact_id: 10160905211
```

GitHub run `34498613045` checkout 的就是 `5b51627e43b6abcd940ac63100048171fd7f460c`。Selected pytest 在该 SHA 上得到 `192 passed in 17.78s`，没有 PostgreSQL skip。Workflow 启动 PostgreSQL 16 service，并通过 `ZUNO_TEST_DATABASE_URL` 让 Domain SQLAlchemy tests 进入真实 PostgreSQL 路径。

本次 PostgreSQL 证明严格限定为当前 Domain mutation/version surface 的三个 failure / concurrency shape：

- **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入与 idempotency identity 重放，只返回既有 committed result，不产生 D2；
- **两个请求同时基于 D0**：并发进入同一 Matter，最多一个提交 D1，另一个读取新 head 后返回 `VERSION_CONFLICT`；
- **commit 前故障**：在已有 `before_commit` fault hook 中抛错，事务不推进；新的 service instance 随后仍从 D0→D1 提交。

这些结果支持当前 `SqlAlchemyCanonicalDomainStore` 的 PostgreSQL transaction、row-lock / expected-version 和 idempotent replay baseline。它们**不等于 Target Formal Admission 已实现**。当前 `src/backend/zuno/domain/` 仍只有 Wave-001 mutation / persistence surface；Target `AdmissionReceipt`、完整 WorkProduct admission transaction 以及 Runtime 读取 matching Receipt 修复 Checkpoint 尚没有 Current implementation evidence。

同一 run 还完成：

- `python -m compileall -q src/backend/zuno tests`；
- strict Model Gateway provider-SDK bypass scan；
- Model Gateway boundary verification；
- Knowledge runtime batch：`ARCH-KNOW-001..030`；
- Capability runtime batch：`ARCH-CAP-001..080`；
- Tool runtime batch：`ARCH-TOOL-001..080`；
- Model Gateway runtime batch：`ARCH-MODEL-001..088`；
- Security runtime batch：`ARCH-SEC-001..060`；
- selected behavior suite across Domain mutation / Citation provenance / Product Application / Runtime / Knowledge / Capability / Tool / Security / Observability / Retrieval / Eval contracts。

具体文件集合由 [`.github/workflows/current-code-selected-verification.yml`](../../.github/workflows/current-code-selected-verification.yml) 固定。

### PostgreSQL 证据的边界

这次 service container 不等于系统级 PostgreSQL qualification。Actions 日志里仍能看到部分其他 selected tests / import-time platform components 尝试默认 `postgres` 用户并被数据库拒绝；这些路径没有被本次 Domain probe 声称为成功。Current 可采用的结论是 **Domain selected PostgreSQL probes PASS**，而不是“Zuno 全部 PostgreSQL 集成通过”。

当前仍未证明：

- Wave-001 Alembic migration 在真实 PostgreSQL 上的完整 upgrade / downgrade / rollback；
- Target AdmissionReceipt 与 Domain mutation 同事务提交；
- Domain commit 后 Runtime Checkpoint 丢失时的 owner-first E2E recovery；
- Checkpoint 已标完成但 matching Receipt 缺失时的 formal-complete denial；
- SecurityEpoch 变化、正式 WorkProduct invalidation 和新 Evidence / late proposal 的完整 02↔04 integration；
- Redis、RabbitMQ、Object Store、真实 Model / Tool Provider、外部 Host、HA / DR、负载和生产运维。

## 两类 GitHub Gate

当前仓库保留两类不同 GitHub gate：

- `Architecture document set`：验证 Project / Architecture / Modules / Governance / Evidence 文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；
- `Current code selected verification`：验证 lockfile 可安装性、代码边界、runtime-batch contracts、selected behavior tests，以及当前这组 PostgreSQL Domain probes。

两者组合后仍不等于 Full Project CI。Formal benchmark 继续 `BLOCKED_NOT_MEASURED`，法院 QA、capacity、SLA、HA / DR 与 Production Readiness 仍未建立。

## 历史 selected verification

历史记录继续保留，但不覆盖当前代码：

```text
historical_verified_head: 1ea56a5d61afa27ebda8f8745a6dbc6584796d05
final_selected_suite: 90 passed
full_ci: NOT_RUN / NO_GITHUB_STATUS
benchmark: BLOCKED_NOT_MEASURED
production_readiness: NOT_ESTABLISHED
```

`4736cf4409658e43af6e129e34dadbd97a5866ad` 的 run `34497460461` 是恢复 GitHub-native selected gate 的上一份快照：`189 passed, 1 skipped`，其中 PostgreSQL 因未配置 URL 被 skip。当前判断优先使用上面的 `5b51627...` / run `34498613045`。

## 后续 Evidence Gate

Module Detail Freeze 的下一道高价值验证仍是 **Slice B — Domain ↔ Runtime crash authority**。数据库基本 transaction / concurrency baseline 已经前进，但跨 Owner recovery 被一个更明确的 Implementation Gap 阻断：Target `AdmissionReceipt` 当前没有实现证明。任何为了补这个对象、事务或 Runtime consumer 而修改业务代码的工作，都需要独立明确的 Implementation Authorization。
