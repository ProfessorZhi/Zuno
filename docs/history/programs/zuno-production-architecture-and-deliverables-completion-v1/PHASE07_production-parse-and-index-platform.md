# PHASE07 Production Parse and Index Platform

status: completed
previous_phase: PHASE06_product-surface-desktop-recovery-loop
completed_at: 2026-07-01
next_phase: PHASE08_durable-agent-runtime-persistence

## 目标

把文档解析与索引从本地 deterministic runtime 推进到生产 parser queue、深度抽取和外部索引 adapter。

## 范围

- Parser queue、job status、retry、metrics。
- Docling / MinerU / Unstructured adapter 可插拔边界。
- OCR、layout、table、code extraction。
- Elasticsearch / Milvus / Neo4j 或等价外部 adapter 边界。

## 禁止范围

- 不把未接通的外部服务写成 Current。
- 不破坏现有本地 deterministic fixtures。

## 验收闸门

- parser queue 和 index job 有本地可测实现或明确外部 blocked evidence。
- Document IR、chunk、provenance、ACL、manifest 可追踪。
- parser golden fixtures 覆盖主要格式。

## 验证命令

```powershell
git diff --check
pytest -q tests/knowledge tests/api/test_knowledge_api_contract.py tests/retrieval -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```

## 需要先读取

- `src/backend/zuno/knowledge/ingestion/README.md`
- `src/backend/zuno/knowledge/indexing/README.md`
- `src/backend/zuno/knowledge/ingestion/**`
- `src/backend/zuno/knowledge/indexing/**`
- `src/backend/zuno/platform/services/convert_files/**`
- `src/backend/zuno/platform/services/pipeline/**`
- `docs/architecture/production-readiness.md`

## 需要修改的文件

- `src/backend/zuno/knowledge/ingestion/**`
- `src/backend/zuno/knowledge/indexing/**`
- parser adapter / queue / job status modules
- index adapter / manifest / retry / replay modules
- `tests/knowledge/**`
- `tests/api/test_knowledge_api_contract.py`
- `tests/retrieval/**`

## 执行拆解

1. 设计 parser queue contract：job id、status、retry、metrics、failure reason、source provenance。
2. 接入或封装 Docling / MinerU / Unstructured adapter 边界，提供 local fallback。
3. 扩展 Document IR：OCR、layout、table、code block、ACL、provenance。
4. 设计 index adapter：BM25、vector、graph，本地实现和外部 service adapter 分离。
5. 为外部 Elasticsearch / Milvus / Neo4j 标记 Current / Target，未接通不得写成 Current。

## 多 agent 分工

- Thread A：parser queue / Document IR。
- Thread B：adapter registry / parser golden fixtures。
- Thread C：index job / manifest / retry / replay。
- Thread D：retrieval contract tests。
- 主线程：确认 parse -> index -> retrieval evidence 链路。

## 需要返回的证据

- parser capability matrix。
- parser queue/job 状态样例。
- Document IR fixture。
- index manifest 和 retrieval payload。
- external adapter blocked/current 边界。

## 完成证据

- Parser adapter boundary：`ParserAdapterContract` 区分 `current_runtime = deterministic_local`、`production_target` 和 `external_dependency_status`；`native` 是 Current，Docling / PyMuPDF、MinerU OCR / VLM、Unstructured / MarkItDown 是 target-blocked production adapter 边界。
- Parser queue/job：`ParseGateway.submit_parse_job()` 继续提供本地 deterministic parse，新增 `ParseJobSnapshot`，记录 queued / running / succeeded|failed timeline、attempt、retry lineage、metrics、failure reason、source provenance 和 adapter boundary；`retry_parse_job()` 可用同一 request contract 做本地 retry。
- Document IR / provenance / ACL：现有 Canonical Document IR、source span、table、figure、code block、ACL、sensitivity tags 和 index handoff 继续由 golden fixtures 覆盖；PHASE07 增加 queue snapshot 对 source provenance 的运行时记录。
- Index adapter boundary：`INDEX_ADAPTER_CONTRACTS` 区分 `local_bm25` / `local_vector` / `local_graph` Current 与 Elasticsearch / Milvus / Neo4j target-blocked external adapters。
- Index manifest：`IndexJobManifest` 记录 source provenance、ACL scopes、sensitivity tags、adapter status、source block ids、retry lineage、graph project ref 和 retrieval payload。

## 验证结果

```powershell
pytest -q tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
# RED before implementation: 4 failed, 21 passed
# GREEN after implementation: 25 passed

pytest -q tests/knowledge tests/api/test_knowledge_api_contract.py tests/retrieval -p no:cacheprovider
# baseline before implementation: 79 passed
# after implementation: 83 passed

python tools/agent/render_architecture.py --check
git diff --check
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
# passed
```

## Remaining Target

- 真实生产 Docling / PyMuPDF、MinerU OCR / VLM、Unstructured / MarkItDown worker 仍是 Target；本 phase 只把 production adapter boundary、local fallback 和 blocked evidence 固定为 Current。
- Elasticsearch / Milvus / Neo4j 仍是 target-blocked external adapters；Current 只包括本地 deterministic BM25 / vector / graph index runtime。
- 深度 OCR / layout / table / code 抽取仍以现有 fixtures 和 deterministic extraction 证明边界，不声称已经具备生产级 OCR/VLM 或复杂版面平台。

## 停止条件

- 外部 parser 或索引服务需要真实部署且无 local fallback。
- OCR/layout/table/code 抽取依赖不可安装或许可证不清。
- 旧 pipeline owner 迁移会破坏现有 retrieval tests。
