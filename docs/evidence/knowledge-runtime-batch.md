# Knowledge Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-KNOW-001` 到 `ARCH-KNOW-030`

范围说明：

- 已证明 Knowledge query 只能由 Agent Core retrieval decision 触发，并携带 EvidenceRequirement、snapshot、security filter 和 budget。
- 已证明 KnowledgeVersion 接受必须具备 SourceSpan manifest、DocumentVersion、security metadata、index manifest 和 visibility receipt。
- 已证明 Knowledge 使用固定 retrieval graph，动态内容只存在于 versioned RetrievalPlan / RetrievalRound。
- 已证明多 retriever 结果经 idempotent reducer，round result 绑定 snapshot/security/hash/deadline/generation。
- 已证明 evidence requirement、frontier、ledger append/dedup/version reducer 可验证。
- 已证明 fusion normalization、RRF version、rerank candidate bound 和 model slot 边界。
- 已证明 Graph evidence 需要 capability、reason code 和 SourceSpan backlink；无 SourceSpan 只能 auxiliary-only。
- 已证明 authority/temporal/conflict/citation eligibility policy。
- 已证明 corrective retrieval、retry/correct/replan separation、stop/no-progress/budget guard。
- 已证明 cancellation late guard、domain/checkpoint reconciliation、version lifecycle、deletion propagation、typed/redacted event。
- 已证明 eval comparability、quality release gate 和 config intent/spec/projection API 分离。

未覆盖：

- Knowledge 模块 `ARCH-KNOW-001` 到 `ARCH-KNOW-030` 已由本批 evidence 覆盖；其他模块仍需后续批次证明。
- 本证据不声明 PHASE12 或全 Program 关闭。

验证命令：

```powershell
python -m py_compile src/backend/zuno/knowledge/runtime_batch.py tools/scripts/verify_knowledge_runtime_batch.py
pytest -q tests/knowledge/test_knowledge_runtime_batch.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
python tools/scripts/verify_knowledge_runtime_batch.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
pytest -q tests/knowledge/test_knowledge_runtime_batch.py tests/agent/test_knowledge_layer_surfaces.py tests/agent/test_agentic_retrieval_runtime.py tests/agent/test_agentic_graphrag_contract.py tests/knowledge/test_evidence_ledger.py tests/knowledge/test_index_jobs_runtime.py tests/retrieval/test_retrieval_fusion.py tests/retrieval/test_retrieval_orchestrator.py tests/retrieval/test_retrieval_planner.py -p no:cacheprovider
```

结果：

```text
7 passed in 3.10s
Knowledge runtime batch verifier passed for ARCH-KNOW-001..030
Requirement ledger evidence gate passed.
documentation entrypoint verification passed.
51 passed in 12.77s
```
