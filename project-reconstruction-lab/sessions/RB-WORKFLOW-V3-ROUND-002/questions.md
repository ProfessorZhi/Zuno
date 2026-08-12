# Round-002 Questions

Protocol: `ZUNO-RED-BLUE-WORKFLOW-V3`

## Q001

- Question ID: Q001
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: Product thesis acceptance
- Question: Given the approved Part-A Target, which measurable business problem would falsify the Legal Case Intelligence thesis before any service is built?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind Product thesis acceptance.
- Assumption Being Attacked: The current Target contract for Product thesis acceptance is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for Product thesis acceptance; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize Product thesis acceptance if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q002

- Question ID: Q002
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: Canonical state admission
- Question: A Provider returns a plausible FactProposal with three citations but no stable identity; exactly which gate prevents it becoming Canonical State?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind Canonical state admission.
- Assumption Being Attacked: The current Target contract for Canonical state admission is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for Canonical state admission; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize Canonical state admission if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q003

- Question ID: Q003
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: Owner registry drift
- Question: Domain and Data documents disagree about who owns DomainVersion; which document wins and how does the verifier detect drift?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind Owner registry drift.
- Assumption Being Attacked: The current Target contract for Owner registry drift is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for Owner registry drift; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize Owner registry drift if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q004

- Question ID: Q004
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: main runtime flow
- Question: A Run reaches Final Gate while one independent EvidenceRequirement is still pending; may the response be published?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind main runtime flow.
- Assumption Being Attacked: The current Target contract for main runtime flow is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for main runtime flow; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize main runtime flow if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q005

- Question ID: Q005
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: cross-state reconciliation
- Question: DomainVersion=D10, PlanVersion=P3, Checkpoint=C8 and EffectReceipt=R4 disagree after a crash; give the deterministic recovery order.
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind cross-state reconciliation.
- Assumption Being Attacked: The current Target contract for cross-state reconciliation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for cross-state reconciliation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize cross-state reconciliation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q006

- Question ID: Q006
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: new evidence invalidation
- Question: EvidenceVersion=E11 invalidates two Findings but a parallel branch is still running on E10; which branch result may be joined?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind new evidence invalidation.
- Assumption Being Attacked: The current Target contract for new evidence invalidation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-I
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for new evidence invalidation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize new evidence invalidation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q007

- Question ID: Q007
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: accepted target maturity
- Question: What exact evidence is still missing between ACCEPTED_TARGET and IMPLEMENTED, VERIFIED, MEASURED, and PRODUCTION_PROVEN?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind accepted target maturity.
- Assumption Being Attacked: The current Target contract for accepted target maturity is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for accepted target maturity; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize accepted target maturity if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q008

- Question ID: Q008
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: ordinary JSON alternative
- Question: If ordinary JSON plus PostgreSQL passes identity, provenance, CAS, review and stale tests, what part of a named Domain Kernel survives?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind ordinary JSON alternative.
- Assumption Being Attacked: The current Target contract for ordinary JSON alternative is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for ordinary JSON alternative; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize ordinary JSON alternative if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q009

- Question ID: Q009
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: host sufficiency
- Question: WorkBuddy plus a Legal Backend satisfies Domain Conditions and Evidence Gate but has one extra network hop; what would justify Native Runtime?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind host sufficiency.
- Assumption Being Attacked: The current Target contract for host sufficiency is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for host sufficiency; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize host sufficiency if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q010

- Question ID: Q010
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: architecture trace
- Question: A Canonical paragraph changes after Q042; how can a reviewer trace the change back to Red finding, Blue decision and Delta?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind architecture trace.
- Assumption Being Attacked: The current Target contract for architecture trace is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for architecture trace; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize architecture trace if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q011

- Question ID: Q011
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: necessary complexity floor
- Question: Which capability cannot be deleted without changing the real legal workflow, and what is the smallest evidence needed to prove that claim?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind necessary complexity floor.
- Assumption Being Attacked: The current Target contract for necessary complexity floor is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for necessary complexity floor; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize necessary complexity floor if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q012

- Question ID: Q012
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 00 Overall Architecture
- Canonical Doc: docs/project/architecture/architecture.md
- Target Component: failure invariant
- Question: State one invariant that must survive deletion of LangGraph, Graph DB, OpenViking, or a service boundary.
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind failure invariant.
- Assumption Being Attacked: The current Target contract for failure invariant is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for failure invariant; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize failure invariant if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q013

