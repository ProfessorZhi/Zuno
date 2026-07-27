# Goal03 Wave A Runtime Default Completion Fast-Fail Evidence

status: partial_runtime_evidence
phase: PHASE09
commit_scope: Default completion/workspace runtime fast-fail for unavailable memory persistence

本文只证明本次修复切片：默认 Completion / Workspace Unified Runtime 在本机 PostgreSQL 不可用时，不再无限等待 Memory 持久化路径；`DatabaseMemoryStore.persistence_health()` 先做快速 TCP 探测，再让 runtime 节点把不可用状态显式写入 `ContextPack.task_state`，从而让默认入口以可验证的 blocked / finalized 语义结束。

## 已证明

- `DatabaseMemoryStore.persistence_health()` 能在本机无 PostgreSQL 时快速返回 `available=False`，不会阻塞到测试超时。
- `agent.runtime.nodes.core.build_context` 会在 memory persistence unavailable 时改写 ContextPack 并跳过后续持久化上下文读写。
- `agent.runtime.nodes.core.post_turn_commit` 会读取 context task_state，避免在 persistence unavailable 情况下重复撞数据库。
- Completion route 测试恢复为稳定通过。
- Runtime factory start 测试恢复为稳定通过。
- `workspace_task_runtime` 和 `runtime_dependency_factory` 相关用例恢复为稳定通过。

## 已运行验证

```powershell
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py::test_unified_runtime_service_can_start_from_factory_assembly -p no:cacheprovider
python -m pytest -q tests/api/test_completion_unified_runtime.py::test_completion_route_streams_unified_runtime_events -p no:cacheprovider
python -m pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
python -m pytest -q tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
git diff --check
```

结果：

```text
1 passed in 15.27s
1 passed in 16.84s
16 passed in 35.52s
4 passed in 15.25s
```

## 未证明

- 这只证明默认 runtime 入口不再因 memory persistence 不可达而超时，不证明 PHASE13 完整实现或 Wave B 完成。
- 生产 PostgreSQL、Memory 持久化与更大范围恢复语义仍需后续证据。
