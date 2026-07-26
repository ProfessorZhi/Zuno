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
- `RuntimeDependencyFactory.for_workspace_task(...)` 默认返回 durable Knowledge port，而不是裸 corrective runtime。
- `KnowledgeStepExecutor` 把 snapshot、Agent Core decision 和 authorization ref 传入 Knowledge port，并在 observation metadata 暴露 durable persistence trace。

## 已运行验证

```powershell
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_runtime_dependency_factory_builds_completion_dependencies tests/agent/runtime/test_runtime_dependency_factory.py::test_runtime_dependency_factory_builds_workspace_knowledge_runtime -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_missing_runtime_dependencies_return_blocked_observations -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/agentic src/backend/zuno/agent/runtime src/backend/zuno/platform/database/knowledge
git diff --check
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
```

结果：

```text
4 passed
2 passed
1 passed
Repository structure verification passed.
Doc boundary verification passed.
```

## 未完成验证

`python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider` 曾超时。拆分后，新增 Knowledge durable port 和 factory dependency 相关用例均通过；超时点定位为既有完整 runtime start 用例：

```text
command: python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_unified_runtime_service_can_start_from_factory_assembly -p no:cacheprovider
test name: test_unified_runtime_service_can_start_from_factory_assembly
exception type: command timeout
first relevant scope: UnifiedAgentRuntimeService.start from factory completion assembly
environment signature: local focused test process timed out after 124s; no PostgreSQL service on localhost:5432
retry count: 1
```

`python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider` 仍未重跑，因为本机 PostgreSQL 5432 不可用，且 Docker daemon 不可用。

`python -m pytest -q tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider` 未通过，失败点是既有 `zuno.knowledge.agentic_graphrag` surface 会加载 `zuno.database` 模块族：

```text
command: python -m pytest -q tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
test name: test_importing_knowledge_surfaces_does_not_load_heavy_runtime_modules
exception type: AssertionError
first relevant assertion: tests/agent/test_knowledge_layer_surfaces.py:229
environment signature: clean subprocess importing EXPECTED_EXPORTS; zuno.knowledge.agentic_graphrag loads zuno.database.*
retry count: 1
```

## 未证明

- PostgreSQL integration 尚未证明 durable port 真实写入 `knowledge_query_runs`、`knowledge_retrieval_rounds`、`knowledge_evidence_records` 和 `knowledge_citation_lineage`。
- BM25/Vector adapter 的真实服务端索引可见性、ACL/Temporal/Conflict、cutover rollback 和 deletion propagation 尚未完成。
- PHASE12 仍是 `in_progress`，不能据此关闭 Wave A Gate。
