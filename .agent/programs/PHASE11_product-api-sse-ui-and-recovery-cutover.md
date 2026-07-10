# PHASE11_product-api-sse-ui-and-recovery-cutover

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE11
    state: completed
    title: Product/API/SSE/UI 切换与恢复
    depends_on: PHASE10
    next_phase: PHASE12

    ## 目标

    将 Completion、Workspace task、SSE、approval、trace、artifact 和最小 UI 切换到统一 runtime，使用户一次请求真正走目标状态图。

    ## 当前事实

    CompletionService 当前调 GeneralAgent；Workspace runtime 有 durable/approval surface；两者需要统一。

    ## 目标增量

    产品入口统一为 UnifiedAgentRuntimeService；旧路径保留 feature flag 回滚。SSE 包含 node、step、retrieval round、approval、citation、finalization；刷新/重启可查询。

    ## 代码落点

    ```text
src/backend/zuno/api/services/completion.py
src/backend/zuno/api/services/workspace_task_runtime.py
src/backend/zuno/api/v1/completion.py
src/backend/zuno/agent/runtime/service.py
apps/web/<existing agent/workspace paths>
tests/api/test_completion_unified_runtime.py
tests/api/test_workspace_runtime_recovery.py
tests/e2e/test_unified_agent_product_scenario.py
```

    ## 实施步骤

    1. CompletionService 构造 runtime request/dependencies。
2. stream 转现有 SSE schema，兼容新增字段。
3. API 返回 run/task/thread ids。
4. approval API 按 interrupt id resume。
5. trace API 返回 node/step/evidence/tool/memory summary，敏感字段脱敏。
6. artifact/citation 使用 durable refs。
7. UI 显示 plan progress、approval、citation、trace。
8. refresh 按 run_id 重取。
9. restart test 用新 app/store 实例。
10. feature flag 灰度。
11. 旧 Workspace runtime 委托 unified service，不再独立模拟。

    ## 关键代码草图

    ```python
class CompletionService:
    async def stream_completion(self, request, actor):
        runtime_request = AgentRuntimeRequest.from_completion(request, actor)
        async for event in self.runtime.stream(runtime_request):
            yield CompletionEvent.from_runtime_event(event)
```

    ## 测试

    completion stream、approval/resume、citation/artifact、refresh/restart、legacy fallback、ACL、browser E2E、event order。

    ## 验收标准

    真实 UI/API request 走 unified graph；approval/trace 可见；restart 恢复；旧 simulated runtime 非主路径。

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
$Targets=@('-m','pytest','-q','tests\api\test_completion_unified_runtime.py','tests\api\test_workspace_runtime_recovery.py','tests\e2e\test_unified_agent_product_scenario.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'product integration tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    前端范围过大时先做 API/SSE 和最小 approval/trace UI，不重写全站。legacy flag 到 PHASE13 才决定默认关闭。

    ## 文档与状态同步

    更新 Scenario/Process Current、production-readiness 和 demo。

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

    ## PHASE11 完成记录

    状态：completed。

    本轮真实完成：

    - `CompletionService` 增加 `UnifiedAgentRuntimeService` cutover stream；`POST /completion` 在 `product_mode=unified_runtime` 或 `ZUNO_COMPLETION_UNIFIED_RUNTIME=1` 时输出 unified runtime SSE。
    - `WorkspaceTaskRuntimeService` 在 task 创建链路中启动 unified runtime，将 `runtime_started`、`runtime_node`、`runtime_completed` 写入现有 task event stream，并在 task snapshot 中暴露 `unified_runtime`。
    - Completion DTO 明确允许 `product_mode=unified_runtime`，避免 API schema 阻断 cutover 请求。
    - SQLite-backed unified runtime store 可由新 `UnifiedAgentRuntimeService` 实例按 task id 恢复 snapshot。
    - 旧 Workspace 产品事件序列仍可从非 runtime events 中稳定读取；runtime events 作为新增 trace 面出现。

    本轮没有声明完成：

    - 没有把 fixed EnterpriseRAG benchmark 写成 measured。
    - 没有声明全量前端 redesign 已完成；最小 UI 面是通过现有 SSE payload 增加 `runtime_topology`、`node`、`run_id` 和 runtime payload。
    - 没有关闭 PHASE12 的真实 PDF SourceSpan vertical slice。

    验证证据：

    ```text
pytest -q tests/api/test_completion_unified_runtime.py tests/api/test_workspace_runtime_recovery.py tests/e2e/test_unified_agent_product_scenario.py -p no:cacheprovider
4 passed

pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
8 passed

python -m compileall -q src/backend/zuno/api/services/completion.py src/backend/zuno/api/v1/completion.py src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/api/dto/completion.py
passed
```
