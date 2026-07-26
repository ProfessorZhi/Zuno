# Goal03 Wave A Knowledge Durable Port Evidence

status: partial_runtime_evidence
phase: PHASE12
commit_scope: Agent Core Knowledge Port durable persistence repair

本文只证明本次 Wave A 修复切片：Agent Core 默认 `KnowledgeStepExecutor` 调用的 Knowledge runtime 可以通过 durable port，把检索结果中的严格 EvidenceLedger 记录提交为 Knowledge Owner 的 QueryRun、RetrievalRound、EvidenceRecord 与 CitationLineage 事实。

## 已证明

- `CorrectiveRetrievalRequest` 携带 `tenant_id`、`snapshot_id`、`agent_core_decision_ref` 和 `authorization_ref`。
- `EvidenceLedgerRecord` 保留 `chunk_id`，避免从 retrieval item 到 durable evidence 时丢失 Chunk lineage。
- 新增 `DurableKnowledgeRetrievalPort`，包装 `CorrectiveAgenticRetrievalRuntime`。
- `DurableKnowledgeRetrievalPort` 只提交具备 `chunk_id`、`document_version`、`SourceSpan` 且允许 strict citation 的 evidence。
- Repository 新增 `commit_citation_lineage`，把 Evidence 绑定到 `knowledge_citation_lineage`。
- `RuntimeDependencyFactory.for_completion(...)` 和 `RuntimeDependencyFactory.for_workspace_task(...)` 默认返回 durable Knowledge port，而不是缺失依赖或裸 corrective runtime。
- 默认 completion factory 的 retrieval step 已证明进入 `DurableKnowledgeRetrievalPort`；无 knowledge scope 时返回 `durable_knowledge_port.status = skipped / reason = knowledge_scope_empty`，不再产生 `missing_knowledge_runtime`，也不冒充检索成功。
- `KnowledgeStepExecutor` 把 snapshot、Agent Core decision 和 authorization ref 传入 Knowledge port，并在 observation metadata 暴露 durable persistence trace。
- `zuno.knowledge.ingestion` 包入口改为 contracts eager import + legacy symbols lazy export，避免 Agent Core Knowledge surface 导入时连带加载数据库 runtime 模块。
- `zuno.knowledge.agentic_graphrag` 与 `zuno.knowledge.indexing.runtime` 改为从 contracts/router 子模块读取轻量契约，不再依赖 ingestion 包入口的重导出。

## 已运行验证

```powershell
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_runtime_dependency_factory_builds_completion_dependencies tests/agent/runtime/test_runtime_dependency_factory.py::test_runtime_dependency_factory_builds_workspace_knowledge_runtime tests/agent/runtime/test_runtime_dependency_factory.py::test_completion_factory_knowledge_step_uses_durable_port_not_missing_dependency -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_missing_runtime_dependencies_return_blocked_observations -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/agentic src/backend/zuno/agent/runtime src/backend/zuno/platform/database/knowledge
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
python -m pytest -q tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_dependency_factory.py::test_runtime_dependency_factory_builds_workspace_knowledge_runtime -p no:cacheprovider
python -m pytest -q tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_ingestion_snapshot_handoff.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
4 passed
3 passed
1 passed
4 passed
5 passed
46 passed
4 passed
6 passed
Repository structure verification passed.
Doc boundary verification passed.
```

## 历史失败指纹

以下 runtime start 超时已由后续 `docs/evidence/goal03-wave-a-runtime-default-completion-fast-fail.md` 的修复与当前 `tests/agent/runtime/test_runtime_dependency_factory.py` 结果覆盖：

```text
command: python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_unified_runtime_service_can_start_from_factory_assembly -p no:cacheprovider
test name: test_unified_runtime_service_can_start_from_factory_assembly
exception type: command timeout
first relevant scope: UnifiedAgentRuntimeService.start from factory completion assembly
environment signature: local focused test process timed out after 124s; no PostgreSQL service on localhost:5432
retry count: 1
```

以下 PostgreSQL / Docker unavailable 记录只保留为历史环境指纹，已由 `docs/evidence/goal03-wave-a-postgres-integration-recovery.md` 的当前运行结果覆盖：

```text
command: python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
test name: migrated_postgres fixture
exception type: sqlalchemy.exc.OperationalError / psycopg.errors.ConnectionTimeout
environment signature: localhost:5432 unavailable; Docker daemon unavailable
retry count: 1
```

旧结论中记录的 Knowledge surface heavy import 失败已在本切片修复。当前 `tests/agent/test_knowledge_layer_surfaces.py` 已通过；该结果只证明导入边界恢复为轻量，不证明 PHASE12 Gate 完成。

## 未证明

- BM25/Vector adapter 的真实服务端索引可见性、ACL/Temporal/Conflict、cutover rollback 和 deletion propagation 尚未完成。
- PHASE12 仍是 `in_progress`，不能据此关闭 Wave A Gate。