- Question ID: Q013
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: matter command
- Question: A user submits the same Create Matter command twice after a timeout; how is one business Matter preserved?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind matter command.
- Assumption Being Attacked: The current Target contract for matter command is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for matter command; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize matter command if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q014

- Question ID: Q014
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: host mutation boundary
- Question: WorkBuddy calls an MCP command with a valid JSON payload that attempts to write FindingVersion; who rejects it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind host mutation boundary.
- Assumption Being Attacked: The current Target contract for host mutation boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for host mutation boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize host mutation boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q015

- Question ID: Q015
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: review delivery
- Question: A WorkProduct cites a stale Finding after HumanDecision changes it; what does the Product Surface show and what is withheld?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind review delivery.
- Assumption Being Attacked: The current Target contract for review delivery is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for review delivery; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize review delivery if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q016

- Question ID: Q016
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: court workflow unknown
- Question: The historical Court workflow is incomplete; which Product Target may be designed and which claim must remain UNKNOWN?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind court workflow unknown.
- Assumption Being Attacked: The current Target contract for court workflow unknown is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for court workflow unknown; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize court workflow unknown if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q017

- Question ID: Q017
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: partial response
- Question: One of five EvidenceRequirements is unresolved but the user asks for an answer now; how is partial output labeled?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind partial response.
- Assumption Being Attacked: The current Target contract for partial response is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for partial response; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize partial response if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q018

- Question ID: Q018
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 01 Product Surface
- Canonical Doc: docs/project/product/product-architecture.md
- Target Component: external host replacement
- Question: If WorkBuddy is replaced by Dify, which Product contract must remain byte-for-byte or semantically stable?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind external host replacement.
- Assumption Being Attacked: The current Target contract for external host replacement is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for external host replacement; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize external host replacement if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q019

- Question ID: Q019
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: document identity
- Question: Two uploads have the same filename and bytes but different tenant scopes; are they one DocumentVersion or two?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind document identity.
- Assumption Being Attacked: The current Target contract for document identity is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for document identity; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize document identity if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q020

- Question ID: Q020
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: ingestion ordering
- Question: Embedding finishes before OCR provenance is committed; can the index become visible?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind ingestion ordering.
- Assumption Being Attacked: The current Target contract for ingestion ordering is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for ingestion ordering; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize ingestion ordering if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q021

- Question ID: Q021
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: parser provenance
- Question: OCR changes a character in a statute quotation; how does SourceSpan preserve raw and normalized text?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind parser provenance.
- Assumption Being Attacked: The current Target contract for parser provenance is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for parser provenance; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize parser provenance if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q022

- Question ID: Q022
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: duplicate upload
- Question: The ingestion queue delivers the same JobId three times; what makes object, parse and index publication idempotent?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind duplicate upload.
- Assumption Being Attacked: The current Target contract for duplicate upload is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for duplicate upload; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize duplicate upload if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q023

- Question ID: Q023
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: retention deletion
- Question: A user requests deletion of a source artifact that is cited by a Finding; which object is deleted and which audit reference remains?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind retention deletion.
- Assumption Being Attacked: The current Target contract for retention deletion is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for retention deletion; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize retention deletion if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q024

- Question ID: Q024
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: corrupt artifact
- Question: Object storage returns a checksum mismatch after DocumentVersion commit; what state transition prevents retrieval?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind corrupt artifact.
- Assumption Being Attacked: The current Target contract for corrupt artifact is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for corrupt artifact; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize corrupt artifact if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q025

- Question ID: Q025
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: ingestion security
- Question: A PDF contains instructions to call a tool during parsing; where is it represented as untrusted content?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind ingestion security.
- Assumption Being Attacked: The current Target contract for ingestion security is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for ingestion security; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize ingestion security if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q026

- Question ID: Q026
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: query class routing
- Question: An Exact Statute query is routed to dense retrieval only and misses an exact version; who selects the retrieval plan?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind query class routing.
- Assumption Being Attacked: The current Target contract for query class routing is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for query class routing; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize query class routing if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q027

- Question ID: Q027
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: hybrid fusion
- Question: BM25 ranks an exact article while dense retrieval ranks a semantically similar but obsolete article; how are scores fused?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind hybrid fusion.
- Assumption Being Attacked: The current Target contract for hybrid fusion is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for hybrid fusion; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize hybrid fusion if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q028

