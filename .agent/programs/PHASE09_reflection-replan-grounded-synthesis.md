# PHASE09_reflection-replan-grounded-synthesis

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE09
    state: planned
    title: Reflection、Replan、Rewrite 与 Grounded Synthesis
    depends_on: PHASE08
    next_phase: PHASE10

    ## 目标

    把 handcrafted observation 上的规则判断接入真实 graph：全部 Reflection 决策改变真实执行。

    ## 当前事实

    AgentControlRuntime 可检查 evidence/citation/tool failure 并生成新计划对象，但不会继续执行；GeneralAgent 无统一 final gate。

    ## 目标增量

    实现 ReflectionEngine、ReplanEngine、GroundedSynthesis：确定性 gate、可选 critic、draft/claims/citations、rewrite loop、replan plan diff、finalization gate。

    ## 代码落点

    ```text
src/backend/zuno/agent/runtime/reflection/{deterministic,critic,engine}.py
src/backend/zuno/agent/runtime/planning/replan.py
src/backend/zuno/agent/runtime/synthesis/{claims,citation_binding,grounded_answer}.py
tests/agent/runtime/test_runtime_reflection_replan.py
tests/agent/runtime/test_runtime_grounded_synthesis.py
```

    ## 实施步骤

    1. EvidenceGate 检查 count/span/coverage/conflict。
2. synthesis role 输出结构化 claims。
3. binder 只绑定 SourceSpan。
4. deterministic reflection 先执行。
5. 高质量策略才 critic。
6. REWRITE 保持 Ledger，不增加 retrieval round，重新 claim binding/reflection。
7. RETRIEVE_MORE 修改 strategy/scope/steps 并回 execute。
8. USE_TOOL 新增/修改 tool step。
9. ASK_USER interrupt。
10. ABSTAIN 合法结果。
11. 限制 revisions/reflections/replans。
12. trace 记录 old/new plan diff。

    ## 关键代码草图

    ```python
class ReflectionDecision(str, Enum):
    PASS="PASS"; REWRITE_ANSWER="REWRITE_ANSWER"
    RETRIEVE_MORE="RETRIEVE_MORE"; USE_TOOL="USE_TOOL"
    ASK_USER="ASK_USER"; ABSTAIN="ABSTAIN"

class ReplanEngine:
    def replan(self, state, decision):
        updated = copy_plan(state.plan_state)
        ...
        assert trajectory_diff(updated, state.plan_state)
        return updated
```

    ## 测试

    empty/citation/bad draft/rewrite/replan execution/max limits/critic unavailable/final metadata。

    ## 验收标准

    同一 request 经 first retrieval -> replan -> second execution -> PASS；rewrite 不直接 final；trace 可见 plan diff。

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
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_reflection_replan.py','tests\agent\runtime\test_runtime_grounded_synthesis.py','tests\agent\test_agent_control_runtime.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'reflection/replan tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    保留 AgentControlRuntime adapter；critic 不可用不得无限 retry。

    ## 文档与状态同步

    只有真实循环测试通过才写 replan execution available。

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
