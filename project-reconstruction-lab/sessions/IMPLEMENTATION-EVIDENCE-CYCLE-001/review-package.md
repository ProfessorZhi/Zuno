# ChatGPT Review Package — IMPLEMENTATION-EVIDENCE-CYCLE-001

- BASE_SHA：`a402683f245e1e4b31c3b2c31b4d352eb9f9a23f`
- FINAL_SHA：`recorded in final handoff`
- Wave：`001`
- Tasks：`TASK-001`、`TASK-003`

## Scope and preserved constraints

- Round-005 原始 Questions/Answers/Scores/Decisions/Architecture Delta/Scorecard：未修改；
- RB-CLOSURE-SEMANTIC-AUDIT-V3.1.3.1：保留；
- Domain Owner 才能提交 Canonical Domain State：保留；
- PostgreSQL Domain State 与 Runtime Checkpoint 分离：保留；
- PlanVersion immutable、Retry/Replan 分离、Citation provenance contract：保留；
- 未实现 Multi-Agent、Tool Runtime、Provider replacement、微服务拆分、Kafka、Event Sourcing、2PC、Saga；
- Facts：`NONE`；ADR：`NONE`；Canonical Part A：未修改。

## TASK-001

- 实现文件：`src/backend/zuno/domain/mutation.py`、`src/backend/zuno/domain/persistence.py`、`src/backend/zuno/domain/__init__.py`；
- Migration：`infra/db/alembic/versions/20260813_57_wave001_domain_mutation.py`，head 为 `20260813_57`，包含 aggregate head、mutation identity/result、state version 三类表；
- 覆盖：CAS version conflict、transactional version advance、idempotency replay、same-key different-input rejection、Review gate、authorization boundary、pre-commit fault、concurrent in-memory race；
- 测试：`tests/domain/test_domain_mutation.py`、`tests/domain/test_domain_mutation_sqlalchemy.py`；
- Concurrency：两条 expected D0 mutation 观察到一条 `COMMITTED`、一条 `VERSION_CONFLICT`；
- Idempotency：同语义 retry 返回 `ALREADY_APPLIED`，不新增 DomainVersion；
- Fault injection：提交前 exception 已执行；response loss 通过 committed 后 retry 模拟；process restart/queue replay 未执行。

## TASK-003

- 实现文件：`src/backend/zuno/knowledge/provenance.py`、`src/backend/zuno/agent/runtime/synthesis/citation_binding.py`、`claims.py`、`grounded_answer.py`、`knowledge_step.py`、finalization binding fields；
- 正例：correct DocumentVersion + SourceSpan 返回 `PASS`；
- 负例：wrong DocumentVersion、wrong SourceSpan、missing Evidence、claim relation missing、stale Evidence、cross-scope 均 reject；
- 原 Q039 wrong-span XFAIL 已转为真实断言；
- Current XFAIL changed：Q039 wrong-span no longer XFAIL；其余原始 P0 不因本 Wave 自动关闭；
- Model 只能提出 Citation candidate；deterministic guard 负责身份和 lineage 验证；
- Citation rejection 只保留 references、failure class、reason 和 trace ref，不写原文或隐藏思维链。

## Verification

- Focused implementation/citation/runtime tests：`93 passed, 1 skipped`；
- Migration contract test：`tests/repo/test_wave001_domain_mutation_migration.py`，通过；
- Migration head：`20260813_57 (head)`；
- `compileall`：通过；
- `git diff --check`：通过；
- Architecture/Docs/Agent governance verifiers：通过；
- Full CI：`FULL CI NOT RUN`；
- PostgreSQL integration：`BLOCKED / NOT_RUN`，未配置 `ZUNO_TEST_DATABASE_URL`；SQLite transaction probe 已运行，但不能替代 PostgreSQL evidence；
- ruff/type check：未运行，当前环境没有 `ruff` 命令，未发现项目现有 type-check command；
- PDF E2E：未完成，仓库缺少既有 `tests/fixtures/documents/phase12_source_span.pdf` fixture。

## Security / Production / architecture status

- Security evidence：仅有 contract-level authorization/scope/provenance checks；未达到 Security Qualified；
- Architecture conflict：`NONE`；
- Runtime changed：仅 Citation binding / provenance guard 的窄路径；Planner、Multi-Agent、Tool Runtime 未改；
- Production readiness：仍为 `NOT_ESTABLISHED`；
- Round-006：`WAITING_FOR_WAVE_001_EVIDENCE_REVIEW`，不自动启动 100Q；
- Working tree：只保留原有未跟踪 `%USERPROFILE%/`，未纳入提交。
