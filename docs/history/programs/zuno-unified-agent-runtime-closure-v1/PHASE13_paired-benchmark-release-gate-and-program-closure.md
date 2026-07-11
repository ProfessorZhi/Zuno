# PHASE13_paired-benchmark-release-gate-and-program-closure

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE13
    state: completed
    title: Paired Benchmark、Release Gate 与 Program 收口
    depends_on: PHASE12
    next_phase: program-closure

    ## 目标

    用同一 fixed case set 证明 standard/deep/agentic measured 结果；完成 sample-8、sample-80、release gate、旧主路径退出和文档 Current 更新。

    ## 当前事实

    Agentic GraphRAG 仍是 implementation available / measurement blocked / quality not yet proven。只有完整 measured profile 可改变。

    ## 目标增量

    冻结 benchmark truth source、resume、profile completeness 和 gate。所有 profile 使用同 dataset/model/index/config。输出机器 report、failure buckets 和 pass/fail/blocked。

    ## 代码落点

    ```text
tools/evals/zuno/<existing owner paths>
tests/evals/test_enterprise_rag_release_gate.py
tests/e2e/test_unified_agent_product_scenario.py
docs/evidence/<measured report summary>
docs/architecture/production-readiness.md
docs/history/programs/zuno-unified-agent-runtime-closure-v1/
```

    ## 实施步骤

    1. 从 PHASE01 manifest 读取 dataset/runner/config/gate。
2. 修 profile 缺失却标 measured 的 bug。
3. profile 写 case counts 和 hashes。
4. 支持 resume，不覆盖成功 case。
5. sample-8 快速验证。
6. sample-80/固定全集 paired。
7. 计算 retrieval/generation/agent/product 指标。
8. profile 不完整 gate=blocked。
9. per-case failure bucket。
10. gate pass 后 unified default on；gate fail 诚实记录。
11. 跑 focused/full verifier/browser E2E。
12. 更新 docs/HTML。
13. program 归档并恢复 no-active。

    ## 关键代码草图

    ```python
class ProfileMeasurement(BaseModel):
    profile: Literal["standard","deep","agentic"]
    case_set_hash: str
    model_config_hash: str
    index_manifest_id: str
    expected_case_count: int
    completed_case_count: int
    failed_case_count: int
    blocked_case_count: int
    measured: bool

def evaluate_release_gate(report):
    if not report.all_profiles_complete_and_measured:
        return GateResult(status="blocked", reason="profile_incomplete")
    return compare_agentic_to_standard(report)
```

    ## 测试

    missing profile/incomplete/resume/same hashes/failure unavailable/sample-8/sample-80/thresholds/E2E/docs verifier。

    ## 验收标准

    measured 不伪造；report 可复现；gate 明确；program archive；若失败则 quality failed/not proven。

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
& $Python '<fixed-runner-path>' '--profile' 'standard,deep,agentic' '--case-set' 'sample-8' '--resume'
if ($LASTEXITCODE -ne 0) { throw 'sample-8 benchmark failed' }
& $Python '<fixed-runner-path>' '--profile' 'standard,deep,agentic' '--case-set' 'sample-80' '--resume'
if ($LASTEXITCODE -ne 0) { throw 'paired benchmark failed' }
$Targets=@('-m','pytest','-q','tests\evals\test_enterprise_rag_release_gate.py','tests\e2e\test_unified_agent_product_scenario.py','tests\repo\test_docs_entrypoints.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'release closure tests failed' }
& $Python 'tools\agent\render_architecture.py' '--check'
if ($LASTEXITCODE -ne 0) { throw 'architecture check failed' }
& $Python 'tools\scripts\verify_docs_entrypoints.py'
if ($LASTEXITCODE -ne 0) { throw 'docs verifier failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    provider/dataset/parser 不可用时 gate=blocked。agentic 低于 baseline 时保留报告，不改 case set 求 pass。

    ## 文档与状态同步

    更新所有 architecture Current/Target 和 HTML；归档 program，恢复 no-active。

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

    ## PHASE13 完成记录

    完成状态：`implementation_complete_measurement_blocked`。

    已完成：

    - 修复 profile 缺失却顶层标记 `measured` / `fixed_benchmark` 的 runner bug。
    - 增加 `profile_completeness`、profile case counts 和 case id hashes。
    - profile runner 配置不可用时，在 `allow_blocked=True` 下写出 blocked `metrics.json` / `report.md` / `failure_cases.md`。
    - sample-8 已运行，输出 `blocked_not_measured`。
    - sample-80 保持 blocked，因为仓库没有 tracked fixed 80-case set。
    - program 已归档，前台恢复 no-active。

    未完成：

    - fixed EnterpriseRAG paired benchmark measured pass。
    - release gate pass/fail 判断；当前 gate 是 blocked，不是 failed measured，也不是 passed。