- Question ID: Q028
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: query rewrite budget
- Question: An Agent rewrites a query four times without improving Evidence Sufficiency; which budget and stop condition apply?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind query rewrite budget.
- Assumption Being Attacked: The current Target contract for query rewrite budget is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for query rewrite budget; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize query rewrite budget if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q029

- Question ID: Q029
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: reranker attribution
- Question: A relevant chunk is retrieved at rank 20 then lost after rerank; which component receives the defect?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind reranker attribution.
- Assumption Being Attacked: The current Target contract for reranker attribution is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for reranker attribution; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize reranker attribution if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q030

- Question ID: Q030
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: graph admission
- Question: What evidence must a Query Class show before Graph projection is enabled instead of Hybrid retrieval?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind graph admission.
- Assumption Being Attacked: The current Target contract for graph admission is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for graph admission; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize graph admission if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q031

- Question ID: Q031
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: graph edge correction
- Question: An Event edge links the wrong Party because coreference was wrong; how is the projection corrected without rewriting Domain Fact?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind graph edge correction.
- Assumption Being Attacked: The current Target contract for graph edge correction is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for graph edge correction; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize graph edge correction if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q032

- Question ID: Q032
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: cross document path
- Question: A graph path joins two documents but one edge has no SourceSpan; can it satisfy an EvidenceRequirement?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind cross document path.
- Assumption Being Attacked: The current Target contract for cross document path is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for cross document path; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize cross document path if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q033

- Question ID: Q033
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: citation binding
- Question: Claim C7 cites the right document but the wrong span and wrong DocumentVersion; what is the final answer state?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind citation binding.
- Assumption Being Attacked: The current Target contract for citation binding is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-I
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for citation binding; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize citation binding if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q034

- Question ID: Q034
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: stale index
- Question: DocumentVersion D3 is superseded while an old Milvus result is in flight; may the result enter a Proposal?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind stale index.
- Assumption Being Attacked: The current Target contract for stale index is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for stale index; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize stale index if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q035

- Question ID: Q035
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: evidence sufficiency
- Question: Three high-scoring chunks support two of four Claim elements; who marks the task insufficient?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind evidence sufficiency.
- Assumption Being Attacked: The current Target contract for evidence sufficiency is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for evidence sufficiency; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize evidence sufficiency if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q036

- Question ID: Q036
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: scope and ACL
- Question: A Matter Scope and Public Legal Scope return the same text with different permissions; which retrieval result is visible?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind scope and ACL.
- Assumption Being Attacked: The current Target contract for scope and ACL is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for scope and ACL; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize scope and ACL if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q037

- Question ID: Q037
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: provider normalization
- Question: Provider A returns a tool call and Provider B returns plain JSON for the same Model Contract; where is normalization?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind provider normalization.
- Assumption Being Attacked: The current Target contract for provider normalization is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for provider normalization; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize provider normalization if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q038

- Question ID: Q038
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: fallback semantic drift
- Question: A fallback model uses a different context window and changes the Plan; may it silently continue the same PlanVersion?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind fallback semantic drift.
- Assumption Being Attacked: The current Target contract for fallback semantic drift is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for fallback semantic drift; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize fallback semantic drift if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q039

- Question ID: Q039
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: quota budget
- Question: A Run has enough token budget but no provider quota; which state is recorded and who decides fallback or stop?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind quota budget.
- Assumption Being Attacked: The current Target contract for quota budget is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for quota budget; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize quota budget if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q040

- Question ID: Q040
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: call trace
- Question: A wrong answer could originate in prompt, model, retrieval or reducer; what correlation fields identify one invocation?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind call trace.
- Assumption Being Attacked: The current Target contract for call trace is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for call trace; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize call trace if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q041

- Question ID: Q041
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: offline model
- Question: A fully offline profile cannot reach a hosted model; which provider capability is degraded and which data boundary remains?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind offline model.
- Assumption Being Attacked: The current Target contract for offline model is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for offline model; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize offline model if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q042

- Question ID: Q042
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 04 Model Gateway
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: gateway service boundary
- Question: When does shared quota, secret isolation or model-serving SLA justify a Model Gateway service rather than a provider library?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind gateway service boundary.
- Assumption Being Attacked: The current Target contract for gateway service boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for gateway service boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize gateway service boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q043

