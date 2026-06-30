# PHASE09 agentic-retrieval-evidence-citation-runtime

status: pending

## 目标

让 ProductMode、QueryMethod、AgenticRetrievalRouter、StagedFusionPlan、EvidenceBundle、CitationBuilder 和 UnsupportedClaimChecker 真正消费新的 ingestion/index runtime。

## 范围

- 接通 normal / enhanced / auto 用户模式与 basic / local / global / drift 内部方法。
- 实现 fusion/rerank、citation-rich answer、unsupported claim guard。
- 推进 graph extraction、community report 和 index manifest runtime。

## 禁止范围

- 不把 query method contract 当作成熟 GraphRAG。
- 不把 global community prior 和 chunk-level evidence 混成不可解释排序。
- 不输出无 citation 的企业知识答案作为成功路径。

## 验收闸门

- e2e retrieval test 能从上传文档产生 citation-rich answer。
- Evidence coverage、citation coverage、unsupported claim check 进入 trace/eval。
- fallback reason 可断言。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_agentic_graphrag_contract.py tests/retrieval tests/graphrag tests/evals -p no:cacheprovider
```

