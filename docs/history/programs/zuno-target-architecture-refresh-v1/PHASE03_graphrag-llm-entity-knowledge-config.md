# PHASE03：GraphRAG LLM 实体抽取与知识库多配置目标

## 目标

明确 GraphRAG 实体抽取目标优先 LLM extraction，而不是正则/规则匹配；明确知识库可以选择不同 extractor / config。

## 范围

- `docs/architecture/target-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `docs/architecture/roadmap.md`

## 验收

目标写清楚 extraction strategy、fallback、成本/延迟/评测边界，但不实现代码。