- Question ID: Q043
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: context precedence
- Question: Matter Fact, Session Observation and User Preference conflict in one ContextPack; which source has precedence?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind context precedence.
- Assumption Being Attacked: The current Target contract for context precedence is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for context precedence; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize context precedence if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q044

- Question ID: Q044
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: write gate
- Question: A model proposes a durable memory from an unverified answer; which Write Gate rejects or quarantines it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind write gate.
- Assumption Being Attacked: The current Target contract for write gate is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for write gate; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize write gate if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q045

- Question ID: Q045
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: promotion gate
- Question: An Observation is useful in three Runs; what evidence allows promotion to Matter Context?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind promotion gate.
- Assumption Being Attacked: The current Target contract for promotion gate is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for promotion gate; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize promotion gate if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q046

- Question ID: Q046
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: stale memory
- Question: A HumanDecision supersedes a remembered Finding; how is recall prevented from returning the old conclusion?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind stale memory.
- Assumption Being Attacked: The current Target contract for stale memory is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for stale memory; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize stale memory if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q047

- Question ID: Q047
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: deletion tombstone
- Question: A user deletes Matter memory while a Run checkpoint still references it; what may be loaded on resume?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind deletion tombstone.
- Assumption Being Attacked: The current Target contract for deletion tombstone is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for deletion tombstone; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize deletion tombstone if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q048

- Question ID: Q048
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: OpenViking failure
- Question: OpenViking is unavailable during a Run; which Memory contract is preserved and what fallback is allowed?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind OpenViking failure.
- Assumption Being Attacked: The current Target contract for OpenViking failure is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for OpenViking failure; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize OpenViking failure if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q049

- Question ID: Q049
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: tenant isolation
- Question: A shared context index returns a similar memory from another tenant; which gate blocks it before the model?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind tenant isolation.
- Assumption Being Attacked: The current Target contract for tenant isolation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-E
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for tenant isolation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize tenant isolation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q050

- Question ID: Q050
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 05 Memory & Context
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: checkpoint distinction
- Question: A LangGraph checkpoint contains prior messages; why is that not permission to treat them as Canonical Fact?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind checkpoint distinction.
- Assumption Being Attacked: The current Target contract for checkpoint distinction is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for checkpoint distinction; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize checkpoint distinction if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q051

- Question ID: Q051
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: plan for one step
- Question: For deterministic Retrieve→Answer, what does a Plan record that prevents it becoming hidden execution?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind plan for one step.
- Assumption Being Attacked: The current Target contract for plan for one step is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for plan for one step; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize plan for one step if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q052

- Question ID: Q052
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: plan activation
- Question: A PlanVersion is activated and then a user changes the task; may the existing Plan be mutated?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind plan activation.
- Assumption Being Attacked: The current Target contract for plan activation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for plan activation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize plan activation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q053

- Question ID: Q053
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: dag dependency
- Question: Step B requires Evidence from Step A but the scheduler sees only completion flags; what contract prevents early dispatch?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind dag dependency.
- Assumption Being Attacked: The current Target contract for dag dependency is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for dag dependency; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize dag dependency if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q054

- Question ID: Q054
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: parallel barrier
- Question: Three parallel research steps finish at different DomainVersions; what exactly does the Join Barrier compare?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind parallel barrier.
- Assumption Being Attacked: The current Target contract for parallel barrier is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for parallel barrier; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize parallel barrier if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q055

- Question ID: Q055
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: reducer determinism
- Question: Two equivalent Proposal messages arrive in different order; can the reducer produce different Domain output?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind reducer determinism.
- Assumption Being Attacked: The current Target contract for reducer determinism is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for reducer determinism; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize reducer determinism if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q056

- Question ID: Q056
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: replan trigger
- Question: What domain or evidence change is strong enough to create P4 instead of allowing the model to improvise?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind replan trigger.
- Assumption Being Attacked: The current Target contract for replan trigger is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for replan trigger; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize replan trigger if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q057

- Question ID: Q057
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: retry vs replan
- Question: A transient Retriever timeout occurs under the same DomainVersion; why is Retry not Replan?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind retry vs replan.
- Assumption Being Attacked: The current Target contract for retry vs replan is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for retry vs replan; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize retry vs replan if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q058

