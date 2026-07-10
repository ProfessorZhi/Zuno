# PHASE05_unified-langgraph-runtime-skeleton

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE05
    state: completed
    title: 统一 LangGraph Runtime 骨架
    depends_on: PHASE04
    next_phase: PHASE06

    ## 目标

    建立唯一 StateGraph 主控制器，支持 run、stream、conditional route、interrupt、resume、cancel 和 checkpoint。先接 deterministic/legacy adapter，再逐 Phase 替换为真实执行。

    ## 当前事实

    GeneralAgent 使用 create_agent；durable runtime 是顺序 for-loop；control runtime 不是 graph。三者无统一 state/route。

    ## 目标增量

    新增 UnifiedAgentRuntimeService，public API 为 start、stream、resume、cancel、get_snapshot。节点只通过 AgentRuntimeDependencies 调外部层。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/{graph,routing,service,checkpointer}.py
src/backend/zuno/agent/runtime/nodes/*.py
tests/agent/runtime/test_runtime_graph_routes.py
tests/agent/runtime/test_runtime_interrupt_resume.py
```

    ## 实施步骤

    1. 检查并锁定仓库 LangGraph 版本。
2. build_graph(dependencies, checkpointer)。
3. 节点覆盖 architecture Process。
4. route 使用 enum，不在 node 硬编码散落字符串。
5. 每节点前后 trace/checkpoint。
6. hard limits 在 routing 统一检查。
7. ASK_USER/approval 用 interrupt。
8. stream 转现有 Workspace/SSE event。
9. execute_step 可暂委托 legacy adapter，但不得生成 simulated result。
10. feature flag：测试开启、产品暂保持旧路径，PHASE11 切换。

    ## 关键代码草图

    ```python
def build_agent_graph(deps):
    graph = StateGraph(AgentRuntimeState)
    for name, node in deps.nodes.items():
        graph.add_node(name, node)
    graph.add_edge(START, "input_gate")
    graph.add_edge("input_gate", "build_context")
    graph.add_edge("build_context", "strategy_select")
    graph.add_conditional_edges("strategy_select", route_after_strategy)
    graph.add_conditional_edges("reflect", route_after_reflection)
    return graph.compile(checkpointer=deps.checkpointer)
```

    ## 测试

    direct route、react/plan route、RETRIEVE_MORE 回环、REWRITE 回环、approval interrupt/resume、hard limits、stream order、checkpoint、无 simulated marker。

    ## 验收标准

    请求可走完整 graph；resume 不重执行已完成节点；service API 稳定；禁止 fake success。

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
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_graph_routes.py','tests\agent\runtime\test_runtime_interrupt_resume.py','tests\agent\runtime\test_runtime_restart_persistence.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'unified graph tests failed' }
$Hits = Get-ChildItem -LiteralPath 'src\backend\zuno\agent\runtime' -Recurse -File | Select-String -Pattern 'status.*simulated'
if ($Hits) { throw 'simulated runtime marker remains' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    LangGraph API 不兼容时做 version-specific adapter，不把依赖升级和大重构混在一起。保留 feature flag 回滚。

    ## 文档与状态同步

    写明 unified graph skeleton available，但 Plan/Tool/Retrieval quality 仍 Partial。

    ## 完成记录

    - 已新增 `UnifiedAgentRuntimeService`，public API 为 `start`、`stream`、`resume`、`cancel`、`get_snapshot`。
    - 已新增 PHASE05 LangGraph topology builder：`build_agent_graph(dependencies, checkpointer)`，使用 `RuntimeNode` 和集中 route 函数表达 conditional route。
    - 已新增 `RuntimeGraphCheckpointer`，每个节点后写入 store-backed checkpoint 和 runtime event；approval / ask_user 进入 pending interrupt。
    - 已新增 deterministic runtime nodes，覆盖 input gate、context build、strategy、plan、execute、observe、evidence gate、claim binding、reflection、replan、rewrite、approval、interrupt、finalize、post-turn commit。
    - 已证明 SQLite-backed 新 service 实例可恢复 approval interrupt 并 resume 到完成；旧产品路径尚未切换，PHASE06/PHASE11 继续完成真实 Plan/ReAct execution 和 API/UI cutover。
    - 已移除旧 durable runtime 的 `status: simulated` marker，避免 deterministic adapter 被误读为 simulated success。

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
