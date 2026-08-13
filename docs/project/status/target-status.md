# Target Status

status: target-baseline
canonical_question: 当前重新设计的 Zuno Target 处于什么状态，什么仍需要验证或可以反转？
owner: Status / Evidence Owner
scope: Target Architecture，不把 Target 升级为 Current、Measured 或 Production

> Target 状态不是功能清单。`ACCEPTED_TARGET` 只表示方向已被当前架构治理接受；它不表示代码已经实现、收益已经测量或外部资格已经获得。

## 1. Product Thesis：Target，不是 Marketing Claim

```text
WorkBuddy / Dify 等通用 Agent Host
    主要解决通用 Agent 如何配置、运行、接入模型、Knowledge、Tool 和 Workflow。

Zuno 需要验证的问题
    高风险法律任务是否还需要维护可追溯、可复核、可持续更新、
    有明确业务状态 Owner 的法律工作结果。
```

因此 Zuno 的目标差异不是“功能更多”，而是验证 Legal Domain State、Evidence Dependency、Versioned Finding、Citation、Human Decision、Staleness、Controlled Side Effect 和 Legal Evaluation 是否能在复杂法律任务中产生可测量收益。

当前这只是 `TARGET PRODUCT THESIS`。不得写成“Zuno 已经比 WorkBuddy / Dify 更准、更安全或更高效”。

## 2. Target 能力状态矩阵

| 能力 / 边界 | 当前状态 | 说明与验证门 |
|---|---|---|
| Python-only / Python-first | `ACCEPTED_TARGET` | Owner 工程约束；当前仓库有 Python 表面，但不等于所有历史或生产链路已证明 |
| Microservice deployment direction | `ACCEPTED_TARGET` | 部署方向已确认；服务数量和边界仍需独立扩缩容、故障、安全和生命周期证据 |
| Legal Domain State | `ACCEPTED_TARGET` | 业务事实、版本、依赖、Review 和 Owner 的核心 Target；当前收益仍需复杂任务 Benchmark |
| Evidence semantics / Citation provenance | `ACCEPTED_TARGET` | 目标是区分材料、证据候选、引用和正式 Finding；完整法院 QA 尚未证明 |
| Legal Intelligence | `ACCEPTED_TARGET` | Event / Fact / Conflict / Fact–Article / Applicability 等能力采用 Provider Contract；历史集成边界未知 |
| Hybrid Retrieval | `ACCEPTED_TARGET` | 作为基础 Retrieval 组合；Recall、Citation 和成本仍需测量 |
| Agentic Retrieval | `PROPOSED` | 根据 Query Class、Evidence Requirement 和结果动态选择检索；需要 A/B 评测 |
| Agentic GraphRAG | `HYPOTHESIS` | Graph 只在关系型、跨文档或多证据链任务中条件启用；必须通过 Graph Kill Test |
| Hierarchical Memory | `PROPOSED` | Working / Session / Matter Context / Long-term / Reflexion Candidate 分层；Memory 不能成为 Canonical Legal Fact |
| OpenViking / Memory Provider | `DEFERRED` | Provider 可替换；需要替换测试和历史运行证据，不锁定具体实现 |
| Single Controller | `ACCEPTED_TARGET` | 默认先采用单控制器和受控 Plan / DAG；不是永久禁止 Worker 或 Multi-Agent |
| Controlled Multi-Agent | `PROPOSED` | 只用于独立上下文、权限、能力或资源确实不同的并行研究；必须与单 Agent + 并行工具比较 |
| Domain-aware Native Runtime | `HYPOTHESIS` | 只有 C 显著优于 B 才保留；否则降级为 Host + Legal Backend 或普通 Workflow |
| LangGraph | `DEFERRED` | 作为可替换 orchestration provider 候选；不拥有 CRUD 或 Canonical Domain State |
| Tool / MCP integration | `ACCEPTED_TARGET` | 外部互操作和能力执行边界；外部副作用需要授权、审批、幂等、Receipt 和对账 |
| Security / Permission | `ACCEPTED_TARGET` | 最小权限、Tenant / Matter 隔离、Policy Epoch、Audit 和执行时授权；安全优势仍未 attested |
| Sandbox | `PROPOSED` | 仅用于不可信 Shell / Code / Browser / File / Tool；需要边界、逃逸、无外联和资源限制测试 |
| Human Review / Human Decision | `ACCEPTED_TARGET` | 高风险 Finding、冲突和不可逆 Effect 的业务复核边界；尚无真实法院 Review 协议 |
| Legal Evaluation | `ACCEPTED_TARGET` | 必须同时测质量、效率、引用、支持率、成本、重试和状态复用；当前正式结果不足 |
| Model Gateway | `DEFERRED` | 是否独立服务、如何路由和降级需由 Provider 替换与运维证据决定 |
| Graph / Vector physical provider | `DEFERRED` | Neo4j、Milvus 等只作为 Provider 候选；不因当前依赖存在而固定 |
| Physical service count | `MEASUREMENT_BLOCKED` | `FINAL_MODULE_COUNT: NOT_DECIDED`；先按 Workload / Failure / Security / Scaling 证据收敛 |
| Production readiness | `NOT_ESTABLISHED` | 不属于 Target capability acceptance；必须由独立运行、安全、HA、Eval 和外部资格证明 |

