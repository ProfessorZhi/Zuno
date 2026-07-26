# Goal03 Wave A Knowledge Cutover Rollback Delete Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE12 的 Knowledge Cutover race、Rollback 和 Source deletion propagation 纵切：

- `KnowledgeRepository.cutover` 使用 `knowledge_cutover_decisions` 的 committed generation 做 CAS。
- stale `expected_generation` fail closed，不允许覆盖 active alias。
- rollback 可以把旧 `SUPERSEDED` KnowledgeVersion 重新切回 `ACTIVE`，并记录 `rollback_of_cutover_id`。
- strict Evidence 写入前必须存在 KnowledgeChunk lineage，且 SourceSpan 与 Authority 必须继承自 Chunk；SourceSpan 或 Authority mismatch fail closed。
- deleted SourceSpan 会 taint `knowledge_citation_lineage`，并把关联 evidence 从 `STRICT / SELECTED` 改为 rejected，不再返回 strict evidence。

## 默认调用链

```text
KnowledgeRepository.cutover
→ next_cutover_expected_generation
→ knowledge_cutover_decisions CAS
→ ACTIVE / SUPERSEDED version status update

KnowledgeRepository.mark_source_deleted
→ knowledge_chunks by document_version_id + source_span_ref
→ knowledge_evidence_records citation_eligibility = REJECTED
→ knowledge_citation_lineage deleted_or_tainted = true
→ strict_evidence_ids excludes tainted evidence

KnowledgeRepository.commit_evidence
→ knowledge_chunks by chunk_id
→ SourceSpan / Authority inheritance guard
→ knowledge_evidence_records STRICT / SELECTED insert
```

## 代码证据

- `src/backend/zuno/platform/database/knowledge/domain.py`
- `tests/integration/test_goal03_wave_a_persistence.py`

## 验证

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
7 passed
```

```powershell
python -m pytest -q tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_evidence_ledger.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py -p no:cacheprovider
```

结果：

```text
39 passed
```

## 边界

本证据证明 PHASE12 的 durable cutover CAS、rollback、strict evidence SourceSpan / Authority guard 和 deletion propagation 已进入 PostgreSQL repository 路径。

本证据不单独证明完整 PHASE12 completed；外部 BM25/Vector/Graph adapter 的真实可见性、完整 ACL/Temporal/Conflict 策略和端到端 Standard RAG 默认切流仍需 Closure Gate 汇总证明。
