# Round-004 Architecture Deltas

本表只记录经过 Red → Blue → Counter reasoning 后可进入 Canonical Target 的稳定澄清。没有
把任何一项写成 Current，也没有关闭历史 P0。

## D001 Overall Architecture

- Source Questions: Q001–Q012
- Affected Canonical Docs: architecture.md、domain-state-lifecycle.md、data-ownership-and-recovery.md
- Part A Impact: reviewed Domain/Runtime/Host closure and recovery narrative; existing text remains sufficient
- Part B Impact: existing version、receipt、reconciliation contracts remain sufficient
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D002 Product Surface

- Source Questions: Q013–Q018
- Affected Canonical Docs: product-architecture.md
- Part A Impact: rewrite product narrative around stale WorkProduct and Review delivery
- Part B Impact: retain delivery/review contract
- Document Impact: PART_A
- Apply Mode: FULL_PART_REWRITE

## D003 Input / Document Ingestion

- Source Questions: Q019–Q025
- Affected Canonical Docs: knowledge-evidence-architecture.md
- Part A Impact: no independent stable narrative delta
- Part B Impact: retain identity、partial parsing、ACL and job idempotency
- Document Impact: PART_B
- Apply Mode: NO_CHANGE

## D004 Knowledge / Agentic GraphRAG

- Source Questions: Q026–Q036
- Affected Canonical Docs: knowledge-evidence-architecture.md
- Part A Impact: conditional Graph and citation freshness remain explicit
- Part B Impact: preserve projection generation and evidence gate
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D005 Model Gateway

- Source Questions: Q037–Q042
- Affected Canonical Docs: agent-platform.md
- Part A Impact: no new stable narrative claim
- Part B Impact: keep provider normalization and budget receipt
- Document Impact: PART_B
- Apply Mode: NO_CHANGE

## D006 Memory & Context

- Source Questions: Q043–Q050
- Affected Canonical Docs: agent-platform.md、data-ownership-and-recovery.md
- Part A Impact: keep Memory as candidate context, not Domain truth
- Part B Impact: promotion、expiry、scope and replay idempotency
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D007 Agent Core / Planning & Control

- Source Questions: Q051–Q064
- Affected Canonical Docs: agent-platform.md、multi-agent-runtime.md、domain-state-lifecycle.md
- Part A Impact: rewrite was not required because existing narrative already states single control authority
- Part B Impact: explicit Replan Barrier and Domain/Checkpoint reconciliation
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D008 Capability / Skill

- Source Questions: Q065–Q070
- Affected Canonical Docs: agent-platform.md、legal-domain-model.md
- Part A Impact: provider remains replaceable and proposal-only
- Part B Impact: preserve capability contract and admission
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D009 Tool Runtime

- Source Questions: Q071–Q080
- Affected Canonical Docs: security-architecture.md、data-ownership-and-recovery.md
- Part A Impact: no new stable narrative claim
- Part B Impact: retain EffectReceipt、unknown outcome and reconciliation
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D010 Security

- Source Questions: Q081–Q088
- Affected Canonical Docs: security-architecture.md
- Part A Impact: no new stable narrative claim
- Part B Impact: preserve execute-time authorization and SecurityEpoch
- Document Impact: BOTH
- Apply Mode: NO_CHANGE

## D011 Observability & Eval

- Source Questions: Q089–Q094
- Affected Canonical Docs: legal-eval-and-benchmark.md
- Part A Impact: rewrite evaluation narrative around causal claims and incomparable outcomes
- Part B Impact: preserve A/B/C and failure classification
- Document Impact: BOTH
- Apply Mode: FULL_PART_REWRITE

## D012 Infrastructure

- Source Questions: Q095–Q100
- Affected Canonical Docs: microservice-deployment.md、service-architecture.md
- Part A Impact: rewrite deployment narrative around rolling upgrade and queue drain
- Part B Impact: keep compatibility、backpressure and evidence boundary
- Document Impact: BOTH
- Apply Mode: FULL_PART_REWRITE
