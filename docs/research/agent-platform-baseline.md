# Generic Agent Platform Baseline

> status: time-sensitive-research-reference
> last_verified: 2026-08-27
> reverify_before_architecture_claim: true

本文件用于回答：**WorkBuddy / Dify / Coze / LangGraph 等通用平台已经解决了什么，Zuno 哪些能力不应该重复造？**

它不是采购结论，也不是永久 Feature Matrix。平台变化很快；任何超过当前核验周期的结论都必须回到官方文档重新确认。

## 结论先行

Zuno 不应再用下面这些泛化说法作为差异化：

- “通用平台没有持久化”；
- “通用平台没有企业权限”；
- “通用平台不能长期运行”；
- “通用平台没有 RAG / Memory / Eval / Trace”；
- “我们有 Workflow / GraphRAG / MCP，所以比平台高级”。

成熟 Agent 平台已经覆盖大量通用 orchestration 与 enterprise plumbing。Zuno 的比较重点应该从 **Can platform implement it?** 转成 **Should platform own this semantic authority?**

## Generic capability baseline

以下能力默认优先 `ADOPT / INTEGRATE / EXTEND`，而不是 Zuno 自研：

- Conversation / Agent workspace；
- Workflow / DAG / Graph execution；
- Tool Calling / MCP transport；
- Checkpoint / resume / human interrupt；
- generic session / memory；
- generic RAG pipeline；
- model SDK / adapter；
- vector / graph / search infrastructure；
- Identity / SSO / RBAC / Secret infrastructure；
- tracing / observability backend；
- generic Eval harness / dataset runner。

不同平台的具体企业能力、部署模式和 SLA 必须按当前官方版本重新核验。

## Zuno 应该 Own 的候选语义

通用平台可以 Host、Invoke、Persist 这些状态，但不会天然替 Zuno 定义：

- Legal `DocumentVersion` 与当前任务材料集合；
- Knowledge 是否满足当前 Task 的 Readiness；
- `EvidenceCandidate` 与 Formal Evidence 的业务边界；
- conflicting Evidence 如何同时存在与后续解释；
- `Finding / HumanDecision / WorkProduct` 的正式生命周期；
- Provider 对某个专业 Capability / Task Class 的 qualification；
- Research artifact version / provenance；
- Domain state 与 Runtime state 的 Authority 分离；
- Tool attempt 与真实外部 Effect truth 的分离；
- 新证据怎样导致旧正式结果 stale / review-required；
- 哪些法律 Eval / failure taxonomy 决定一个研究能力能否进入生产路径。

关键不是“平台不能实现”。平台完全可以通过 Plugin / Skill / API / Workflow Node 接入这些语义。

更准确的结论是：

> **平台可以承载语义，但通用平台本身不应成为 Zuno 法律业务和研究能力语义的隐式 Authority。**

## WorkBuddy / Dify / Coze / LangGraph 的比较方式

不要只列 Feature Checklist。每次平台比较至少回答：

1. 平台最核心解决的问题是什么？
2. 它已经成熟覆盖哪些 commodity / generic agent primitives？
3. Zuno 哪些当前实现如果重复这些 primitive，应该删或变薄？
4. Zuno 的哪项需求是领域 semantic ownership，而不是平台 feature gap？
5. 如果平台明天补齐某个 primitive，Zuno 哪一层应该退出？

### WorkBuddy

研究重点：Agent Host、长期任务、MCP / Action、Memory、企业身份与治理、Trace / Eval 等能力。不能再把“WorkBuddy 只是 Coding Assistant”作为默认前提。

### Dify

研究重点：Agentic Workflow、RAG / Knowledge Pipeline、Tool / Model integration、自托管与企业治理。Zuno 不应重造 generic knowledge plumbing 只为证明差异化。

### Coze

研究重点：Agent / Workflow / Knowledge / Plugin / Model Service 以及 Eval / Trace 能力。平台拥有 Eval tooling 不等于它拥有 Zuno 的法律 Dataset / Qualification policy。

### LangGraph / LangSmith

研究重点：Graph execution、checkpoint、pause/resume、human-in-the-loop、fault-tolerance primitives 与 generic evaluation。Zuno Runtime 只有在 domain-aware control semantics 不能由 Generic Host + Legal Backend 清楚承载时才值得扩展。

## Build / Buy / Extend baseline

| 能力 | 默认方向 |
| --- | --- |
| Agent Host / Workspace | ADOPT / INTEGRATE |
| Workflow / Checkpoint / HITL | ADOPT；不足时 EXTEND |
| Queue / DB / Vector / Graph Store | BUY / ADOPT |
| OCR / Embedding / Generic Rerank | BUY / ADOPT |
| MCP / Tool protocol | ADOPT |
| Generic RAG plumbing | ADOPT |
| Generic Model SDK | ADOPT |
| Identity / SSO / Secret / Policy infra | BUY / ADOPT |
| Observability backend | ADOPT |
| Generic Eval harness | ADOPT |
| Research Capability semantics | BUILD |
| Scoped Provider Qualification | BUILD semantic layer |
| Legal material / evidence provenance | BUILD |
| Candidate → Formal Domain | BUILD |
| WorkProduct invalidation / history | BUILD |
| Domain-specific Effect reconciliation | EXTEND / BUILD semantic layer |
| Native Runtime | MEASUREMENT-GATED / DEFER / DELETE if unnecessary |
| GraphRAG default path | MEASUREMENT-GATED |

## 最难的面试问题

> 如果明天 WorkBuddy 已经拥有 durable workflow、human approval、MCP、memory、RAG、evaluation、multi-agent、checkpoint 和 enterprise identity，Zuno 为什么仍然存在？

当前最可信的回答不是“法律行业特殊”，而是：

> Zuno 仍然需要拥有研究能力的专业语义与资格、材料/证据的版本和来源、Candidate 到 Formal Business Fact 的 Authority、正式 WorkProduct 的生命周期，以及领域 Effect / Security / Evaluation decision semantics。WorkBuddy 可以成为 Host；如果它的 Runtime primitives 已经满足长期恢复，Zuno Native Runtime 就应该缩小甚至删除。

这仍需通过 Generic Host vs Zuno Legal Backend vs Native Runtime 的真实对照 Evidence 验证。
