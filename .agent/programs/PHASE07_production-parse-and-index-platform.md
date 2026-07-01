# PHASE07 Production Parse and Index Platform

status: active
previous_phase: PHASE06_product-surface-desktop-recovery-loop

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

## 停止条件

- 外部 parser 或索引服务需要真实部署且无 local fallback。
- OCR/layout/table/code 抽取依赖不可安装或许可证不清。
- 旧 pipeline owner 迁移会破坏现有 retrieval tests。
