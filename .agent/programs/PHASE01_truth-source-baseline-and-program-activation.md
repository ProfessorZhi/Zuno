# PHASE01_truth-source-baseline-and-program-activation

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE01
    state: completed
    title: 事实源、基线与 Program 激活
    depends_on: none
    next_phase: PHASE02

    ## 目标

    建立不可争议的起点：确认当前 HEAD、三套 Agent runtime 的真实调用边界、Memory/Tool/Retrieval/Trace 已有能力、benchmark truth source、PowerShell 命令和 sample case set。此 Phase 不修改生产 runtime。

    ## 当前事实

    当前仓库有真实 `GeneralAgent.create_agent()` ReAct、规则式 `StrategySelector/AgentControlRuntime`、模拟节点的 `SingleControllerDurableRuntime`。MemoryEngine、ToolControlPlaneRuntime、Agentic GraphRAG contracts 已存在，但统一产品闭环和 measured gate 未完成。

    ## 目标增量

    输出可机器核对的 baseline manifest，冻结 current HEAD、runtime call chain、direct model call inventory、产品入口、持久化 owner、fixed benchmark runner/config/dataset、sample-8 与 paired case ids、failure semantics 和 regression tests。

    ## 代码落点

    ```text
.agent/programs/baseline-manifest.md
.agent/references/current-program.md
.agent/system.yaml
tools/scripts/verify_current_program.py
tests/repo/test_current_program_contract.py
```
不要修改 `src/backend/zuno/**`。

    ## 实施步骤

    1. 读取全部 canonical architecture 和 workflow。
2. 记录 HEAD、branch、dirty state。
3. 搜索 `create_agent`、ModelManager/direct SDK、AgentControlRuntime、SingleControllerDurableRuntime 调用点。
4. 确认 Completion API 和 Workspace task 真实入口。
5. 找到 fixed EnterpriseRAG dataset、runner、profile config、report、release gate 唯一 owner。
6. 选择 sample-8：exact lookup、multi-hop、graph relation、citation miss、conflict、PDF、tool、abstain。
7. 固定 sample-80 或仓库固定全集；不足则记录 blocked。
8. 运行当前 focused suites并记录结果。
9. 激活 current.md、roadmap、references、system/verifier。
10. 提交仅 program/workflow 变更。

    ## 关键代码草图

    ```yaml
baseline_manifest:
  program: zuno-unified-agent-runtime-closure-v1
  baseline_commit: <actual HEAD>
  product_entrypoints:
    completion_service: <path:function>
    workspace_runtime: <path:function>
  agent_runtimes:
    react: <path:class>
    planning_control: <path:class>
    durable: <path:class>
  model_call_inventory:
    - path: <path>
      owner: gateway | legacy
  benchmark:
    dataset: <path>
    runner: <path>
    profile_config: <path>
    release_gate: <path>
    sample_8_case_ids: [...]
    paired_case_ids: [...]
```

    ## 测试

    - verifier 检查 active_program/current_phase。
- manifest 中所有 path 必须存在。
- sample ids 可在 dataset 中解析。
- no-active guardrail 切换为 active。
- 当前 focused suites 作为 regression baseline。

    ## 验收标准

    Program 正确激活；manifest 可读；无生产 runtime 修改；没有把未运行 benchmark 写 measured；PowerShell 命令可复制。

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
git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'cannot read HEAD' }
& $Python 'tools\scripts\verify_docs_entrypoints.py'
if ($LASTEXITCODE -ne 0) { throw 'docs verifier failed' }
& $Python -m pytest -q 'tests\repo\test_docs_entrypoints.py' -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw 'repo docs tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    任何路径或 benchmark owner 不确定时保持 Phase active 并记录 blocked；不得凭文档猜测。

    ## 文档与状态同步

    同步 current、roadmap、closure、references、system.yaml、verifier/tests。

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
