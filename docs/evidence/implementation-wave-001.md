# Implementation Evidence — Wave-001

status: `IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE`
scope: `TASK-001`、`TASK-003`
base_sha: `a402683f245e1e4b31c3b2c31b4d352eb9f9a23f`
production_readiness: `NOT_ESTABLISHED`

本文是从已完成的 `IMPLEMENTATION-EVIDENCE-CYCLE-001` Session 迁移出的唯一 Current Evidence
摘要。它证明有限的代码、测试和窄验证结果，不证明完整 Runtime、真实 PostgreSQL 生产行为、法院质量、
Provider 替换、微服务拆分或 Production Ready。原始 Session 只是施工材料，已不再由 Lab 保存。

## TASK-001：Canonical Domain Mutation / Version

| 架构主张 | 代码 / 测试 | 观察结果 | 已知缺口 |
| --- | --- | --- | --- |
| Domain Owner 是唯一 admission boundary | `src/backend/zuno/domain/mutation.py`、`persistence.py`；`tests/domain/test_domain_mutation.py` | 无 authorizer 或 Review-required proposal 不推进版本；没有公开 `write_fact` surface | 真实 API authorization policy 尚未接入 |
| expected DomainVersion 使用 CAS | `InMemoryCanonicalDomainStore`、`SqlAlchemyCanonicalDomainStore`；stale-version test | D0→D1 成功，过期 D0 返回 `VERSION_CONFLICT` | PostgreSQL race 尚未在真实环境执行 |
| 同一幂等输入不会产生第二次 Canonical Commit | mutation record、唯一 `(tenant,matter,idempotency_key)`；idempotency tests | 重试返回 `ALREADY_APPLIED`，同 key 不同输入返回 `REJECTED` | 真实队列 duplicate delivery 未运行 |
| 提交前故障不推进 DomainVersion | transaction hook / in-memory fault hook；fault test | 故障后版本仍为 D0，无 committed version | 进程崩溃注入未运行 |
| Domain State Version 与 mutation identity 同一事务 | `20260813_57_wave001_domain_mutation.py`；SQLAlchemy transaction test | 观察到 commit/conflict/replay 语义 | PostgreSQL migration apply/rollback 未在真实 DB 执行 |

## TASK-003：Citation Provenance Guard

| 架构主张 | 代码 / 测试 | 观察结果 | 已知缺口 |
| --- | --- | --- | --- |
| Citation 身份不依赖回答顺序 | `src/backend/zuno/knowledge/provenance.py`、`runtime/synthesis/citation_binding.py`；citation/runtime tests | Binder 按 Evidence/Claim/Lineage 查找，没有唯一关系时不绑定 | 多 Claim 真实模型输出仍需评测 |
| Claim→Evidence→SourceSpan→DocumentVersion 可确定验证 | `CitationProvenanceGuard.validate`；positive test | 正确身份返回 `PASS` | 真实 DB lineage lookup 未接入 |
| wrong-document / wrong-span / missing evidence 不能通过 | provenance guard；negative tests | 返回 `INVALID_PROVENANCE` 或 `UNSUPPORTED` | Cross-scope 仅完成 contract-level probe |
| stale / scope 不能静默替换 | stale/scope checks | 返回 `STALE` / `SCOPE_DENIED` | 当前生产 authorization provider 未资格认证 |
| rejection trace 不记录原文或隐藏推理 | `CitationValidationResult`、`CitationBinding`；metadata assertions | 只保留 Claim/Evidence/DocumentVersion/Span/failure/trace references | 全链路 trace sink 集成未运行 |

## Verification record

- Focused implementation/citation/runtime tests：`93 passed, 1 skipped`；
- Migration contract test：`tests/repo/test_wave001_domain_mutation_migration.py`，通过；
- Migration head：`20260813_57`；
- `compileall` 与 `git diff --check`：通过；
- Full CI：`FULL CI NOT RUN`；
- PostgreSQL integration：`BLOCKED / NOT_RUN`，SQLite transaction probe 不能替代 PostgreSQL evidence；
- Security：仅 contract-level authorization/scope/provenance checks，未达到 Security Qualified；
- Production readiness：仍为 `NOT_ESTABLISHED`。

TASK-001 的输入命名为 `proposal`，持久化为 `domain_state_versions.proposal_json`；本轮没有让
Model、Knowledge、Memory 或 Tool 直接写 Canonical Domain Table。TASK-003 的模型只产生 Citation
candidate，最终身份和 lineage 由 deterministic guard 验证。
