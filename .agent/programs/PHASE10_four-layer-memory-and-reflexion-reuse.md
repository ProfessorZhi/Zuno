# PHASE10_four-layer-memory-and-reflexion-reuse

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE10
    state: planned
    title: 四层 Memory 与 Reflexion 复用闭环
    depends_on: PHASE09
    next_phase: PHASE11

    ## 目标

    把四层 Memory 真正接入统一 Agent 生命周期，并证明 approved Reflexion lesson 能影响后续 Strategy/Planning。

    ## 当前事实

    MemoryEngine 已有 raw event、summary、candidate、review、decay、consolidation、semantic search、privacy delete 和 GeneralAgent pre/post 接入，但 unified graph、Entity Memory 和未来任务复用未完整证明。

    ## 目标增量

    实现 Sensory/Short-term/Long-term/Entity 的真实读用写；ContextPack 记录 include/exclude；Reflexion candidate 审批后进 procedural/episodic，并影响下一相似任务。

    ## 代码落点

    ```text
src/backend/zuno/memory/{engine,entity,context_builder,reflexion}.py
src/backend/zuno/agent/runtime/nodes/{build_context,post_turn_commit}.py
src/backend/zuno/agent/runtime/planning/selector.py
tests/agent/runtime/test_runtime_memory_reflexion.py
tests/memory/test_entity_memory.py
tests/memory/test_memory_context_trace.py
```

    ## 实施步骤

    1. Context 按 policy/request/PlanState/entity/procedural/session/knowledge/tool 装配。
2. 每个 item 记录 source、priority、token、sensitivity、freshness、include/exclude reason。
3. Sensory/Short-term 不自动进入长期。
4. post-turn 保存 raw event/task summary。
5. 只在真实失败/verification feedback 生成 lesson。
6. candidate 绑定 trace/evidence/applicability/confidence/sensitivity。
7. review 后保存 procedural/episodic。
8. 下一相似任务主动检索 approved lesson。
9. selector trace `memory_influenced_strategy=true`。
10. Entity 以 scope+entity+attribute 为 authoritative key，支持 effective time/supersede。
11. Semantic 不双写 Entity authoritative fact。
12. privacy delete 清派生 refs。

    ## 关键代码草图

    ```python
class ReflexionCandidateBuilder:
    def build(self, *, state, failure, trace_refs):
        return MemoryCandidate(
            layer=MemoryLayer.PROCEDURAL,
            content=render_lesson(...),
            requires_review=True,
            source_event_ids=tuple(trace_refs),
            metadata={"failure_type":failure.code,"hidden_cot":False},
        )
```

    ## 测试

    four-layer 分类、include/exclude、sensitive block、pending 不检索、approved 检索、策略受影响、entity supersede、privacy delete、repeated failure。

    ## 验收标准

    真实 graph pre-read/post-write 可见；approved reuse 被证明；不保存隐藏 CoT；重启后可读。

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
$Targets=@('-m','pytest','-q','tests\agent\runtime\test_runtime_memory_reflexion.py','tests\memory\test_entity_memory.py','tests\memory\test_memory_context_trace.py','tests\agent\test_memory_durable_runtime.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'memory/reflexion tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    Entity 先做 SQLite baseline，不引入新图数据库。lesson 质量不稳时保持 pending，不 auto approve。

    ## 文档与状态同步

    不得把 candidate 创建写成 reuse completed；更新 memory Current/Partial。

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
