# PHASE02 LangGraph Execution Cutover

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE02_langgraph-execution-cutover
state: completed
```

## 目标

让 `UnifiedAgentRuntimeService` 通过 compiled LangGraph 执行 start / stream / resume，使手写 `_run_from()` 主循环退出产品主路径。

## 范围

- `src/backend/zuno/agent/runtime/service.py`
- `src/backend/zuno/agent/runtime/graph.py`
- `src/backend/zuno/agent/runtime/checkpointer.py`
- `src/backend/zuno/agent/runtime/routing.py`
- `src/backend/zuno/agent/runtime/state.py`
- `tests/agent/runtime/**`
- `tools/scripts/verify_real_runtime_cutover.py`

## 禁止范围

- 不改 Completion / Workspace 默认产品切换；那是 PHASE06。
- 不把 deterministic executor 修复塞进本 phase；那是 PHASE04-PHASE05。
- 不把 benchmark 写成 measured。

## 验收闸门

- [x] `UnifiedAgentRuntimeService.start()` 通过 compiled graph `invoke` / `ainvoke` 等价入口执行。
- [x] `stream()` 保留从持久化 event 读取的兼容面；节点 event 由 compiled graph 节点执行时写入 store，不再由 service 手写主循环生成。
- [x] approval / ask_user resume 使用明确 resume payload，不再通用改成 PASS。
- [x] restart 后新 service/store instance 能恢复同一 task。
- [x] `tools/scripts/verify_real_runtime_cutover.py --enforce-langgraph` 通过。

## 完成证据

- `UnifiedAgentRuntimeService.start()` / `resume()` 现在调用 compiled LangGraph `invoke`。
- `_run_from()` / `_next_node()` 手写主运行控制已移出产品主路径。
- LangGraph 节点包装器负责节点级持久化、interrupt 持久化和 completion 持久化。
- `pytest -q tests/agent/runtime -p no:cacheprovider` 通过。
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-langgraph` 通过。

## 验证命令

```powershell
pytest -q tests/agent/runtime -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-langgraph
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
