# PHASE09 Memory Context Production Governance

status: completed
previous_phase: PHASE08_durable-agent-runtime-persistence
completed_at: 2026-07-01
next_phase: PHASE10_tool-sandbox-vault-network-runtime

## 目标

把 Memory 与 Context 推进到 semantic/vector memory、后台治理 scheduler、隐私删除平台和 memory eval baseline。

## 范围

- SQLModel-backed memory store 的生产边界。
- semantic / vector memory adapter。
- promotion、decay、consolidation、privacy delete、sensitive data isolation。
- memory eval baseline 和 context pack quality checks。

## 禁止范围

- 不把 in-memory 或 fixture-only 行为写成生产 Current。
- 不保存敏感信息到不可删除路径。

## 验收闸门

- memory 可跨任务读写、审查、删除和追责。
- semantic/vector adapter 有本地 fallback 和 tests。
- memory eval baseline 进入 release gate。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/storage -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/memory/contracts.py`
- `src/backend/zuno/memory/engine.py`
- `src/backend/zuno/memory/store.py`
- `src/backend/zuno/memory/retrieval.py`
- `src/backend/zuno/memory/rendering.py`
- `tests/agent/test_memory_layers.py`
- `tests/storage/**`

## 需要修改的文件

- `src/backend/zuno/memory/**`
- memory scheduler / semantic adapter modules
- `src/backend/zuno/agent/**` only for context pack integration
- `tests/agent/test_memory_*.py`
- `tests/storage/**`

## 执行拆解

1. 区分 raw event、task summary、durable memory、semantic/vector memory、context pack。
2. 实现 semantic/vector adapter 边界和 local deterministic fallback。
3. 补后台 governance：promotion、decay、consolidation、privacy delete、sensitive isolation。
4. 建立 memory eval baseline：retrieval relevance、privacy safety、context compression quality。
5. 接入 GeneralAgent context pack，但不让 memory 存储不可删除敏感信息。

## 多 agent 分工

- Thread A：memory store / governance ledger。
- Thread B：semantic/vector adapter。
- Thread C：context pack / GeneralAgent integration。
- Thread D：memory eval / storage tests。
- 主线程：审查隐私删除和可追责证据。

## 需要返回的证据

- memory taxonomy matrix。
- semantic/vector fallback 证据。
- governance ledger 样例。
- privacy delete 测试。
- memory eval baseline 结果。

## 完成证据

- Memory taxonomy：继续由 `MEMORY_TAXONOMY` 区分 raw event log、working / recent window、task summary、episodic / semantic / procedural memory、graph memory candidate 和 model context pack。
- Semantic / vector fallback：`DeterministicSemanticMemoryAdapter` 提供 local token-hash search result，输出 `adapter_id`、`vector_ref`、`score` 和 `local_fallback=True`；不依赖外部向量库。
- Governance ledger：`DurableMemoryStore` 和 `DatabaseMemoryStore` 都支持 redacted privacy delete ledger，删除 scoped raw event、task summary、memory candidate、review decision 和旧治理记录后，只保留不含原文的 `privacy_delete_applied` 证据。
- Context Pack safety：`MemoryEngine.render_context_pack()` 会阻止 sensitive raw event 和由 sensitive source event 派生的 summary 进入 context，并保留 excluded item reason。
- GeneralAgent integration：`GeneralAgent.prepare_context()` 通过 semantic memory search 选择 approved memory；无 query match 时才回退到 approved memory fallback，仍保留 source event ids 和 adapter metadata。
- Memory eval baseline：`evaluate_memory_baseline()` 生成 retrieval relevance、privacy safety、context compression quality 三类指标和 `release_gate_status`，可作为后续 release gate 输入。

## 验证结果

```powershell
pytest -q tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py tests/storage -p no:cacheprovider
# baseline before implementation: 41 passed
# RED before implementation: 6 failed, 40 passed
# GREEN after implementation: 46 passed

pytest -q tests/repo/test_static_target_layer_imports.py tests/repo/test_backend_facade_layers.py -p no:cacheprovider
# 6 passed

git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-docs.ps1
# passed
```

## Remaining Target

- 本 phase 的 semantic/vector 能力是 deterministic local fallback，不是 Milvus / Elasticsearch / pgvector 等生产级向量记忆库。
- privacy delete 当前证明 scoped runtime memory store 删除和 redacted ledger，不是完整企业隐私工单平台、跨备份删除或法务保留流程。
- memory eval baseline 当前是本地 release gate 输入；后台 scheduler、nightly memory eval、冲突检测和深度 PII/secret 检测仍是 Target。

## 停止条件

- 需要外部 vector DB 且无 local fallback。
- 隐私删除无法覆盖新增存储路径。
- memory 写入会泄露未授权 workspace 数据。
