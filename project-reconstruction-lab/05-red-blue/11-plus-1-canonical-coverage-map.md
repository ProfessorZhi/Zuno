# 11+1 Historical Coverage Map

status: superseded-legacy-reference
canonical_role: History / coverage audit only; not an active architecture taxonomy
current_architecture_entry: `docs/project/architecture/architecture.md`

本文件定义 Review Lens 到新 Canonical Owner 文档的映射。它不是第二套架构 taxonomy，也不
把 Lens 变成 Service；Contract Ownership 仍以对应 Owner 文档为准。

| Review Lens | Canonical Owner Doc(s) | 核心问题 |
|---|---|---|
| 00 Overall Architecture | `docs/project/architecture/architecture.md`、`architecture-views.md` | 跨层 Product、Domain、Logical Capability、Service、Data、Security、Eval 如何闭环？ |
| 01 Product Surface | `docs/history/superseded-document-taxonomy/project-topics/product/product-architecture.md` | 用户、Host、Matter、Review、WorkProduct 的边界是什么？ |
| 02 Input / Document Ingestion | `docs/history/superseded-document-taxonomy/project-topics/domain/legal-domain-model.md`、`docs/history/superseded-document-taxonomy/project-topics/knowledge/knowledge-evidence-architecture.md` | 文档版本和来源如何进入可追溯证据链？ |
| 03 Knowledge / Agentic GraphRAG | `docs/history/superseded-document-taxonomy/project-topics/knowledge/knowledge-evidence-architecture.md`、`docs/history/superseded-document-taxonomy/project-topics/eval/legal-eval-and-benchmark.md` | Projection、Retrieval、Graph、Citation 如何证明有价值？ |
| 04 Model Gateway | `docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md`、`docs/history/superseded-document-taxonomy/project-topics/services/service-architecture.md` | Model Provider、Quota、Fallback 和 Gateway 是否需要独立边界？ |
| 05 Memory & Context | `docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md`、`docs/history/superseded-document-taxonomy/project-topics/data/data-ownership-and-recovery.md` | Memory 如何受 Scope、Write/Recall/Promotion Gate 约束？ |
| 06 Agent Core / Planning & Control | `docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md`、`docs/history/superseded-document-taxonomy/project-topics/agents/multi-agent-runtime.md` | Plan、DAG、Parallel、Reflection、Replan、Checkpoint 如何执行和恢复？ |
| 07 Capability / Skill | `docs/history/superseded-document-taxonomy/project-topics/agents/agent-platform.md`、`docs/history/superseded-document-taxonomy/project-topics/domain/legal-domain-model.md` | Skill、Capability、Provider、Proposal 和 Canonical Mutation 如何分开？ |
| 08 Tool Runtime | `docs/history/superseded-document-taxonomy/project-topics/security/security-architecture.md`、`docs/history/superseded-document-taxonomy/project-topics/services/service-architecture.md` | PreparedAction、Approval、EffectReceipt、Unknown Effect 如何闭环？ |
| 09 Security | `docs/history/superseded-document-taxonomy/project-topics/security/security-architecture.md` | Authorization、Secret、Sandbox、Egress、Audit 如何可验证？ |
| 10 Observability & Eval | `docs/history/superseded-document-taxonomy/project-topics/eval/legal-eval-and-benchmark.md`、`docs/project/status/production-readiness.md` | 质量、效率、安全和复杂度收益如何公平测量？ |
| 11 Infrastructure | `docs/history/superseded-document-taxonomy/project-topics/services/service-architecture.md`、`docs/history/superseded-document-taxonomy/project-topics/data/data-ownership-and-recovery.md`、`docs/history/superseded-document-taxonomy/project-topics/deployment/microservice-deployment.md` | 服务、Worker、Queue、Storage、部署和恢复如何隔离？ |

## Owner rule

例如 `PlanVersion` 的状态由 Agent Runtime Owner 定义，Data 文档只说明物理保存和恢复；
`CitationLineage` 的语义由 Knowledge Owner 定义，Eval 文档只引用其指标和验证。重复出现的
名称不是重复 Owner。
