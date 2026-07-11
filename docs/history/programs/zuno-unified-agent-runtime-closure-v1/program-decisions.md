# Program Decisions

program: zuno-unified-agent-runtime-closure-v1
status: active
baseline_commit: 72488a25fde59bc5ef86b2b1c84f25d42cb946ca

## D1：不新建第二套 Agent 产品入口

`CompletionService` 和 Workspace task runtime 最终都调用同一个 `UnifiedAgentRuntimeService`。旧 `GeneralAgent` 作为过渡 ReAct adapter，不再是长期顶层 controller。

## D2：LangGraph 是状态编排骨架，不拥有其他层

Graph node 只调用 typed dependency：

```text
ModelGateway
MemoryEngine
KnowledgeRuntime
ToolControlPlaneRuntime
SecurityGates
TraceStore
AgentRunStore
```

检索、工具和 Memory 的具体实现不得复制进 node。

## D3：状态 contract 版本化

运行状态至少包含：

```text
state_version
run_id / task_id / thread_id / trace_id
request / context_pack / strategy
plan_state / current_step_id
observations / evidence_ledger
draft_answer / claim_set / citations
reflection / replan_count / revision_count
interrupt / final_answer / memory_commit
limits / usage / failure
```

任何持久化 snapshot 必须带 `state_version`，禁止依赖 Python 对象隐式 pickle。

## D4：先确定性 gate，再可选模型 critic

证据、SourceSpan、citation coverage、schema、tool status、安全和预算使用确定性检查。Model critic 只用于 completeness、逻辑一致性、相关性、faithfulness 和冲突说明。

## D5：Replan 必须改变轨迹

每次 replan 至少改变 query strategy、retrieval scope、retriever mix、graph traversal、tool selection、remaining step、acceptance criteria、model role 或 budget allocation之一。

## D6：Reflexion 进入 Governance，不直接写长期记忆

经验候选必须绑定 failure fact、trace/evidence refs、适用条件、置信度和 sensitivity。批准后进入 Episodic/Procedural Memory，并通过后续 ContextPack 影响 Strategy/Planning。

## D7：EvidenceLedger 是 Agentic Retrieval 的跨轮事实源

多轮检索不直接追加匿名 chunk list。每个 evidence record 必须能回答来源、文档版本、SourceSpan、检索轮次、query、retriever、fusion/rerank、选择原因、claim attribution 和 trace span。

## D8：本地优先不等于只用内存

近期持久化使用 SQLite/SQLModel 和 LocalObjectStore。Postgres、Redis、Milvus、Neo4j 不作为 blocker。

## D9：Windows PowerShell 是第一等执行环境

所有 program 文档中的命令必须兼容 Windows PowerShell 5.1：

- 不使用 `&&`。
- 不使用 `export VAR=...`。
- 不使用 `source .venv/bin/activate`。
- 不使用 `rm -rf`、`grep`、`sed`。
- 包含空格或 `&` 的路径必须使用 `Set-Location -LiteralPath`。
- 外部程序执行后检查 `$LASTEXITCODE`。
- 优先使用 `& $Python -m pytest`。
