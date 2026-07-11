# PHASE04 Real Agent Execution

```yaml
program: zuno-real-unified-runtime-cutover-v1
phase: PHASE04_real-agent-execution
state: completed
```

## 目标

把 ModelStep、Planner、ReActStep 和 Grounded Synthesis 从 deterministic observation baseline 切到真实执行数据面。

## 范围

- `src/backend/zuno/agent/runtime/execution/model_step.py`
- `src/backend/zuno/agent/runtime/execution/react_step.py`
- `src/backend/zuno/agent/runtime/execution/react_runner.py`
- `src/backend/zuno/agent/runtime/planning/**`
- `src/backend/zuno/agent/runtime/synthesis/**`
- `tests/agent/runtime/**`

## 禁止范围

- 不让 ReAct 执行整个全局任务；它只能执行当前 PlanStep。
- 不绕过 Model Gateway。
- 不输出 `Draft answer for:` 或 canned final answer 作为正常产品结果。

## 验收闸门

- [x] `ModelStepExecutor` 调用 Model Gateway，并记录 provider/model/role/latency/token/cost/fallback/trace。
- [x] `ReActStepExecutor` 调用真实 ReAct runner 或在依赖缺失时 blocked。
- [x] Grounded Synthesis 输出 `final_answer`、claims、citation bindings、unsupported claims。
- [x] Reflection 能处理 `REWRITE_ANSWER -> revise_draft -> claim binding -> reflection`。

## 完成证据

- `ModelStepExecutor` 通过 `ModelGatewayRequest` 调用 `deps.model_gateway.invoke()`，并记录 output、metrics、budget verdict 和 trace event。
- 新增 `ReActStepRunner`，`ReActStepExecutor` 只执行当前 PlanStep 的单步 reason / act / observe，不接管全局任务。
- `GroundedSynthesisEngine` 输出 `final_answer`、claims、citation bindings 和 unsupported claims，不再输出 `Draft answer for:` 作为正常结果。
- `pytest -q tests/agent/runtime -p no:cacheprovider` 通过。
- `python tools/scripts/verify_real_runtime_cutover.py --enforce-real-execution` 通过。

## 验证命令

```powershell
pytest -q tests/agent/runtime -p no:cacheprovider
python tools/scripts/verify_real_runtime_cutover.py --enforce-real-execution
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
