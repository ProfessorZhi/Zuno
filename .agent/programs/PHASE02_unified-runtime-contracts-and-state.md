# PHASE02_unified-runtime-contracts-and-state

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE02
    state: planned
    title: 统一 Runtime Contract 与版本化状态
    depends_on: PHASE01
    next_phase: PHASE03

    ## 目标

    建立唯一 Agent runtime 状态和节点输入输出 contract，使 GeneralAgent、planning/control baseline 和 durable runtime 能被同一个 graph 消费。

    ## 当前事实

    状态分散在 StreamAgentState、ControllerRuntimeState、PlanState、RuntimeObservation 和领域 models 中；序列化与版本策略不统一。

    ## 目标增量

    新增 `zuno.agent.runtime` contract 层，复用现有领域对象。Graph state 与持久化 snapshot 分离，并为 legacy objects 提供 adapter。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/{state,contracts,dependencies,limits,events,adapters}.py
tests/agent/runtime/test_runtime_state_contract.py
tests/agent/runtime/test_runtime_legacy_adapters.py
```

    ## 实施步骤

    1. 定义稳定 ids 与 ObservationKind。
2. 定义 NormalizedObservation、RuntimeLimits、RuntimeCounters。
3. 定义轻量 AgentRuntimeState 和 Pydantic AgentRuntimeSnapshot。
4. 定义 NodeOutcome、StrategyDecision、ReflectionDecision、FinalizationStatus。
5. PlanStep 增 expected output、acceptance、dependencies、policy refs、budget、attempt。
6. 为 ControllerRuntimeState、PlannerOutput、RuntimeObservation 写转换。
7. 敏感或大 payload 只保存 ref。
8. unknown state_version 明确拒绝或 migrate。

    ## 关键代码草图

    ```python
class NormalizedObservation(BaseModel):
    observation_id: str
    step_id: str
    kind: ObservationKind
    status: Literal["completed","failed","blocked","waiting"]
    summary: str = ""
    payload_ref: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    failure_code: str | None = None
    trace_span_id: str

class AgentRuntimeSnapshot(BaseModel):
    state_version: Literal["agent-runtime-v1"] = "agent-runtime-v1"
    run_id: str
    task_id: str
    thread_id: str
    trace_id: str
    context_pack: dict[str, Any] = Field(default_factory=dict)
    strategy: StrategyDecision | None = None
    plan_state: PlanState | None = None
    observations: list[NormalizedObservation] = Field(default_factory=list)
    evidence_ledger_ref: str | None = None
    reflection: ReflectionDecision | None = None
```

    ## 测试

    enum/string compatibility、JSON round-trip、version error、legacy adapter field preservation、敏感 payload exclusion。

    ## 验收标准

    新 graph 后续只依赖该 contract；无第四套 Plan/Observation；所有状态 JSON 可序列化；adapter 不丢关键字段。

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
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_state_contract.py','tests\agent\runtime\test_runtime_legacy_adapters.py','tests\agent\test_agent_control_runtime.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'runtime contract tests failed' }
& $Python -m compileall -q 'src\backend\zuno\agent\runtime'
if ($LASTEXITCODE -ne 0) { throw 'compileall failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    不得一次删除旧 contract；用 adapter 过渡。state 过大时优先 refs。

    ## 文档与状态同步

    更新 agent-core-runtime 实现路径，但 unified runtime 仍为 Partial/Target。

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
