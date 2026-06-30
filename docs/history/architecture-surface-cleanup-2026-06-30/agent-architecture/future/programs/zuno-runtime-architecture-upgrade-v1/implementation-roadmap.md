# Zuno Runtime Architecture Upgrade V1
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

在 Query Router、Context Builder、Hooks / Evidence / Trace 三个边界清楚后，再做真正 runtime 架构升级。

## Phase

1. [PHASE01：Runtime upgrade audit](PHASE01_runtime-upgrade-audit.md)
2. [PHASE02：GraphRAG LLM entity extraction](PHASE02_graphrag-llm-entity-extraction.md)
3. [PHASE03：Knowledge extractor configs](PHASE03_knowledge-extractor-configs.md)
4. [PHASE04：Memory / Capability / Trace hardening](PHASE04_memory-capability-trace-hardening.md)
5. [PHASE05：Eval / trace closure](PHASE05_eval-trace-closure.md)

## 禁止范围

不恢复多 Agent runtime；Zuno runtime 目标仍是 Single GeneralAgent。
不把 `auto` 写成第五种 query method；不绕过 Context Pack、Evidence Check 和 Trace contract。
