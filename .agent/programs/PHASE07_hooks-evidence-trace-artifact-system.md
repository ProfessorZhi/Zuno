# PHASE07 Hooks Evidence Trace Artifact System

Program: `zuno-eight-deliverables-full-realization-v1`
status: completed

## 为什么

增强模式必须能回答“做了什么、为什么这么做、证据够不够、哪里 fallback、产物怎么复现”。Hooks、Evidence、Trace 和 Artifact 是把 Agent 行为从黑箱变成可审计系统的关键。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- pre-retrieval / post-retrieval / pre-tool / post-tool / post-answer hooks。
- Evidence Check、Citation Coverage、fallback reason。
- Trace event schema 和 artifact manifest。

## 执行步骤

1. 审计现有 observability、trace、citation、evidence 入口。
2. 定义事件 schema 和 artifact manifest。
3. 实现 hooks policy 与 runtime event emission 的 focused path。
4. 将 evidence coverage 与 citation check 接入 enhanced mode。
5. 增加 focused tests 和一份可复现 evidence report。

## 验收

- 每次增强路径能产生可读 trace。
- evidence check 不通过时有 fallback 或低置信说明。
- artifact manifest 能关联输入、检索、工具、证据和输出。
- docs/evals 能解释 trace 字段。

## PR 边界

建议拆成 schema PR、runtime hooks PR、evidence/artifact PR。

## 完成内容

- 新增 `RuntimeTraceEvent`、`RuntimeTraceBuilder`、`HookPoint`、`EvidenceChecker`、`EvidenceVerdict` 和 `TraceArtifactManifest` foundation contract。
- `GraphRAGQueryService` 会在 query result trace metadata 中补充 `runtime_trace_events`、`evidence_verdict` 和 `artifact_manifest`，并把低置信 evidence fallback reason 同步到 `KnowledgeQueryResult.fallback_reason`。
- `GeneralAgent` 的知识库工具会通过既有 custom event 通道发出 additive trace / evidence / artifact payload，并在工具返回文本里暴露低置信 evidence 状态。
- `EmitEventAgentMiddleware` 在既有 START / END / ERROR payload 内增加 `runtime_trace_event`，证明 pre-tool / post-tool hook foundation，不改变 SSE 外层 envelope。
- Multihop eval diagnostics 可解释 PHASE07 的 evidence verdict、artifact manifest trace id 和 runtime trace event count。

## 多 agent 审计结果

- Architecture / Docs Agent：确认 PHASE07 只能写成 focused enhanced path foundation，不能宣称 production-grade hooks、完整 middleware governance、产品 artifact delivery 或 frontend trace panel。
- Runtime / Code Agent：确认最短路径是 retrieval trace artifact contract、GraphRAG query result enrichment、GeneralAgent knowledge trace emission 和 additive tool hook payload，不改 API/DB/frontend。
- Verification Agent：确认 focused tests 应覆盖 hook schema、evidence verdict、artifact manifest、GeneralAgent event emission、API trace passthrough、eval diagnostics、facade/static guards。
- Integration Reviewer Agent：确认 stacked PR base 为 PHASE06，必须保持 SSE/API fields additive，并修复低置信 evidence fallback 只嵌套在 trace metadata 的风险。

## 验证

```powershell
pytest -q tests/agent/test_hooks_evidence_trace_artifacts.py tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/evals/test_multihop_eval_real_runtime_runner.py tests/repo/test_backend_facade_layers.py tests/repo/test_static_target_layer_imports.py tests/retrieval/test_enhanced_retrieval_composition.py tests/retrieval/test_retrieval_orchestrator.py -p no:cacheprovider
```

结果：40 passed。

## 风险与边界

- PHASE07 是 trace / evidence / artifact manifest foundation，不是完整 artifact storage、download flow、frontend trace panel 或 production-grade hooks governance。
- Custom event payload 和 tool middleware payload 均保持 additive；不改变 SSE 外层 envelope、API DTO、DB schema 或 frontend contract。
- 低置信 evidence fallback reason 会进入 top-level `KnowledgeQueryResult.fallback_reason`，但 retrieval fallback 与 evidence verdict fallback 仍在 trace metadata 中分开表达。