- Question ID: Q058
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: reflection trigger
- Question: What measurable condition causes Step Reflection, and when is reflection deleted as no-value overhead?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind reflection trigger.
- Assumption Being Attacked: The current Target contract for reflection trigger is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for reflection trigger; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize reflection trigger if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q059

- Question ID: Q059
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: reflexion bound
- Question: A Reflexion loop keeps criticizing its own answer; which budget, state and stop gate end it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind reflexion bound.
- Assumption Being Attacked: The current Target contract for reflexion bound is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for reflexion bound; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize reflexion bound if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q060

- Question ID: Q060
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: budget exhaustion
- Question: Token budget ends after a tool Proposal but before Domain validation; what is persisted and what is not complete?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind budget exhaustion.
- Assumption Being Attacked: The current Target contract for budget exhaustion is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for budget exhaustion; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize budget exhaustion if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q061

- Question ID: Q061
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: hitl resume
- Question: A reviewer approves a Finding after the SecurityEpoch changed; can the interrupt resume directly?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind hitl resume.
- Assumption Being Attacked: The current Target contract for hitl resume is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for hitl resume; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize hitl resume if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q062

- Question ID: Q062
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: cancellation
- Question: Cancellation arrives while a read-only retrieval and an irreversible Tool Effect are both active; how do their states differ?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind cancellation.
- Assumption Being Attacked: The current Target contract for cancellation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for cancellation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize cancellation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q063

- Question ID: Q063
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: run generation
- Question: Two workers resume the same AgentRun generation; which CAS or lease prevents duplicate Domain commit?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind run generation.
- Assumption Being Attacked: The current Target contract for run generation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for run generation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize run generation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q064

- Question ID: Q064
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: checkpoint compatibility
- Question: A deployed graph changes node names while an old checkpoint is pending; how is compatibility checked?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind checkpoint compatibility.
- Assumption Being Attacked: The current Target contract for checkpoint compatibility is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-I
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for checkpoint compatibility; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize checkpoint compatibility if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q065

- Question ID: Q065
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: capability version
- Question: EVENT_EXTRACTION v2 adds a required field; can a v1 Agent accept the proposal without an adapter?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind capability version.
- Assumption Being Attacked: The current Target contract for capability version is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for capability version; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize capability version if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q066

- Question ID: Q066
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: proposal validation
- Question: A ConflictProposal has valid JSON but references an inaccessible EvidenceCandidate; which validator rejects it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind proposal validation.
- Assumption Being Attacked: The current Target contract for proposal validation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for proposal validation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize proposal validation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q067

- Question ID: Q067
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: deterministic algorithm
- Question: A legal algorithm and an LLM disagree on Fact–Article Mapping; how are candidates compared and who commits?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind deterministic algorithm.
- Assumption Being Attacked: The current Target contract for deterministic algorithm is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for deterministic algorithm; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize deterministic algorithm if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q068

- Question ID: Q068
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: license boundary
- Question: An official repository has no LICENSE but its paper is public; what can be used, linked, or reimplemented?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind license boundary.
- Assumption Being Attacked: The current Target contract for license boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for license boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize license boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q069

- Question ID: Q069
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: capability timeout
- Question: A capability provider times out after producing a partial result; is that Observation, Failure, or Unknown Effect?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind capability timeout.
- Assumption Being Attacked: The current Target contract for capability timeout is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for capability timeout; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize capability timeout if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q070

- Question ID: Q070
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 07 Capability / Skill
- Canonical Doc: docs/project/agents/agent-platform.md
- Target Component: skill capability boundary
- Question: A Skill says how to identify a dispute while Capability exposes detection; which layer owns legal semantics?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind skill capability boundary.
- Assumption Being Attacked: The current Target contract for skill capability boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for skill capability boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize skill capability boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q071

- Question ID: Q071
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: tool visibility
- Question: A Tool is visible in a prompt but not authorized for the Matter; which catalog state is returned?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind tool visibility.
- Assumption Being Attacked: The current Target contract for tool visibility is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for tool visibility; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize tool visibility if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q072

- Question ID: Q072
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: prepared action hash
- Question: Arguments change after approval but before execution; which canonical hash invalidates the action?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind prepared action hash.
- Assumption Being Attacked: The current Target contract for prepared action hash is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for prepared action hash; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize prepared action hash if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q073

