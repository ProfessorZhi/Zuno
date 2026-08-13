# Implementation Evidence Record

BASE_SHA：`a402683f245e1e4b31c3b2c31b4d352eb9f9a23f`

## TASK-001 — Canonical Domain Mutation / Version

| Architecture Claim | Code Location | Test Location | Observed Result | Evidence Level | Known Gap |
|---|---|---|---|---|---|
| Domain Owner 是唯一 admission boundary | `src/backend/zuno/domain/mutation.py`、`persistence.py` | `tests/domain/test_domain_mutation.py::test_missing_authorizer_and_review_gate_cannot_commit` | 无 authorizer、Review-required proposal 均不推进版本；没有 `write_fact` surface | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 尚未接入真实 API authorization policy |
| expected DomainVersion 采用 CAS，不能静默覆盖 | `InMemoryCanonicalDomainStore`、`SqlAlchemyCanonicalDomainStore` | `test_stale_expected_version_is_typed_conflict_without_overwrite`、SQLAlchemy integration test | D0→D1 成功；过期 D0 返回 `VERSION_CONFLICT` | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | PostgreSQL race 尚未在真实环境执行 |
| 同一幂等输入不会产生第二次 Canonical Commit | mutation records、unique `(tenant,matter,idempotency_key)` | `test_same_key_same_input_replays_one_commit_and_different_input_rejects`、`test_retry_after_lost_response_finds_the_committed_result` | 重试返回 `ALREADY_APPLIED`；同 key 不同输入返回 `REJECTED` | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 真实队列 duplicate delivery 未运行 |
| 提交前故障不会推进 DomainVersion | SQL transaction hook / in-memory fault hook | `test_fault_before_transaction_commit_does_not_advance_domain_version` | 故障后版本仍为 D0、无 committed version | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 进程崩溃注入未运行 |
| Domain State Version 与 mutation identity 同一事务 | `20260813_57_wave001_domain_mutation.py`、SQLAlchemy store | `test_sqlalchemy_store_exercises_transactional_version_and_replay_semantics` | SQLite transaction probe 观察到 commit/conflict/replay 语义 | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | PostgreSQL migration apply/rollback 未在真实 DB 执行 |

## TASK-003 — Citation Provenance Guard

| Architecture Claim | Code Location | Test Location | Observed Result | Evidence Level | Known Gap |
|---|---|---|---|---|---|
| Citation 身份不依赖回答顺序 | `src/backend/zuno/knowledge/provenance.py`、`runtime/synthesis/citation_binding.py` | `tests/knowledge/test_citation_provenance.py`、`tests/agent/runtime/test_runtime_grounded_synthesis.py` | Binder 按 Evidence/Claim/Lineage 查找；没有唯一关系时不绑定 | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 多 Claim 真实模型输出仍需评测 |
| Claim→Evidence→SourceSpan→DocumentVersion 可确定验证 | `CitationProvenanceGuard.validate` | correct document/span positive test | 正确身份返回 `PASS` | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 真实 DB lineage lookup 未接入 |
| wrong-document / wrong-span / missing evidence 不能通过 | 同上 | `test_wrong_document_version_is_rejected`、`test_correct_document_with_wrong_span_is_rejected`、`test_missing_evidence_is_unsupported`、Q039 assertion | 分别返回 typed `INVALID_PROVENANCE` 或 `UNSUPPORTED` | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | Cross-scope 仅完成 contract-level probe |
| stale / scope 不能静默替换 | guard stale/scope checks | `test_stale_evidence_and_cross_scope_are_not_silently_rewritten` | 返回 `STALE` / `SCOPE_DENIED` | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 当前生产 authorization provider 未资格认证 |
| rejection trace 不记录原文或隐藏推理 | `CitationValidationResult`、`CitationBinding` | binding metadata assertions and code review | 结果只带 Claim/Evidence/DocumentVersion/Span/failure/trace references | IMPLEMENTATION_AVAILABLE / VERIFICATION_AVAILABLE | 全链路 trace sink 集成未运行 |

## Provider/Model ownership conformance

TASK-001 的输入命名为 `proposal`，持久化为 `domain_state_versions.proposal_json`；本轮没有 Model、Knowledge、Memory 或 Tool 直接写 Canonical Domain Table 的 public API。TASK-003 的模型只产生候选 Citation，最终是否有效由 deterministic guard 决定。
