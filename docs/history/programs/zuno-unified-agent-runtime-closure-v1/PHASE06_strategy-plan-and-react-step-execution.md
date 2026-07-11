# PHASE06_strategy-plan-and-react-step-execution

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE06
    state: completed
    title: Strategy、Plan-and-Execute 与 ReAct Step 真实执行
    depends_on: PHASE05
    next_phase: PHASE07

    ## 目标

    将 StrategySelector、PlanState 和真实 ReAct 合并：Plan-and-Execute 负责宏观步骤，单步 ReAct/adapter 完成行动和 Observation。

    ## 当前事实

    现有 selector 关键词化、PlanStep 固定；GeneralAgent 是独立全任务 ReAct；没有通用 PlanExecutor。

    ## 目标增量

    实现 StrategySelector V2、Planner/Validator、PlanExecutor、StepExecutorRegistry、ReAct/Knowledge/Tool/Model executors。每步有 acceptance、attempt、budget、status。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/planning/{selector,planner,validator,executor}.py
src/backend/zuno/agent/runtime/execution/{registry,react_step,knowledge_step,tool_step,model_step}.py
tests/agent/runtime/test_runtime_plan_execution.py
```

    ## 实施步骤

    1. 落 StrategyDecision 字段。
2. 先计算 deterministic complexity/tool/evidence/risk features。
3. 高复杂任务可用 planner role；失败 fallback deterministic plan。
4. validator 检查 completeness、atomicity、DAG、acceptance、budget。
5. executor 找 ready step；近期串行，contract 支持 dependencies。
6. ReActStepExecutor 只完成一个 step，不 final 整个任务。
7. tool call 输出 ToolCallIntent；knowledge 输出 RetrievalRequest。
8. step 后执行 acceptance。
9. 更新 PlanState version/status/attempt/observation refs。

    ## 关键代码草图

    ```python
class StepExecutor(Protocol):
    action_types: frozenset[str]
    async def execute(self, *, state, step, deps) -> StepExecutionResult: ...

class PlanExecutor:
    def next_ready_step(self, plan):
        completed={s.step_id for s in plan.steps if s.status=="completed"}
        return next((s for s in plan.steps if s.status=="pending" and set(s.dependencies)<=completed), None)
```

    ## 测试

    direct/react/multi-step、invalid DAG、acceptance failure、planner invalid JSON fallback、step budget、legacy GeneralAgent regression。

    ## 验收标准

    复杂请求推进至少两个真实 step；ReAct 不绕过 policy；Plan 不再仅对象生成；step 可持久化。

    ## Windows PowerShell 验证

    ```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath 'F:\internship-work\resume&resume project\02_projects\Zuno'
$VenvPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$Python = if (Test-Path -LiteralPath $VenvPython) { (Resolve-Path -LiteralPath $VenvPython).Path } else { 'python' }
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src\backend').Path
```
```powershell
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_plan_execution.py','tests\agent\runtime\test_runtime_graph_routes.py','tests\agent\test_planning.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'planning execution tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    Planner model 不稳定时保留 deterministic；禁止自由文本 plan 直接执行。planning.py 先作为 facade。

    ## 文档与状态同步

    更新 Plan/ReAct Current/Partial 和 legacy adapter 说明。

    ## 完成记录

    - 已新增 `runtime/planning`：`RuntimeStrategySelector`、`RuntimePlanner`、`PlanValidator`、`PlanExecutor`。
    - 已新增 `runtime/execution`：`StepExecutorRegistry`、`ReActStepExecutor`、`KnowledgeStepExecutor`、`ToolStepExecutor`、`ModelStepExecutor`。
    - `UnifiedAgentRuntimeService` 已从 fixed single-step skeleton 升级为 Strategy -> Plan -> next ready step -> executor -> observation -> plan status/attempt/observation refs 的逐步执行。
    - `PlanStep` contract 已增加 `status` 和 `observation_refs`，支持 durable step progress。
    - 已证明复杂任务在 unified runtime 中执行至少两个 step 后再进入 reflection/finalize；invalid DAG、missing acceptance、attempt/status/observation refs 均有 focused tests。
    - Tool executor 当前只生成 governed ToolCallIntent observation；真实 Tool Control Plane approval、credential、timeout 和 idempotency 闭环属于 PHASE07。

    ## Phase 完成报告

    Codex 必须报告：

    1. 修改文件和 owner。
    2. 新增或修改的 contract。
    3. 真实调用链。
    4. 测试命令与结果。
    5. trace、restart 或 eval 证据。
    6. 未完成和 blocked 项。
    7. commit SHA。
    8. 下一 Phase 是否满足依赖。