- Question ID: Q073
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: execute authorization
- Question: A tenant grant is revoked after approval and before execution; which service performs the final check?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind execute authorization.
- Assumption Being Attacked: The current Target contract for execute authorization is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-I
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for execute authorization; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize execute authorization if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q074

- Question ID: Q074
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: unknown effect
- Question: An external court API times out after accepting a request; why is retry forbidden before reconciliation?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind unknown effect.
- Assumption Being Attacked: The current Target contract for unknown effect is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for unknown effect; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize unknown effect if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q075

- Question ID: Q075
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: operation identity
- Question: The provider lacks idempotency but returns an operation ID only after execution; how is duplicate risk contained?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind operation identity.
- Assumption Being Attacked: The current Target contract for operation identity is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for operation identity; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize operation identity if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q076

- Question ID: Q076
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: receipt persistence
- Question: Tool succeeded but EffectReceipt write failed; what durable record is reconstructed first?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind receipt persistence.
- Assumption Being Attacked: The current Target contract for receipt persistence is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for receipt persistence; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize receipt persistence if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q077

- Question ID: Q077
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: tool version
- Question: MCP ToolVersion changes a side-effect schema while a Plan is paused; can the old PreparedAction run?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind tool version.
- Assumption Being Attacked: The current Target contract for tool version is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for tool version; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize tool version if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q078

- Question ID: Q078
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: sandbox boundary
- Question: A Python parser needs filesystem access but no network; which sandbox policy is least privilege?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind sandbox boundary.
- Assumption Being Attacked: The current Target contract for sandbox boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for sandbox boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize sandbox boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q079

- Question ID: Q079
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: mcp metadata
- Question: An MCP server returns a malicious description that asks the model to reveal a secret; where is it untrusted?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind mcp metadata.
- Assumption Being Attacked: The current Target contract for mcp metadata is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for mcp metadata; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize mcp metadata if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q080

- Question ID: Q080
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 08 Tool Runtime
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: effect reconciliation
- Question: Domain commit references an EffectReceipt whose provider status is unknown; which state remains visible to the user?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind effect reconciliation.
- Assumption Being Attacked: The current Target contract for effect reconciliation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for effect reconciliation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize effect reconciliation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q081

- Question ID: Q081
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: tenant isolation
- Question: A valid user token is replayed with another tenant ID in a Tool request; what decision input catches it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind tenant isolation.
- Assumption Being Attacked: The current Target contract for tenant isolation is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for tenant isolation; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize tenant isolation if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q082

- Question ID: Q082
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: prompt injection
- Question: A court PDF asks the Agent to disable approval; which untrusted-data boundary prevents policy mutation?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind prompt injection.
- Assumption Being Attacked: The current Target contract for prompt injection is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for prompt injection; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize prompt injection if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q083

- Question ID: Q083
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: secret scope
- Question: A secret is mounted for one Tool Attempt; how do Model, Trace, Memory and error logs prove they did not receive it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind secret scope.
- Assumption Being Attacked: The current Target contract for secret scope is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for secret scope; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize secret scope if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q084

- Question ID: Q084
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: no egress
- Question: Offline mode starts with a permissive dependency that attempts telemetry; what test and allowlist prove zero egress?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind no egress.
- Assumption Being Attacked: The current Target contract for no egress is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-E
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for no egress; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize no egress if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q085

- Question ID: Q085
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: sandbox escape
- Question: A parser executes a subprocess outside its intended filesystem; which boundary and evidence classify the failure?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind sandbox escape.
- Assumption Being Attacked: The current Target contract for sandbox escape is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for sandbox escape; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize sandbox escape if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q086

- Question ID: Q086
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: approval expiry
- Question: Human approval expires while a queue message is delayed; can the Worker use the old Approval?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind approval expiry.
- Assumption Being Attacked: The current Target contract for approval expiry is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for approval expiry; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize approval expiry if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q087

- Question ID: Q087
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: audit tamper
- Question: A service reports a successful Domain Decision but omits the model and Tool traces; which audit completeness gate rejects release?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind audit tamper.
- Assumption Being Attacked: The current Target contract for audit tamper is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for audit tamper; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize audit tamper if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q088

- Question ID: Q088
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 09 Security
- Canonical Doc: docs/project/security/security-architecture.md
- Target Component: artifact supply chain
- Question: A container image digest differs from the signed release manifest; which deployment state is allowed?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind artifact supply chain.
- Assumption Being Attacked: The current Target contract for artifact supply chain is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for artifact supply chain; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize artifact supply chain if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q089

