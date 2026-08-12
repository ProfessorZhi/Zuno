# Round-002 Architecture Deltas

## D001

- Delta ID: D001
- Source Questions: Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Overall architecture / Domain-State admission.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 00 Overall Architecture and adjacent linked lenses
- Affected Canonical Docs: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Overall architecture / Domain-State admission refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Overall architecture / Domain-State admission must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D002

- Delta ID: D002
- Source Questions: Q013, Q014, Q015, Q016, Q017, Q018
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Product Host boundary and delivery semantics.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 01 Product Surface and adjacent linked lenses
- Affected Canonical Docs: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Product Host boundary and delivery semantics refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Product Host boundary and delivery semantics must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D003

- Delta ID: D003
- Source Questions: Q019, Q020, Q021, Q022, Q023, Q024, Q025
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Ingestion provenance and idempotent publication.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 02 Input / Document Ingestion and adjacent linked lenses
- Affected Canonical Docs: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Ingestion provenance and idempotent publication refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Ingestion provenance and idempotent publication must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D004

- Delta ID: D004
- Source Questions: Q026, Q027, Q028, Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Conditional retrieval and citation lineage.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 03 Knowledge / Agentic GraphRAG and adjacent linked lenses
- Affected Canonical Docs: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Conditional retrieval and citation lineage refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Conditional retrieval and citation lineage must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D005

- Delta ID: D005
- Source Questions: Q037, Q038, Q039, Q040, Q041, Q042
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Model Provider and Gateway replaceability.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 04 Model Gateway and adjacent linked lenses
- Affected Canonical Docs: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Model Provider and Gateway replaceability refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Model Provider and Gateway replaceability must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D006

- Delta ID: D006
- Source Questions: Q043, Q044, Q045, Q046, Q047, Q048, Q049, Q050
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Memory Policy and provider boundary.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 05 Memory & Context and adjacent linked lenses
- Affected Canonical Docs: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Memory Policy and provider boundary refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Memory Policy and provider boundary must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D007

- Delta ID: D007
- Source Questions: Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q059, Q060, Q061, Q062, Q063, Q064
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in PlanVersion, DAG, reflection and runtime recovery.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 06 Agent Core / Planning & Control and adjacent linked lenses
- Affected Canonical Docs: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the PlanVersion, DAG, reflection and runtime recovery refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, PlanVersion, DAG, reflection and runtime recovery must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D008

- Delta ID: D008
- Source Questions: Q065, Q066, Q067, Q068, Q069, Q070
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Capability Contract and legal provider governance.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 07 Capability / Skill and adjacent linked lenses
- Affected Canonical Docs: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Capability Contract and legal provider governance refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Capability Contract and legal provider governance must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D009

- Delta ID: D009
- Source Questions: Q071, Q072, Q073, Q074, Q075, Q076, Q077, Q078, Q079, Q080, Q081, Q082, Q083, Q084, Q085, Q086, Q087, Q088
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Tool Effect, Approval and Security enforcement.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 08 Tool Runtime and adjacent linked lenses
- Affected Canonical Docs: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Tool Effect, Approval and Security enforcement refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Tool Effect, Approval and Security enforcement must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D010

- Delta ID: D010
- Source Questions: Q089, Q090, Q091, Q092, Q093, Q094
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Legal Eval, attribution and release gates.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 10 Observability & Eval and adjacent linked lenses
- Affected Canonical Docs: docs/project/eval/legal-eval-and-benchmark.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Legal Eval, attribution and release gates refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Legal Eval, attribution and release gates must be reduced or externalized.
- Gap Type: MEASUREMENT_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
## D011

- Delta ID: D011
- Source Questions: Q095, Q096, Q097, Q098, Q099, Q100
- Red Findings: The source questions expose repeated ownership, state, failure or evidence ambiguity in Service, Queue, Storage and Deployment evidence.
- Blue Decisions: Refine the contract without changing the approved Python-only, Microservice, Single Controller or Domain-vs-Runtime principles.
- Affected 11+1 Lens: 11 Infrastructure and adjacent linked lenses
- Affected Canonical Docs: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- Before: Target language named the boundary but left one or more concrete counterexamples implicit.
- After: Canonical docs state the Service, Queue, Storage and Deployment evidence refinement, owner, state, recovery, evidence and reversal condition.
- Why: The refinement protects necessary complexity while removing accidental coupling and silent success.
- Complexity Added: A small contract, trace, gate or benchmark rule; no new runtime component is mandated.
- Complexity Removed: Unbounded retries, provider lock-in, duplicate state machines or unjustified service/database ownership.
- Tradeoff: More explicit metadata and tests increase design/validation work but reduce operational ambiguity.
- New Risk: Implementations may still diverge until the corresponding I/E/X evidence is produced.
- Reversal Condition: If the simpler provider/library/worker alternative passes the same scenario and benchmark, Service, Queue, Storage and Deployment evidence must be reduced or externalized.
- Gap Type: IMPLEMENTATION_GAP
- ADR Impact: NONE; existing ADR-0008 to ADR-0011 remain sufficient.
- Apply Mode: AUTO_APPLY
