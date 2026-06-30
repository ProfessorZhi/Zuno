# PHASE08 RAG GraphRAG Evidence Citation

status: pending

## 目标

把 basic/local/global/drift 变成可解释、可评测、可引用的 Knowledge / Retrieval 系统，支撑企业私有知识库问答和报告生成。

## 步骤

- [ ] 保持 product mode：normal、enhanced、auto。
- [ ] 保持 resolved query method：basic、local、global、drift。
- [ ] 实现或强化 BM25 + dense vector + RRF + optional rerank。
- [ ] 实现 GraphRAG extraction、community report、local/global/drift query 的成熟路径。
- [ ] 建立 Evidence Bundle、Citation Builder、unsupported claim check。
- [ ] 写 retrieval/eval tests。

## 验收

- `auto` 只是 router，不是最终 query method。
- `global` 是 community-level prior，不和 BM25 chunk 生硬混榜。
- 每个答案可以追溯 evidence 和 citation。

## 验证

```powershell
pytest -q tests/graphrag tests/retrieval tests/evals -p no:cacheprovider
```
