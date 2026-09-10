# Current Test Baseline

状态：`CURRENT / SELECTED_VERIFICATION_AVAILABLE / QUALITY_NOT_ESTABLISHED`

## 当前代码快照的 Selected Verification

当前 GitHub-native **selected code verification** 已经覆盖基础代码行为、真实 PostgreSQL Domain probes，以及 Wave-001 Domain revision 的真实 PostgreSQL DDL 可逆性。它绑定具体代码 commit、lockfile 依赖、测试集合、PostgreSQL service container 和 GitHub Actions run，可以作为这些被覆盖行为的 Current Evidence；它仍然不是 Full CI、完整 PostgreSQL integration、正式 benchmark 或 Production Qualification。

```text
verified_code_snapshot: c817bd345c9025524c6380ef208a131277d164bd
workflow: Current code selected verification
workflow_run: 34499552197
event: push / main
runner: ubuntu-24.04
python: 3.12.14
dependency_source: poetry.lock
postgresql_service: PostgreSQL 16.15 / healthy
selected_suite: 193 passed
compileall: PASS
model_gateway_strict_boundary: PASS
postgresql_domain_selected_probes: PASS
wave001_revision_postgresql_upgrade_downgrade_reupgrade: PASS
full_ci: NOT_RUN / NOT_ESTABLISHED
benchmark: BLOCKED_NOT_MEASURED
quality: NOT_YET_PROVEN
production_readiness: NOT_ESTABLISHED
artifact_id: 10161286870
```

GitHub run `34499552197` checkout 的就是 `c817bd345c9025524c6380ef208a131277d164bd`。Selected pytest 在该 SHA 上得到 `193 passed in 8.94s`。Workflow 使用 PostgreSQL 16.15 service，并通过 `ZUNO_TEST_DATABASE_URL` 让 Domain SQLAlchemy tests 和 Wave-001 revision probe 进入真实 PostgreSQL 路径。

当前 PostgreSQL Domain 证明包括四类严格限定的 shape：

- **commit 后调用方丢失响应**：D0→D1 已提交；新的 service instance 使用同一规范化输入与 idempotency identity 重放，只返回既有 committed result，不产生 D2；
- **两个请求同时基于 D0**：并发进入同一 Matter，最多一个提交 D1，另一个读取新 head 后返回 `VERSION_CONFLICT`；
- **commit 前故障**：已有 `before_commit` fault hook 抛错，事务不推进；新的 service instance 随后仍从 D0→D1 提交；
- **Wave-001 revision 真实 DDL 可逆性**：在独立随机 PostgreSQL schema 中执行 revision `20260813_57` 的现有 Alembic `upgrade()`，验证三张 Wave-001 表与 `uq_domain_mutation_idempotency` / `uq_domain_state_version`；随后执行 `downgrade()` 验证 revision 表被移除，再次 `upgrade()` 后重新验证同一表与约束。

最后一项只证明 **revision `20260813_57` 自身的 PostgreSQL DDL 可以 apply / downgrade / re-apply**。测试没有从最早 revision 顺序执行整个 Alembic history，也没有证明线上数据 backfill、锁影响、零停机迁移或生产回滚。因此不能把它写成“完整 migration chain 已验证”。

这些结果支持当前 `SqlAlchemyCanonicalDomainStore` 的 PostgreSQL transaction、row-lock / expected-version、idempotent replay baseline，以及 Wave-001 revision-level DDL 可逆性。它们**不等于 Target Formal Admission 已实现**。当前 `src/backend/zuno/domain/` 仍只有 Wave-001 mutation / persistence surface；Target `AdmissionReceipt`、完整 WorkProduct admission transaction 以及 Runtime 读取 matching Receipt 修复 Checkpoint 尚没有 Current implementation evidence。

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

这次 service container 不等于系统级 PostgreSQL qualification。Actions 日志仍能看到部分其他 selected tests / import-time platform components 尝试默认 `postgres` 用户并被数据库拒绝；这些路径没有被本次 Domain probes 声称为成功。Current 可采用的结论是 **显式 Domain PostgreSQL probes 与 Wave-001 revision probe PASS**，而不是“Zuno 全部 PostgreSQL 集成通过”。

当前仍未证明：

- 整条 Alembic history 的真实 PostgreSQL upgrade / downgrade；
- 真实业务数据的 backfill、约束收紧和在线迁移策略；
- Target AdmissionReceipt 与 Domain mutation 同事务提交；
- Domain commit 后 Runtime Checkpoint 丢失时的 owner-first E2E recovery；
- Checkpoint 已标完成但 matching Receipt 缺失时的 formal-complete denial；
- SecurityEpoch 变化、正式 WorkProduct invalidation 和新 Evidence / late proposal 的完整 02↔04 integration；
- Redis、RabbitMQ、Object Store、真实 Model / Tool Provider、外部 Host、HA / DR、负载和生产运维。

## 两类 GitHub Gate

当前仓库保留两类不同 GitHub gate：

- `Architecture document set`：验证 Project / Architecture / Modules / Governance / Evidence 文档集合、语义一致性、Human Readability、entrypoints 和对应 repository tests；
- `Current code selected verification`：验证 lockfile 可安装性、代码边界、runtime-batch contracts、selected behavior tests、当前 Domain PostgreSQL probes，以及 Wave-001 revision-level DDL probe。

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

`4736cf4409658e43af6e129e34dadbd97a5866ad` 的 run `34497460461` 恢复了 GitHub-native selected gate：`189 passed, 1 skipped`。`5b51627e43b6abcd940ac63100048171fd7f460c` 的 run `34498613045` 把真实 PostgreSQL Domain transaction / concurrency probes 接入后得到 `192 passed`。当前判断优先使用上面的 `c817bd3...` / run `34499552197`。

## 后续 Evidence Gate

**Slice B — Domain ↔ Runtime crash authority** 在“不修改业务实现”的验证范围已经走到边界：当前 mutation transaction / concurrency / lost-response replay 与 Wave-001 revision-level PostgreSQL DDL 已有 GitHub evidence。剩余最关键的 Owner-first recovery 依赖 Target `AdmissionReceipt`、Formal Admission transaction 和 Runtime matching-Receipt consumer；这些当前没有实现证明，不能继续用更多 mutation tests 代替。

下一阶段转入 [`../governance/module-detail-freeze-readiness-review.md`](../governance/module-detail-freeze-readiness-review.md) 的 **Slice C — Effects ↔ Security send boundary**，先判断现有代码能覆盖哪些 fault evidence；任何新增业务实现仍需独立明确的 Implementation Authorization。
