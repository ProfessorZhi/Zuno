# Goal04 PHASE18 KnowledgeRetrievalGraph Contract Evidence

updated: 2026-07-28
phase: PHASE18 Agentic GraphRAG Inner Loop
pr: PR D / #49
status: implementation-evidence
production_readiness: not established

## 目标

本证据记录 PHASE18 的第一块实现增量：把 Knowledge 内层检索从“corrective wrapper trace”推进为显式固定 `KnowledgeRetrievalGraph` contract，并把 Knowledge 产出的 `KnowledgeControlProposal` 暴露给 Agent Core observation。

本文件不是 PHASE18 closure approval，不把 PHASE18 标记为 completed。

## 实现范围

- 新增固定节点 contract：`validate -> pin_snapshot -> scope -> interpret -> select_profile -> plan_round -> admit -> dispatch -> normalize -> fuse_rerank -> evidence_ledger -> evaluate -> corrective_decision`。
- 新增内部 profile contract：`standard/local/global/drift/deep/agentic`。
- 新增 `KnowledgeControlProposal`，默认要求 Agent Core 显式接受或拒绝，Knowledge 不直接修改 Agent PlanVersion、不问用户、不调用外部 Tool。
- `CorrectiveAgenticRetrievalRuntime` 每次检索生成 `knowledge_retrieval_graph` trace。
- `KnowledgeStepExecutor` 把 graph trace 和 proposal 放入 observation metadata，供 Agent Core 后续 gate 消费。

## 验证

```powershell
python -m py_compile src\backend\zuno\knowledge\agentic\contracts.py src\backend\zuno\knowledge\agentic\runtime.py src\backend\zuno\agent\runtime\execution\knowledge_step.py tests\knowledge\test_corrective_retrieval_runtime.py
python -m pytest tests\knowledge\test_corrective_retrieval_runtime.py tests\knowledge\test_evidence_ledger.py -q -p no:cacheprovider --tb=short
```

结果：

```text
11 passed in 48.15s
```

## 剩余范围

PHASE18 尚未完成。后续仍需继续实现和验证 Retriever 并行预算、持久化 Recovery/Idempotency、Agent Core proposal accept/reject gate、旧 GraphRAG 默认路径切流、Migration / integration / fault / security gate 和 closure approval。
