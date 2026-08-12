# Round-003 Architecture Deltas

Each delta is a traceable document synchronization unit; it does not create runtime, schema or fact changes.

## D001

- Delta: D001
- Lens: 00 Overall Architecture
- Source Questions: Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012
- Affected Canonical Docs: docs/project/architecture/architecture.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q001
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.
## D002

- Delta: D002
- Lens: 01 Product Surface
- Source Questions: Q013, Q014, Q015, Q016, Q017, Q018
- Affected Canonical Docs: docs/project/product/product-architecture.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q013
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D003

- Delta: D003
- Lens: 02 Input / Document Ingestion
- Source Questions: Q019, Q020, Q021, Q022, Q023, Q024, Q025
- Affected Canonical Docs: docs/project/knowledge/knowledge-evidence-architecture.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q019
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D004

- Delta: D004
- Lens: 03 Knowledge / Agentic GraphRAG
- Source Questions: Q026, Q027, Q028, Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036
- Affected Canonical Docs: docs/project/knowledge/knowledge-evidence-architecture.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q026
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D005

- Delta: D005
- Lens: 04 Model Gateway
- Source Questions: Q037, Q038, Q039, Q040, Q041, Q042
- Affected Canonical Docs: docs/project/agents/agent-platform.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q037
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D006

- Delta: D006
- Lens: 05 Memory & Context
- Source Questions: Q043, Q044, Q045, Q046, Q047, Q048, Q049, Q050
- Affected Canonical Docs: docs/project/agents/agent-platform.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q043
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D007

- Delta: D007
- Lens: 06 Agent Core / Planning & Control
- Source Questions: Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q059, Q060, Q061, Q062, Q063, Q064
- Affected Canonical Docs: docs/project/agents/agent-platform.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q051
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D008

- Delta: D008
- Lens: 07 Capability / Skill
- Source Questions: Q065, Q066, Q067, Q068, Q069, Q070
- Affected Canonical Docs: docs/project/agents/agent-platform.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q065
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D009

- Delta: D009
- Lens: 08 Tool Runtime
- Source Questions: Q071, Q072, Q073, Q074, Q075, Q076, Q077, Q078, Q079, Q080
- Affected Canonical Docs: docs/project/security/security-architecture.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q071
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D010

- Delta: D010
- Lens: 09 Security
- Source Questions: Q081, Q082, Q083, Q084, Q085, Q086, Q087, Q088
- Affected Canonical Docs: docs/project/security/security-architecture.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q081
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D011

- Delta: D011
- Lens: 10 Observability & Eval
- Source Questions: Q089, Q090, Q091, Q092, Q093, Q094
- Affected Canonical Docs: docs/project/eval/legal-eval-and-benchmark.md
- Part A Impact: Narrative boundary, scenario, ownership, tradeoff or reversal was audited.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: BOTH
- Apply Mode: AUTO_APPLY
- Trace: Q089
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.

## D012

- Delta: D012
- Lens: 11 Infrastructure
- Source Questions: Q095, Q096, Q097, Q098, Q099, Q100
- Affected Canonical Docs: docs/project/deployment/microservice-deployment.md
- Part A Impact: No Part A rewrite required by the scored questions.
- Part B Impact: Detailed Contract, state/version, failure, recovery, security or verification was audited.
- Document Impact: PART_B
- Apply Mode: AUTO_APPLY
- Trace: Q095
- Decision Summary: Keep only the Target/document refinement that survives the same-file Part A/Part B quality gate; do not promote Current or Production evidence.
- Reversal Condition: If a simpler document or implementation passes the same scenario, ownership, safety, recovery, quality and cost test, simplify or externalize the affected boundary.
