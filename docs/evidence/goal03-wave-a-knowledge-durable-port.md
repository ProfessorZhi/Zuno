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
- `CorrectiveRetrievalRequest` 与 `KnowledgeStepExecutor` 无显式 plan / strategy 时的默认 retrieval profile 已改为 `standard`；测试证明 Agent Core 默认请求和 durable query run payload 都不再回落到 `deep`。
- `KnowledgeIndexRuntime` 的 current local BM25 / vector / graph adapter 会在 `IndexJobManifest.adapter_visibility_receipts` 写入 per-target visibility receipt；receipt 现在必须通过 sample retrieval verification 才能标记 `visibility = visible`，否则 target 进入 `degraded`，retrieval payload 不把它纳入 `retrievers_used`。
- `KnowledgeIndexRuntime.index_document(...)` 现在通过 target 对应的 configured adapter binding 执行 index dispatch，并在 `IndexJobManifest.adapter_dispatch_receipts` 写入 adapter_id、operation、dispatch_ref、payload_hash 与 indexed_document_count；测试覆盖自定义 adapter binding 被真实调用后才产生 visibility receipt。
- 新增 `ExternalServiceIndexAdapterBinding` 与 `external_adapter_bindings(...)` expand 层；外部 adapter dispatch 后必须通过 adapter 自身 `search_documents` / `search` / `query` readback 才能写入 `visible`，且 adapter contract 需为 `current` 才能进入默认 retrieval payload。readback 无匹配时 target 降级且不进入 retrieval payload。
- Elasticsearch BM25 与 Neo4j Graph 外部 adapter 已通过容器化服务 readback integration，`INDEX_ADAPTER_CONTRACTS` 中对应 contract 为 `current`。
- 新增 `MilvusVectorIndexClient`，具备惰性 `pymilvus` 连接、确定性 vector 写入、collection index 和 search readback contract；已通过容器化 Milvus service readback integration，并在 `INDEX_ADAPTER_CONTRACTS` 中标为 `current`。
- `KnowledgeRepository.record_index_visibility(...)` 现在对 index build job 的 duplicate same batch 做幂等返回，对相同 job 不同 batch、相同 target/fencing/attempt 不同 write batch、低 fencing stale worker visibility commit 做 fail-closed；更高 fencing 的恢复尝试可提交新的 visibility 事实。
- 外部 Elasticsearch BM25、Milvus Vector、Neo4j Graph adapter contract 均已有容器化 service readback 证据并标为 `current`。
- 默认 `AgenticRetrievalRuntime.answer(...)` 在把检索候选升级为 `EvidenceBundle`、`Citation` 和回答前，会按 allowed ACL、temporal valid_from / valid_until 与 unresolved conflict policy 丢弃证据，并在 task event / trace metadata 写入 `dropped_evidence_reasons`。
- `KnowledgeStepExecutor` 把 snapshot、Agent Core decision 和 authorization ref 传入 Knowledge port，并在 observation metadata 暴露 durable persistence trace。
- `DurableKnowledgeRetrievalPort` 对 Knowledge Repository 写入失败 fail closed：retrieval runtime 的 evidence 不会被冒充为 durable success；trace 写入 `durable_knowledge_port.status = blocked`、failure type 和 reason。
- `KnowledgeStepExecutor` 看到 durable persistence blocked 时返回 BLOCKED observation，`failure_reason = durable_knowledge_persistence_failed`；无 knowledge scope 的 skipped 语义保持 skipped，不回退成 missing dependency。
- 有 knowledge scope 但没有 ACTIVE Knowledge Snapshot 时，`DurableKnowledgeRetrievalPort` 返回 `blocked / active_snapshot_unavailable`，`KnowledgeStepExecutor` 返回 `failure_reason = active_knowledge_snapshot_unavailable`；只有无 knowledge scope 才允许 skipped。
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
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/agent/test_agentic_retrieval_runtime.py::test_agentic_retrieval_runtime_drops_temporal_and_conflicted_evidence_before_citation -p no:cacheprovider
python -m pytest -q tests/agent/test_agentic_retrieval_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/test_agentic_graphrag_contract.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py::test_index_manifest_tracks_document_ir_provenance_acl_and_adapter_status tests/knowledge/test_index_jobs_runtime.py::test_index_runtime_invokes_configured_adapter_bindings -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase12_knowledge_index_visibility_rejects_stale_fencing_and_conflicting_batches -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_dependency_factory.py::test_completion_factory_knowledge_step_uses_durable_port_not_missing_dependency tests/agent/runtime/test_runtime_dependency_factory.py::test_missing_runtime_dependencies_return_blocked_observations -p no:cacheprovider
python -m pytest -q tests/knowledge/test_corrective_retrieval_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/api/test_knowledge_api_contract.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/agentic/durable.py src/backend/zuno/agent/runtime/execution/knowledge_step.py tests/knowledge/test_corrective_retrieval_runtime.py
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/indexing tests/knowledge/test_index_jobs_runtime.py
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
docker compose -f infra/docker/docker-compose.yml up -d neo4j etcd
docker compose -f infra/docker/docker-compose.yml up -d elasticsearch
python -m pytest -q tests/integration/test_goal03_wave_a_external_index_adapters.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/indexing tests/integration/test_goal03_wave_a_external_index_adapters.py
python -m pytest -q tests/integration/test_goal03_wave_a_external_index_adapters.py tests/knowledge/test_index_jobs_runtime.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
docker pull milvusdb/milvus:v2.4.15
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/indexing tests/knowledge/test_index_jobs_runtime.py
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
docker pull mirror.gcr.io/milvusdb/milvus:v2.4.15
docker compose -f infra/docker/docker-compose.yml up -d milvus
python -m pytest -q tests/integration/test_goal03_wave_a_external_index_adapters.py::test_phase12_milvus_vector_adapter_requires_real_service_readback -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_external_index_adapters.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/indexing tests/integration/test_goal03_wave_a_external_index_adapters.py
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/agent/runtime/test_runtime_dependency_factory.py tests/integration/test_goal03_wave_a_external_index_adapters.py -p no:cacheprovider
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
23 passed
1 passed
9 passed
7 passed
2 passed
13 passed
1 passed
12 passed
5 passed
14 passed
8 passed
7 passed
6 passed
24 passed
13 passed
compileall passed
16 passed
compileall passed
49 passed
zuno-neo4j healthy
zuno-etcd healthy
zuno-elasticsearch healthy
2 passed
20 passed
compileall passed
22 passed
49 passed
Milvus direct image pull stalled on layer de4351a735f5 without progress; the process was stopped and the image is not available.
21 passed
compileall passed
50 passed
Milvus mirror.gcr.io image pull also stalled on layer de4351a735f5 without progress; the process was stopped and the image is not available.
zuno-milvus healthy
1 passed
3 passed
21 passed
compileall passed
53 passed
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

- 完整 PHASE12 是否 completed 由 `docs/evidence/goal03-wave-a-gate-review.md` 汇总判定；本证据提供 Knowledge durable port、configured adapter dispatch、service readback、visibility 和 default Knowledge port 相关证明。
- Production readiness 仍未建立；本证据不证明 PHASE20/22 fixed benchmark、quality gate 或生产运维就绪。