- Question ID: Q089
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: metric denominator
- Question: A system abstains on unsupported Claims; how do Evidence Sufficiency, Task Completion and Unsupported Claim Rate count it?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind metric denominator.
- Assumption Being Attacked: The current Target contract for metric denominator is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for metric denominator; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize metric denominator if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q090

- Question ID: Q090
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: abc randomization
- Question: A/B/C variants see different case difficulty; what split and assignment protocol keeps comparison fair?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind abc randomization.
- Assumption Being Attacked: The current Target contract for abc randomization is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-E
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for abc randomization; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize abc randomization if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q091

- Question ID: Q091
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: ablation attribution
- Question: Graph, Memory and Multi-Agent are enabled together; which ablation isolates their causal contribution?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind ablation attribution.
- Assumption Being Attacked: The current Target contract for ablation attribution is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for ablation attribution; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize ablation attribution if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q092

- Question ID: Q092
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: court qa review
- Question: Court QA reference answers disagree among reviewers; who resolves the rubric before scoring?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind court qa review.
- Assumption Being Attacked: The current Target contract for court qa review is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for court qa review; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize court qa review if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q093

- Question ID: Q093
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: release regression
- Question: A new Reranker improves Recall but worsens Citation Correctness; which release gate blocks adoption?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind release regression.
- Assumption Being Attacked: The current Target contract for release regression is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for release regression; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize release regression if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q094

- Question ID: Q094
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 10 Observability & Eval
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: telemetry and eval
- Question: Operational traces contain secrets or hidden reasoning; what is retained for audit without persisting chain of thought?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind telemetry and eval.
- Assumption Being Attacked: The current Target contract for telemetry and eval is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for telemetry and eval; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize telemetry and eval if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q095

- Question ID: Q095
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: service boundary
- Question: A candidate service has no independent scaling or security need but has a clean package boundary; why is it not a library?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind service boundary.
- Assumption Being Attacked: The current Target contract for service boundary is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for service boundary; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize service boundary if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION

## Q096

- Question ID: Q096
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: queue semantics
- Question: A Job is delivered twice after lease expiry; how do JobId, Attempt, Idempotency and DLQ interact?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind queue semantics.
- Assumption Being Attacked: The current Target contract for queue semantics is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for queue semantics; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize queue semantics if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q097

- Question ID: Q097
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: physical database
- Question: Knowledge wants its own PostgreSQL instance for autonomy but no distinct SLO exists; what evidence is missing?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind physical database.
- Assumption Being Attacked: The current Target contract for physical database is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P0
- Closure Class: P0-I
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for physical database; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize physical database if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q098

- Question ID: Q098
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: retry storm
- Question: A model timeout causes three queues to retry simultaneously; where are budgets, backpressure and circuit breaks enforced?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind retry storm.
- Assumption Being Attacked: The current Target contract for retry storm is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for retry storm; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize retry storm if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q099

- Question ID: Q099
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: rollback compatibility
- Question: A service rolls back code while messages use a newer schema; how is the compatibility window enforced?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind rollback compatibility.
- Assumption Being Attacked: The current Target contract for rollback compatibility is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for rollback compatibility; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize rollback compatibility if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: NOVEL

## Q100

- Question ID: Q100
- Round ID: RB-WORKFLOW-V3-ROUND-002
- 11+1 Lens: 11 Infrastructure
- Canonical Doc: docs/project/services/service-architecture.md
- Target Component: capacity heterogeneity
- Question: Peak users fall but concurrent Sandbox and OCR jobs rise; which scaling signal justifies separate workers?
- Attack Intent: Attack the unstated ownership, state, failure or replacement assumption behind capacity heterogeneity.
- Assumption Being Attacked: The current Target contract for capacity heterogeneity is sufficient without this concrete counterexample.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this operation is in flight.
- Simpler Alternative: A narrower contract, library, worker, Host integration or PostgreSQL-backed workflow is sufficient.
- OSS Alternative: Use an existing provider or framework behind the same contract and compare its evidence.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Contract test and failure replay for capacity heterogeneity; no Current claim without runtime evidence.
- Kill Condition: Delete or externalize capacity heterogeneity if the stated failure is handled with equal quality and lower cost by the simpler alternative.
- Question Type: REGRESSION
