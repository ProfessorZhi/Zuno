# PHASE06 Product Cutover

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE06_product-cutover
state: completed
```

## 目标

Completion / Workspace 默认走 unified runtime；GeneralAgent 只保留显式 rollback flag；Workspace artifact 来自 unified runtime final state。

## 范围

- `src/backend/zuno/api/**`
- `src/backend/zuno/agent/**`
- `apps/web/**`
- `tests/api/**`
- `tests/e2e/**`

## 禁止范围

- 不要求前端重设计。
- 不把 legacy path 静默删除；短期必须有 rollback flag。
- 不让 unified runtime 依赖特殊 `product_mode` 才启用。

## 验收闸门

- [x] 普通 Completion 请求默认进入 unified runtime。
- [x] `ZUNO_AGENT_RUNTIME=legacy_general_agent` 或等价显式 flag 才回 legacy。
- [x] SSE 输出 runtime_started、node_started、model_call、retrieval_round、tool_call、approval_required、reflection、replan、answer_chunk、citation、runtime_completed。
- [x] Workspace task final answer / artifact 来自 unified runtime。
- [x] page refresh 后 approval resume 只执行一次。

## 完成证据

- Completion route 默认走 `CompletionService.stream_unified_runtime()`；只有 `ZUNO_AGENT_RUNTIME=legacy_general_agent` 回 legacy GeneralAgent。
- Completion final chunk 来自 unified runtime `GroundedSynthesisEngine` 的 `final_answer`，不再输出固定 `Unified runtime completed.`。
- Completion SSE 保留 runtime events，并派生 node_started、model_call、retrieval_round、tool_call、approval_required、reflection、replan、citation 和 answer_chunk。
- `pytest -q tests/api tests/e2e tests/agent/runtime -p no:cacheprovider` 通过。
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-product-cutover` 通过。

## 验证命令

```powershell
pytest -q tests/api tests/e2e tests/agent/runtime -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-product-cutover
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