## 3. 五层 Target Architecture View

这五层是责任视图，不是最终五个模块、服务或团队：

1. **Legal Work Surface**：案件分析、合同审查、法律研究、Finding、报告和 Human Review；
2. **Legal Domain & Intelligence**：Evidence、Fact / Event、Conflict、Dispute、Legal Issue、Fact–Article、Finding、Version 和 Staleness；
3. **Agentic Knowledge & Context**：Ingestion、Hybrid Retrieval、条件 Graph、Citation、Memory 和 Context Assembly；
4. **Agent Runtime & Execution**：Single Controller、Plan DAG、Step、ReAct、Reflection、Replan、受控 Worker、Model、Skill 和 Tool；
5. **Trust & Platform Engineering**：Permission、Approval、Sandbox、Audit、Observability、Eval 和 Infrastructure。

逻辑能力、物理服务、Worker、Process、Container、Database 和 Team 不做一一映射。最终服务数量保持 `NOT_DECIDED`。

## 4. WorkBuddy / Dify 与 A/B/C Kill Test

比较必须使用相同模型、原始语料、外部 Tool、相近 Prompt、Token 和时间预算：

```text
A — Generic Host + Legal Prompt / Skills
B — Generic Host + Zuno Legal Backend / Legal Capabilities
C — Zuno Native Runtime + First-class Domain State
```

- `B > A`：支持 Legal Backend / Legal Capability 有价值；
- `C ≈ B`：没有理由保留复杂 Native Runtime，应考虑 Host 作为主要宿主；
- `C > B`：才支持 Domain-aware Native Runtime 具有额外价值；
- `B ≈ A`：应删除没有产生收益的 Legal Backend 复杂度。

指标至少包括 Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict / Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls 和 Domain State Reuse Rate。

## 5. 反转条件

如果更简单的方案在同等数据、模型和预算下达到相同质量与恢复边界，必须缩减对应复杂度：

- Host + Legal Backend 足以完成任务：缩减 Native Runtime；
- Hybrid Retrieval 已覆盖关系型任务：Graph 降为条件 Provider；
- 单 Agent + 并行工具足够：不默认升级为 Persistent Multi-Agent；
- Matter DB + Checkpoint 足够：不额外维护不必要的 Memory 层；
- 模块化服务 + 独立 Worker 满足故障和资源隔离：合并服务；
- MCP / 现有 Sandbox 满足安全边界：不重复建设 Tool Runtime。

任何 reversal 都需要保留 Benchmark、Spike、故障测试或用户验证证据。
