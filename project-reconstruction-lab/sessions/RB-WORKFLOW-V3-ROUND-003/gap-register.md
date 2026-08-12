# Round-003 Documentation Gap Register

These gaps are deliberately retained as gaps. They do not authorize Current, measured, or Production claims.

| Gap | Area | Status | Evidence Needed | Owner |
|---|---|---|---|---|
| DOC-R3-001 | 00 Overall Architecture | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/architecture/architecture.md |
| DOC-R3-002 | 01 Product Surface | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/product/product-architecture.md |
| DOC-R3-003 | 02 Input / Document Ingestion | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/knowledge/knowledge-evidence-architecture.md |
| DOC-R3-004 | 03 Knowledge / Agentic GraphRAG | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/knowledge/knowledge-evidence-architecture.md |
| DOC-R3-005 | 04 Model Gateway | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/agents/agent-platform.md |
| DOC-R3-006 | 05 Memory & Context | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/agents/agent-platform.md |
| DOC-R3-007 | 06 Agent Core / Planning & Control | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/agents/agent-platform.md |
| DOC-R3-008 | 07 Capability / Skill | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/agents/agent-platform.md |
| DOC-R3-009 | 08 Tool Runtime | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/security/security-architecture.md |
| DOC-R3-010 | 09 Security | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/security/security-architecture.md |
| DOC-R3-011 | 10 Observability & Eval | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/eval/legal-eval-and-benchmark.md |
| DOC-R3-012 | 11 Infrastructure | OPEN | Contract review, implementation trace, focused test or benchmark appropriate to the boundary | docs/project/deployment/microservice-deployment.md |

Open cross-cutting gaps:

- Court QA protocol and reviewer agreement are not present as runtime evidence.
- A/B/C quality, efficiency and cost comparison is still a Target benchmark.
- Security verifiability, no-egress, sandbox and cross-tenant evidence remain unexecuted.
- Service count, queue provider, graph provider and memory provider remain replaceable until workload and failure evidence justify a lock-in.
- Production readiness remains NOT_ESTABLISHED.
