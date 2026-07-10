# PHASE07_tool-control-plane-and-approval-integration

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE07
    state: completed
    title: Tool Control Plane、Approval 与 Resume
    depends_on: PHASE06
    next_phase: PHASE08

    ## 目标

    让所有 Tool/MCP 实际执行经过 ToolControlPlaneRuntime，并把 approval wait、timeout、denied、normalized result 转为 Observation 和 graph route。

    ## 当前事实

    GeneralAgent middleware 可直接调用 handler；ToolControlPlaneRuntime 已有 manifest、approval、credential、sandbox/network 和 normalized result，但不是统一 graph 唯一路径。

    ## 目标增量

    实现 ToolStepExecutor：ToolCallIntent -> ToolRuntimeRequest -> policy/approval -> interrupt -> approved idempotent execution -> Observation。选择 2–3 个真实工具 vertical slice。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/execution/tool_step.py
src/backend/zuno/agent/runtime/nodes/tool_approval.py
src/backend/zuno/capability/langchain_adapter.py
src/backend/zuno/agent/core/agents/general_agent.py
tests/agent/runtime/test_runtime_tool_control_plane.py
tests/agent/runtime/test_runtime_tool_idempotency.py
```

    ## 实施步骤

    1. 从 ToolCard/DB tool 建 manifest。
2. LangChain call 只形成 intent。
3. executor 调 ToolControlPlaneRuntime。
4. approval_waiting 保存 interrupt、args hash、ids。
5. resume 先 claim idempotency。
6. normalized result 转 TOOL Observation。
7. denied/timeout/network blocked 也变 Observation。
8. credential 只存 ref。
9. MCP 走同一 policy。
10. vertical set：只读本地/知识、只读 remote、一个 local write/side effect。

    ## 关键代码草图

    ```python
result = deps.tool_runtime.execute(ToolRuntimeRequest(
    tool_id=intent.tool_id,
    arguments=intent.arguments,
    workspace_id=state.workspace_id,
    user_id=state.user_id,
    task_id=state.task_id,
    trace_id=state.trace_id,
    model_intent=intent.reason_summary,
    execution_id=intent.idempotency_key,
))
if result.status == "approval_waiting":
    return StepExecutionResult.interrupt(...)
return StepExecutionResult.observation(NormalizedObservation.from_tool_result(result))
```

    ## 测试

    read-only auto、approval wait、approve once、重复 resume、reject、timeout/network、secret redaction、GeneralAgent adapter。

    ## 验收标准

    approval/reject/timeout 可解释；至少一个 tool scenario；unified runtime 无 direct handler；同 key 不重复执行。

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
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_tool_control_plane.py','tests\agent\runtime\test_runtime_tool_idempotency.py','tests\agent\test_tool_control_plane_runtime.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'tool runtime tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    保留旧 adapter 回滚。side-effect 无审批/幂等不得进默认产品路径。

    ## 文档与状态同步

    更新 capability/tool Current/Partial 与 trace event。

    ## 完成记录

    - `ToolStepExecutor` 已从 intent-only baseline 升级为调用 `ToolControlPlaneRuntime`。
    - Read-only tool 会自动执行并输出 `NormalizedObservation(kind=tool)`、sandbox audit、tool result trace metadata。
    - Side-effect tool 会进入 `approval_waiting` interrupt；resume 时先通过 `SQLiteAgentRunStore.claim_tool_execution` claim idempotency key，再以 approved request 执行一次。
    - denied / network blocked 会转为 `TOOL` blocked observation，不直接抛成 fake success。
    - vertical slice 覆盖：`filesystem.read` 只读本地、`mail.send` 外部副作用 approval/resume、`mail.send` 非 mail egress blocked。
    - 产品 API/UI 仍未切换到 unified runtime；GeneralAgent 旧 handler path 的产品切换属于 PHASE11。

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
