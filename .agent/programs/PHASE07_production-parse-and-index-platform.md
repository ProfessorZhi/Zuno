# PHASE07 Production Parse and Index Platform

status: pending

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
