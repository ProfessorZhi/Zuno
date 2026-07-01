# PHASE04 Knowledge Retrieval And GraphRAG Profile

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE04_knowledge-retrieval-and-graphrag-profile
status: completed

## 目标

把知识库产品层固定为标准检索 / 深度检索，并让后端以 staged retrieval 方式自动选择 BM25、vector、GraphRAG local / community / drift、rerank、requery 和 citation coverage check。

## 范围

- RetrievalProfile：`standard`、`deep`、`deep_without_graph`。
- RetrievalDecision：记录 requested profile、effective profile、retrievers used、fallback reason。
- EvidenceBundle：聚合 evidence、citation refs、coverage 和 unsupported claim inputs。
- CitationLineage：保持 source object、document version、block、parse job、span / page。
- graph index 未就绪时 fallback 为 `deep_without_graph`。

## 目标架构拼接点

本 phase 拼到 Knowledge Capability 和 Agentic Retrieval Planner 的执行侧。它必须把“用户只选标准检索 / 深度检索”落实成后端可观测决策：

- `standard` 负责日常问答：BM25 + vector + light fusion + citation。
- `deep` 负责复杂分析：staged retrieval、query rewrite、evidence check、conditional graph expansion、rerank、requery、citation coverage check。
- `deep_without_graph` 负责图谱未构建时的 graceful fallback。
- `EvidenceBundle` 是 Planning / Reflection / Output Gate 的唯一证据输入。
- `CitationLineage` 让 artifact 和回答能回到 source object / document version / block / span。

本 phase 不决定最终回答，也不直接暴露 local / global / drift 给用户；它只给 Agent 提供可调用的检索能力。

## 并行开发可行性

本 phase 可由 Workstream B 独立推进，并与 Workstream A 的 index persistence、Workstream F 的 RetrievalPlan 并行协作。

可并行：

- RetrievalProfile / RetrievalDecision tests 与 EvidenceBundle / CitationLineage tests 可拆开。
- standard 与 deep fallback 可并行实现。
- graph trace boundary 可在真实 graph runtime 前先以 deterministic local fixtures 验证。

不可并行：

- 不得同时修改 frozen retrieval contract 和 planning contract。
- 不得绕过 Retrieval Gate 的 ACL / sensitivity filter。
- 不得把 graph unavailable 变成 silent empty answer。

## 详细执行卡

- 输入依赖：PHASE02 RetrievalProfile / EvidenceBundle contract、PHASE03 index manifest/chunks/citation lineage、现有 knowledge/indexing runtime。
- 主要交付物：`standard` / `deep` profile、RetrievalDecision、deep_without_graph fallback、EvidenceBundle、CitationBuilder / CitationLineage integration、retrieval trace fields。
- 可并行工作包：standard profile、deep staged profile、fallback/trace、citation coverage tests 可拆；GraphRAG materialization 只做 boundary，不阻塞 standard/deep baseline。
- Coordinator 锁点：用户可见 profile 名称只能是“标准检索 / 深度检索”；不得把 basic/local/global/drift 暴露为产品模式。
- 下游交接：PHASE09/10 消费 RetrievalPlan 和 EvidenceBundle；PHASE12 用 standard/deep E2E；PHASE13 用 retrieval rounds、retrievers_used、citation coverage metrics。
- PR / commit 建议：`feat(retrieval): add standard deep retrieval profiles` 与 `test(retrieval): cover deep fallback and citation coverage` 分开提交。

## 禁止范围

- 不让用户手动选择 basic / local / global / drift 作为主产品模式。
- 不把 Basic RAG 或 Static GraphRAG 写成最终产品形态。
- 不让深度检索一上来无条件跑所有昂贵通道。

## 验收闸门

- 标准检索单文档事实测试通过。
- 深度检索跨文档分析测试通过。
- graph index 不可用时 deep_without_graph fallback 测试通过。
- retrieval decision trace 记录 requested/effective profile 和 fallback reason。
- citation coverage 进入 evidence / trace。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/evals -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/knowledge/retrieval/**`
- `src/backend/zuno/knowledge/graphrag/**`
- `src/backend/zuno/knowledge/query_service.py`
- `tests/knowledge/**`
- `tests/evals/**`

## 需要修改的文件

- `src/backend/zuno/knowledge/**`
- `tests/agent/test_knowledge_graphrag_runtime_contracts.py`
- `tests/knowledge/**`
- `tests/evals/**`

## 执行拆解

1. 写 RetrievalProfile / RetrievalDecision tests。
2. 写 standard profile retrieval test。
3. 写 deep profile staged retrieval test。
4. 写 deep_without_graph fallback test。
5. 实现最小 deterministic router / planner boundary。
6. 确认 citation lineage 未断链。

## 多 agent 分工

- Workstream B owner。
- Workstream F 只消费 retrieval plan output，不直接改 retrieval internals。
- Coordinator 审查任何 public API 字段变化。

## 需要返回的证据

- standard / deep / fallback tests。
- trace fields 示例。
- citation lineage 示例。

## Closure Evidence

- Runtime files：`src/backend/zuno/knowledge/agentic_graphrag.py`、`src/backend/zuno/agent/contracts.py`。
- Product profile：`AgenticRetrievalRuntimeRequest.retrieval_profile` 接受 `standard` / `deep`，用户可见 profile 只暴露 `standard` 和 `deep`，`basic` / `local` / `global` / `drift` 保持内部 QueryMethod。
- Standard retrieval：`standard` 映射到本地 light fusion baseline，使用 BM25 + vector，生成 EvidenceBundle、Citation 和 RetrievalDecision。
- Deep fallback：`deep` 在本地 graph index 不可用时输出 `effective_profile=deep_without_graph` 与 `fallback_reason=graph_index_unavailable`，不 fake graph success。
- Trace evidence：retrieval trace 记录 requested/effective profile、fallback reason、retrievers_used、evidence_count、citation_coverage 和 profile contract。
- ACL / sensitivity：EvidenceItem 从 index chunk metadata 保留 `acl_scope` 与 `sensitivity_tags`，disallowed ACL evidence 会被 dropped 并进入 task event / evidence verdict。
- Focused tests：`pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py -p no:cacheprovider` 通过，`4 passed`。
- Regression tests：`pytest -q tests/agent -p no:cacheprovider` 通过，`171 passed`；`pytest -q tests/knowledge -p no:cacheprovider` 通过，`54 passed`；`pytest -q tests/evals -p no:cacheprovider` 通过，`148 passed, 3 warnings`。

## 停止条件

- GraphRAG fallback 会产生无来源 answer。
- 深度检索绕过 ACL / sensitivity filter。
- 新 profile 破坏现有 workspace query compatibility。
