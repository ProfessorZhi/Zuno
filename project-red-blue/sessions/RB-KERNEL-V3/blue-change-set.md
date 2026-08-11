# RB-KERNEL-V3 Blue Change Set

本文件记录红队后允许进入正式架构的最小变更。创建时尚未同步 Canonical 文档；Commit SHA 在验证后回填。

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-003
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/decisions/0008-legal-domain-kernel-and-host-boundary.md; docs/project/architecture/architecture.md
Applied Commit SHA: d264dbd
Validation Run: architecture/document/module verifier suite passed; no Runtime implementation performed
Retest IDs: RETEST-001

Decision: 保留最小 Legal Domain Kernel 作为可审计业务状态契约；不把完整法律对象列表或 Native Runtime 当作 Current。默认 Host + Legal Backend，Native Runtime 只保留可逆 benchmark 变体。

## CHANGE-002

Source Cluster IDs: CLUSTER-004, CLUSTER-005, CLUSTER-006, CLUSTER-007, CLUSTER-008
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/project/modules/01-product-surface.md; docs/project/modules/03-knowledge-agentic-graphrag.md; docs/project/modules/05-memory-context.md; docs/project/modules/06-agent-core-planning-control.md; docs/project/modules/07-capability-skill.md; docs/project/modules/08-tool-runtime.md; docs/project/modules/09-security.md; docs/project/modules/10-observability-eval.md; docs/project/modules/11-infrastructure.md
Applied Commit SHA: d264dbd
Validation Run: architecture/document/module verifier suite passed; no Runtime implementation performed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: Graph、Persistent Multi-Agent、Long-term Memory、自研 Tool Runtime、微服务拆分、安全优越性和法律质量优越性均不得作为无证据默认；改为 conditional/optional/deferred，并冻结 A/B/C 及安全评测协议。
