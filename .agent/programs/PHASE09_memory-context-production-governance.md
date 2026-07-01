# PHASE09 Memory Context Production Governance

status: active
previous_phase: PHASE08_durable-agent-runtime-persistence

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

## 停止条件

- 需要外部 vector DB 且无 local fallback。
- 隐私删除无法覆盖新增存储路径。
- memory 写入会泄露未授权 workspace 数据。
