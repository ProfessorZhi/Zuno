# Memory Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-MEM-001` 到 `ARCH-MEM-060`

范围说明：

- 已证明 Working、Session、Long-term 生命周期边界明确，Working State 归 Agent Core，长期记忆仅 Episodic、Semantic、Procedural 三类。
- 已证明 Entity、Vector、Graph、Lexical 只是 projection，ContextPackVersion 是不可变 read view。
- 已证明 Session Summary 与原始消息分离，增量更新、coverage/source hash、atomic raw tail、manifest/object lazy loading 和 context pack immutable hash。
- 已证明长期写入必须经 MemoryCandidate 和 governance，MemoryVersion 不可变，source fact 与 memory fact 可追溯。
- 已证明按类型检索、scope/ACL 召回前执行，Security 先于模型摘要。
- 已证明 C0-C3 compression、F0-F4 fidelity、tool payload 优先压缩、protected set 不静默删除、context budget 确定且 exact token validation。
- 已证明 compact 后 rehydration，summary 不是唯一恢复源。
- 已证明 Reflexion 默认 Episodic，Procedural 晋升需要证据门槛，Procedural 仅为 strategy hint。
- 已证明 consolidation 不直接删除 source，utility projection 与 fact 分离，negative transfer 可 suspend，freshness 使用前验证，effective/observed time 分离，冲突不静默覆盖。
- 已证明 Candidate、Version、Summary、Context Build 状态机闭合。
- 已证明 projection 发布顺序不可跳过，index receipt 不等于 active。
- 已证明 commit intent 可幂等重放，checkpoint 与 domain commit 可协调恢复，并发更新使用 generation/CAS，UNKNOWN 先 reconcile。
- 已证明 privacy delete 传播所有 projection，legal hold 阻断删除，prompt injection 不获得权威，隐藏思维链不持久化，模型只产生 proposal。
- 已证明弱模型默认摘要、强模型复杂整合，model upgrade 有 lineage，context selection 全量 trace，MemoryUseTrace 关联 outcome/eval，固定 eval 覆盖长期与压缩质量。
- 已证明 canonical store 使用 PostgreSQL，大 payload 使用 ObjectRef，Vector/Graph/Lexical projection 可重建，CrossModuleEnvelope 字段贯通，Target/Current 状态源分离。

未覆盖：

- Memory 模块 `ARCH-MEM-001` 到 `ARCH-MEM-060` 已由本批 evidence 覆盖；其他模块仍需后续批次证明。
- 本证据不声明 PHASE13 或全 Program 关闭。

验证命令：

```powershell
python -m py_compile src/backend/zuno/memory/runtime_batch.py tools/scripts/verify_memory_runtime_batch.py
pytest -q tests/memory/test_memory_runtime_batch.py tests/agent/test_memory_layer_surfaces.py -p no:cacheprovider
python tools/scripts/verify_memory_runtime_batch.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
pytest -q tests/memory/test_memory_runtime_batch.py tests/agent/test_memory_layer_surfaces.py tests/memory/test_context_pack_engine.py tests/memory/test_memory_context_trace.py tests/agent/runtime/test_runtime_memory_reflexion.py tests/agent/test_memory_system_contract.py tests/agent/test_memory_durable_runtime.py tests/storage/test_memory_runtime_store.py -p no:cacheprovider
```

结果：

```text
6 passed in 1.76s
Memory runtime batch verifier passed for ARCH-MEM-001..060
Requirement ledger evidence gate passed.
documentation entrypoint verification passed.
22 passed in 12.84s
```
