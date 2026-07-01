# PHASE09 Memory Context Production Governance

status: pending

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
