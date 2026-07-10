# PHASE02 Source Span Provenance Contract

program: zuno-evidence-span-agentic-graphrag-hardening-v1
phase: PHASE02_source-span-provenance-contract
status: completed
owner: Ingestion / Knowledge

## 目标

冻结 evidence-span citation 必需的 provenance contract，保证检索结果能从 chunk 回到原始 source span。

## 范围

必须覆盖字段：

- `document_id`
- `source_object_id`
- `document_version_id`
- `page_number`
- `section_path`
- `block_id`
- `chunk_id`
- `char_start`
- `char_end`
- `normalized_text`
- `raw_text`
- `parent_chunk_id`
- `neighbor_chunk_ids`
- `source_uri`
- `file_name`
- `content_hash`
- `parser_name`
- `parser_version`

## 禁止范围

- 不接 external graph DB。
- 不接 external vector DB。
- 不把 OCR / VLM 标为 Current。

## 验收闸门

- [x] IR / chunk / eval fixtures 中 provenance 字段不丢失。
- [x] retrieval result 能回到 source block 或 source span。
- [x] 缺失字段时保留 `null`，不 fake page/span。

## 完成事实

PHASE02 已完成 source span provenance contract 的本地 runtime 链路，不表示 PHASE03 citation-sized chunking 或 PHASE07 claim-level citation binding 已完成。

Current 已冻结并贯通字段：

- `document_id`
- `source_object_id`
- `document_version_id`
- `page_number`
- `section_path`
- `block_id`
- `chunk_id`
- `char_start`
- `char_end`
- `normalized_text`
- `raw_text`
- `parent_chunk_id`
- `neighbor_chunk_ids`
- `source_uri`
- `file_name`
- `content_hash`
- `parser_name`
- `parser_version`

贯通路径：

```text
CanonicalDocumentIR / DocumentBlock / SourceSpan
-> build_source_span_provenance()
-> IndexHandoffPayload chunks / bm25 / vector / graphrag / evidence / citation
-> KnowledgeIndexRuntime retrieval metadata / citation_lineage
-> AgenticRetrievalRuntime EvidenceItem / Citation / trace payload
-> GraphRAGIndexPipelineContract text_units
```

Legacy 边界：

- 旧 fixture 缺少真实 page 或 char offset 时，`page_number`、`char_start` 和 `char_end` 保持 `null`。
- `normalized_text` 和 `raw_text` 来自当前 block text，不从 gold answer 或 eval label 推导。

## 验证命令

```powershell
pytest -q tests/knowledge tests/evals/test_enterprise_rag_paired_benchmark.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/ingestion/contracts.py`
- `src/backend/zuno/knowledge/agentic_graphrag.py`
- `tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py`

## 需要修改的文件

预计修改范围：

- `src/backend/zuno/knowledge/**`
- `tools/evals/zuno/rag_eval/**`
- `tests/knowledge/**`
- `tests/evals/**`

## 执行拆解

1. 审计当前 source id / chunk id / citation lineage 字段。
2. 明确缺口和向后兼容策略。
3. 补齐 fixtures 和 contract tests。
4. 更新 owner note。

## 多 agent 分工

可拆成 ingestion provenance audit 和 eval fixture audit，但共享 contract 由主线程收口。

## 需要返回的证据

- provenance 字段流转路径。
- 新增或更新的 focused tests。
- 仍属于 Target 的外部依赖。

## 停止条件

只有 source span 字段在 runtime/eval 路径可复现流转后才能关闭。
