# PHASE08_corrective-agentic-graphrag-and-evidence-ledger

    program: zuno-unified-agent-runtime-closure-v1
    phase: PHASE08
    state: completed
    title: Corrective Agentic GraphRAG 与 EvidenceLedger
    depends_on: PHASE07
    next_phase: PHASE09

    ## 目标

    把 retrieval routing/evidence/citation baseline 变成真实多轮 corrective retrieval：每轮证据进入 EvidenceLedger，质量门选择动作并回 execute_step。

    ## 当前事实

    现有 agentic_graphrag.py 有 mode/router/fusion/evidence/citation，但目标 QueryStrategy、Ledger、QualityVerdict、CorrectiveAction 尚未形成持久多轮闭环。

    ## 目标增量

    实现 AgenticRetrievalRuntime：NeedRetrieval、QueryStrategy、BM25/Vector/Graph、Fusion/Rerank、Ledger、quality verdict、corrective action 和 stop conditions。

    ## 代码落点

    ```text
src/backend/zuno/knowledge/agentic/{contracts,query_strategy,evidence_ledger,quality,corrective,runtime}.py
src/backend/zuno/knowledge/agentic_graphrag.py
src/backend/zuno/agent/runtime/execution/knowledge_step.py
tests/knowledge/test_evidence_ledger.py
tests/knowledge/test_corrective_retrieval_runtime.py
```

    ## 实施步骤

    1. EvidenceRecord 带 document_version、SourceSpan、round/query/retriever/scores/graph/selection/trace。
2. 按 version+span+text hash 去重。
3. QueryStrategy 支持 DIRECT/REWRITE/MULTI_QUERY/STEP_BACK/HYDE/ENTITY/RELATION。
4. 初期 deterministic；生成 query 可经 gateway。
5. Quality 输出 RELEVANT/AMBIGUOUS/IRRELEVANT/CONFLICTING/INSUFFICIENT_SPAN。
6. failure bucket 映射 action。
7. novelty 低、max rounds、budget、无安全动作时停止。
8. Graph 无 span 只能辅助。
9. Ledger 保存 Phase04 store。
10. KnowledgeQueryService 作为 adapter，不复制索引。

    ## 关键代码草图

    ```python
class CorrectiveRetrievalPolicy:
    def decide(self, verdict, bucket, history, budget):
        if budget.max_rounds_reached: return CorrectiveAction.ABSTAIN
        if verdict == "INSUFFICIENT_SPAN": return CorrectiveAction.FOCUSED_CITATION_RETRIEVE
        if bucket == "doc_miss": return first_unused("REWRITE","MULTI_QUERY","HYDE")
        ...
```

    ## 测试

    ledger dedupe/version、doc/text/citation miss actions、conflict、graph no span、low novelty/max rounds、restart、共享 evidence contract。

    ## 验收标准

    第一次不足能真实第二轮；第二轮 query/round 不同；Ledger 可 trace；loop 不无限；质量仍待 PHASE13。

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
$Targets=@('-m','pytest','-q','tests\knowledge\test_evidence_ledger.py','tests\knowledge\test_corrective_retrieval_runtime.py','tests\agent\runtime\test_runtime_graph_routes.py','-p','no:cacheprovider')
& $Python @Targets
if ($LASTEXITCODE -ne 0) { throw 'corrective retrieval tests failed' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff check failed' }
```

    ## 失败与回滚

    拆分风险大时保留 facade 逐类抽取，不能为了目录破坏 query path。

    ## 文档与状态同步

    更新 retrieval planner Current/Partial，benchmark 仍 blocked。

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

    ## 完成记录

    状态：completed，本地 runtime baseline available；fixed EnterpriseRAG paired benchmark 仍未 measured。

    已完成：

    - 新增 `zuno.knowledge.agentic` contracts、EvidenceLedger、RetrievalQualityGate、CorrectiveRetrievalPolicy 和 CorrectiveAgenticRetrievalRuntime。
    - EvidenceLedger 按 document version / source span / text hash 去重，Graph evidence 缺少 SourceSpan 时只能作为辅助证据，不能作为 strict citation。
    - `doc_miss`、`doc_hit_text_miss`、`text_hit_citation_miss`、conflicting / ambiguous / irrelevant verdict 可映射到 corrective action。
    - corrective runtime 可在第一轮不足时生成第二轮 query / strategy / round trace，并受 max rounds / novelty / action budget 停止条件约束。
    - `KnowledgeStepExecutor` 在注入 `knowledge_runtime` 时调用 corrective retrieval runtime，并把 rounds、final action、final verdict 和 ledger trace 写入 observation metadata；未注入依赖时保留 deterministic fallback。

    证据：

    - `pytest -q tests/knowledge/test_evidence_ledger.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/runtime/test_runtime_graph_routes.py -p no:cacheprovider`
    - `python -m compileall -q src/backend/zuno/knowledge/agentic src/backend/zuno/agent/runtime/execution/knowledge_step.py`

    未关闭：

    - 本 phase 不声称 fixed paired benchmark measured pass。
    - Reflection / Replan / Rewrite / grounded synthesis 的质量闭环仍属于 PHASE09。
