# PHASE03_model-gateway-closure

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE03
    state: planned
    title: Model Gateway 统一入口
    depends_on: PHASE02
    next_phase: PHASE04

    ## 目标

    把 planner、executor、critic、synthesis、tool-call 的所有真实模型调用收口到可追踪、可预算、可 fallback 的 Model Gateway。

    ## 当前事实

    GeneralAgent 仍通过 LLMService + ModelManager 获得模型；其他模块可能直接调用 ModelManager/provider。

    ## 目标增量

    Gateway 提供 `get_chat_model(binding, role)` 与 `invoke/astream(ModelCallRequest)`；每次调用输出 usage、latency、provider/model、role、fallback、error 和 trace。

    ## 代码落点

    ```text
src/backend/zuno/platform/model_gateway.py
src/backend/zuno/platform/model_roles.py
src/backend/zuno/agent/core/agents/general_agent.py
tests/platform/test_model_gateway.py
tools/scripts/verify_model_gateway_boundaries.py
```

    ## 实施步骤

    1. 审计所有模型构造/调用。
2. 定义 planner/executor/critic/synthesis/tool_call roles。
3. ModelCallRequest 带 run/task/trace、role、timeout、budget、slot。
4. GeneralAgent 改为注入 gateway。
5. 新 runtime nodes 只用 gateway protocol。
6. legacy ModelManager 只保留 adapter。
7. timeout/fallback 失败码统一。
8. usage/cost 写 runtime event。
9. verifier 阻止新增 direct call。

    ## 关键代码草图

    ```python
class ModelRole(str, Enum):
    PLANNER="planner"; EXECUTOR="executor"; CRITIC="critic"
    SYNTHESIS="synthesis"; TOOL_CALL="tool_call"

class ModelGateway(Protocol):
    async def invoke(self, request: ModelCallRequest) -> ModelCallResponse: ...
    async def get_chat_model(self, binding, role: ModelRole): ...
```

    ## 测试

    role routing、slot/fallback、timeout/provider error、usage/cost trace、GeneralAgent regression、direct-call verifier。

    ## 验收标准

    新增模型调用无绕过；GeneralAgent baseline 保持；role 调用可用；fallback 可解释；secret 不入 trace。

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
& $Python 'tools\scripts\verify_model_gateway_boundaries.py'
if ($LASTEXITCODE -ne 0) { throw 'model gateway boundary verification failed' }
$Targets=@('-m','pytest','-q','tests\platform\test_model_gateway.py','tests\agent\runtime\test_runtime_model_roles.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'model gateway tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    适配困难时先做 LegacyModelManagerGatewayAdapter，但 GeneralAgent 仍依赖 gateway 接口。缺真实 key 时 smoke=blocked。

    ## 文档与状态同步

    只有 verifier 和真实调用链都收口后才将 Model Gateway 写 Current。

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
