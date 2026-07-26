# Goal03 Wave A Knowledge and Capability Surface Guard Evidence

status: partial_runtime_evidence
phase: PHASE12, PHASE14
commit_scope: Knowledge search persistence guard and Capability runtime public surface repair

本文只证明本次修复切片：Knowledge search API 在受控 QueryService adapter 成功返回后，不再因为当前缺少 ACTIVE Knowledge Snapshot 而把 API 响应降为 500；同时 `zuno.capability.runtime.__all__` 收回到 PHASE14 target surface，不再把 legacy approval adapter 常量和内部 security sink protocol 暴露为公共模块边界。

## 已证明

- `KnowledgeService.search_knowledge(...)` 仍先调用 `KnowledgeQueryService().query(...)`，旧 `RagHandler` 不会被 API contract 测试路径使用。
- Durable query-run persistence 在缺少 ACTIVE snapshot 时以 `query_run_persistence.status = blocked` 暴露，不冒充已记录，也不覆盖已成功的检索 payload。
- `zuno.capability.runtime.__all__` 与 capability target surface 测试一致，只暴露运行时请求、执行上下文、sandbox、credential broker 和默认 control plane builder。
- Goal03 Wave A / Wave B 当前 PostgreSQL persistence baseline 未被本次修复破坏。

## 已运行验证

```powershell
python -m pytest -q tests/api/test_goal03_knowledge_route.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_knowledge_runtime_batch.py -p no:cacheprovider
python -m pytest -q tests/api/test_goal03_capability_route.py tests/capability/test_capability_skill_layer.py tests/capability/test_tool_runtime_batch.py tests/agent/test_capability_layer_surfaces.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py tests/integration/test_goal03_wave_b_persistence.py -p no:cacheprovider
git diff --check
```

结果：

```text
31 passed
16 passed
5 passed
```

## 未证明

- 本证据不证明 PHASE12 external BM25/Vector/Graph adapter、ACL/Temporal/Conflict、rollback 和 deletion propagation 全部完成。
- 本证据不证明 PHASE14 Installation/Activation CAS、revocation propagation、ordered transition crash recovery、progressive loading budget 和 legacy registry cutover 全部完成；这些需结合对应 PHASE14 evidence 做 Closure Gate 汇总。
