# Round-003 Questions

Protocol: ZUNO-RED-BLUE-WORKFLOW-V3.1

## Q001

- Question ID: Q001
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Which stable boundary must a cross-layer Matter analysis preserve when Domain State, Runtime Control State, and provider output disagree?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q002

- Question ID: Q002
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Can the complex-case happy path be explained from Matter intake to reviewed WorkProduct without hiding a service or state owner?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL
## Q003

- Question ID: Q003
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: What prevents a LangGraph checkpoint or queue acknowledgement from being treated as Domain success?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q004

- Question ID: Q004
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: When Domain commit succeeds but checkpoint persistence fails, what is the recovery contract and who reconciles it?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q005

- Question ID: Q005
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Why does the Target need five physical services rather than the former eleven logical modules or one modular worker?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q006

- Question ID: Q006
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: What falsifiable result would show that a WorkBuddy Host plus Legal Backend is sufficient and the native runtime adds no value?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q007

- Question ID: Q007
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Which Python-only workload boundary protects API latency from OCR, embedding, sandbox, and long-running agent work?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q008

- Question ID: Q008
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Could a modular package plus independent workers satisfy the same ownership, isolation, scaling, and recovery requirements?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q009

- Question ID: Q009
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Which concepts are stable Legal Domain contracts and which remain replaceable model, graph, memory, or runtime providers?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q010

- Question ID: Q010
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: What evidence would justify reversing LangGraph, Graph, Memory, or a service split after implementation?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q011

- Question ID: Q011
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Which statements are Current, Target, Hypothesis, Gap, or History, and how does the document stop status leakage?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q012

- Question ID: Q012
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 00 Overall Architecture
- Canonical Owner Doc: docs/project/architecture/architecture.md
- Target Component: 00 Overall Architecture Part A / Part B contract
- Question: Does the cross-layer contract expose enough input, output, version, failure, security, audit, and evidence fields to implement it?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 00 Overall Architecture; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q013

- Question ID: Q013
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: Can a user follow one Matter from document intake through analysis, review, and WorkProduct without learning internal services?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q014

- Question ID: Q014
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: Where does an external Host such as WorkBuddy stop, and where must Zuno retain the legal Domain write boundary?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q015

- Question ID: Q015
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: Why are Review, AgentRun, and WorkProduct separate product concepts instead of one chat transcript?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q016

- Question ID: Q016
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: How does the product show stale, pending, unsupported, and human-reviewed results without presenting them as final truth?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q017

- Question ID: Q017
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: What controlled benchmark could prove that WorkBuddy plus Legal Skills and MCP is already sufficient for this product surface?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q018

- Question ID: Q018
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 01 Product Surface
- Canonical Owner Doc: docs/project/product/product-architecture.md
- Target Component: 01 Product Surface Part A / Part B contract
- Question: How do approval, audit, citation, and delivery contracts survive a provider failure or a repeated client request?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 01 Product Surface; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q019

- Question ID: Q019
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: What does a DocumentVersion mean when the same pleading is uploaded again with changed bytes or metadata?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q020

- Question ID: Q020
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: Which hash, provenance, parser version, scope, and access fields make an ingested artifact reproducible?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q021

- Question ID: Q021
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: How do duplicate uploads, worker crashes, and retry deliveries converge without creating duplicate evidence?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q022

- Question ID: Q022
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: What does the user receive when OCR or parsing is corrupt, partial, timed out, or unavailable?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q023

- Question ID: Q023
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: Which data belongs to the artifact owner and which is only a retrieval projection that can be rebuilt?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q024

- Question ID: Q024
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: How does late evidence invalidate dependent facts, conflicts, findings, indexes, and active analysis?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q025

- Question ID: Q025
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 02 Input / Document Ingestion
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 02 Input / Document Ingestion Part A / Part B contract
- Question: What evidence would justify a separate ingestion service instead of a package or independent worker?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 02 Input / Document Ingestion; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q026

- Question ID: Q026
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How does retrieval choose lexical, dense, hybrid, rerank, graph, or corrective search for the query class?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q027

- Question ID: Q027
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: When does a graph relation improve cross-document evidence reasoning enough to justify its build and maintenance cost?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q028

- Question ID: Q028
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: Can every cited answer span be traced to a stable source, DocumentVersion, scope, and retrieval receipt?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q029

- Question ID: Q029
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: What happens when a vector, lexical, graph, or rerank index is stale, unavailable, or disagrees with canonical evidence?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q030

- Question ID: Q030
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How are public, organization, and Matter scopes selected and enforced without retrieving unauthorized material?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q031

- Question ID: Q031
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How is a graph reasoning chain kept distinct from the citation evidence that supports the final legal statement?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q032

- Question ID: Q032
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: What is the deterministic fallback when the graph provider is down or its projection is behind the Domain version?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q033

- Question ID: Q033
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How does the system measure evidence sufficiency instead of treating Recall@K as answer correctness?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q034

- Question ID: Q034
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: Does a Kill Graph benchmark show material gain over fixed Hybrid RAG across the defined legal query classes?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q035

- Question ID: Q035
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How do retrieval rounds, tokens, latency, and cost stay bounded when an Agent requests corrective search?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q036

- Question ID: Q036
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 03 Knowledge / Agentic GraphRAG
- Canonical Owner Doc: docs/project/knowledge/knowledge-evidence-architecture.md
- Target Component: 03 Knowledge / Agentic GraphRAG Part A / Part B contract
- Question: How are index disagreement and evidence version changes surfaced to the planner and human reviewer?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 03 Knowledge / Agentic GraphRAG; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q037

- Question ID: Q037
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: Which model-routing decision is stable platform policy and which is provider-specific implementation detail?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q038

- Question ID: Q038
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: Why is a Model Gateway a service rather than a library or capability inside the Runtime worker?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q039

- Question ID: Q039
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: How are quota, timeout, fallback, provider receipt, and model version recorded for each invocation?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q040

- Question ID: Q040
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: What happens when the selected model becomes unavailable after a Plan has already started?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q041

- Question ID: Q041
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: How does an offline or local-model profile preserve the same Contract without silently changing evidence policy?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q042

- Question ID: Q042
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 04 Model Gateway
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 04 Model Gateway Part A / Part B contract
- Question: What benchmark would justify deleting the gateway and calling model providers directly from the Runtime?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 04 Model Gateway; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q043

- Question ID: Q043
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: Why is canonical Matter Domain State not a long-term Memory record, even when an Agent reuses it?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q044

- Question ID: Q044
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: Which memory scope, write gate, provenance, expiry, and permission rules prevent context from becoming hidden truth?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q045

- Question ID: Q045
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: How is tenant or Matter leakage prevented when a Memory provider compacts or retrieves similar experiences?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q046

- Question ID: Q046
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: What happens when a remembered statement conflicts with a newer Evidence or Domain version?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q047

- Question ID: Q047
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: Can OpenViking be replaced by a Matter database plus checkpoint and context builder without quality loss?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q048

- Question ID: Q048
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: How are compaction, summarization, deletion, legal hold, and provenance handled without hiding unsupported claims?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q049

- Question ID: Q049
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: How does a user request or legal hold remove reusable context while preserving required audit evidence?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q050

- Question ID: Q050
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 05 Memory & Context
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 05 Memory & Context Part A / Part B contract
- Question: Does an ablation prove Memory adds value beyond Matter DB plus Runtime checkpoint for the target workflows?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 05 Memory & Context; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q051

- Question ID: Q051
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: Why does the Target need a Single Controller with explicit Plan state instead of an unconstrained autonomous society?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q052

- Question ID: Q052
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: Which graph control requirement cannot be met by a plain state machine, async workflow, or queue worker?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q053

- Question ID: Q053
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How is an immutable PlanVersion separated from mutable Domain State and provider checkpoints?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q054

- Question ID: Q054
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: Can a complex case analysis show parallel evidence, dispute, and legal research work joining at an explicit barrier?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q055

- Question ID: Q055
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How does the join barrier decide whether missing, stale, or conflicting branches block a Finding?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q056

- Question ID: Q056
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: What is retried, replanned, or escalated when one step times out after partial provider work?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q057

- Question ID: Q057
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How does reflection improve a result without persisting hidden chain of thought or making unverifiable claims?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q058

- Question ID: Q058
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How does HITL pause, permission change, review, and resume without losing the Domain version it was based on?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q059

- Question ID: Q059
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: What happens when a Finding changes while a long-running Agent Run is waiting to resume?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q060

- Question ID: Q060
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How do budget, timeout, cancellation, queue backpressure, and model limits stop an unbounded run?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q061

- Question ID: Q061
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: Why are FactProposal, ConflictProposal, and FindingProposal safer than allowing an Agent to write Canonical state?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q062

- Question ID: Q062
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: Which replacement test would allow the Runtime to move from LangGraph to another durable orchestration engine?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q063

- Question ID: Q063
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: How does recovery reconcile Domain commit, checkpoint position, queue delivery, and tool receipts in both directions?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q064

- Question ID: Q064
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 06 Agent Core / Planning & Control
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 06 Agent Core / Planning & Control Part A / Part B contract
- Question: What result would falsify the value of a native domain-aware runtime compared with WorkBuddy plus Zuno APIs?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 06 Agent Core / Planning & Control; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q065

- Question ID: Q065
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: Where is the boundary between a Skill method, a Legal Capability Contract, a Tool, and retrievable Knowledge?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q066

- Question ID: Q066
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: How does a shared legal capability prevent each Agent from embedding a separate copy of event or conflict logic?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q067

- Question ID: Q067
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: What input, output, provenance, confidence, version, and evidence fields make a capability contract testable?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q068

- Question ID: Q068
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: Why can a provider return only a proposal or observation, and who admits it as a Canonical Domain version?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q069

- Question ID: Q069
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: Can local code, an LLM, an OSS model, an API, or MCP provider be swapped behind the same capability?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q070

- Question ID: Q070
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 07 Capability / Skill
- Canonical Owner Doc: docs/project/agents/agent-platform.md
- Target Component: 07 Capability / Skill Part A / Part B contract
- Question: What evidence would justify deleting a dedicated capability layer and using ordinary typed tools instead?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 07 Capability / Skill; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q071

- Question ID: Q071
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: How are Proposal, PreparedAction, EffectReceipt, and Canonical Domain mutation kept distinct?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q072

- Question ID: Q072
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: Which authorization and approval checks run immediately before an effect rather than only at planning time?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q073

- Question ID: Q073
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: How is an unknown outcome handled when a tool times out after the external provider may have executed?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: REGRESSION

## Q074

- Question ID: Q074
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: How do read-only, reversible, and irreversible effects change approval, retry, and reconciliation requirements?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q075

- Question ID: Q075
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: Why does a Python or network sandbox need a separate security and resource boundary from the Agent worker?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q076

- Question ID: Q076
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: Which idempotency key and provider operation ID prevent duplicate external side effects?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q077

- Question ID: Q077
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: How does the Tool service reconcile a receipt, queue retry, checkpoint, and Domain audit entry after partial failure?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q078

- Question ID: Q078
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: How does prompt injection in Matter content fail to grant a tool capability or secret?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q079

- Question ID: Q079
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: Could MCP or an existing sandbox provide this boundary, and what replacement test is required?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q080

- Question ID: Q080
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 08 Tool Runtime
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 08 Tool Runtime Part A / Part B contract
- Question: What measured evidence would allow deletion of the custom Tool Runtime while preserving effect safety?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 08 Tool Runtime; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q081

- Question ID: Q081
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: Who owns tenant, Matter, Domain, Runtime, Tool, secret, approval, and audit decisions across service boundaries?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q082

- Question ID: Q082
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: Which tenant, Matter, scope, capability, approval, and policy epoch fields are evaluated on every sensitive operation?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q083

- Question ID: Q083
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: How are permissions and policy epochs invalidated during a long-running Run or after a role change?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q084

- Question ID: Q084
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: What does a no-egress or offline profile prove beyond a configuration flag?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q085

- Question ID: Q085
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: How are secret access, model invocation, tool execution, Domain decision, and Human decision traced?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q086

- Question ID: Q086
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: Can a revoked permission, stale credential, duplicate effect, or cross-tenant request be rejected and audited deterministically?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q087

- Question ID: Q087
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: Which prompt-injection, sandbox, network, secret, and cross-tenant tests are required before a security claim?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q088

- Question ID: Q088
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 09 Security
- Canonical Owner Doc: docs/project/security/security-architecture.md
- Target Component: 09 Security Part A / Part B contract
- Question: When should the security boundary be simplified or a provider externalized if the same attestations are available?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 09 Security; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q089

- Question ID: Q089
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: How do A/B/C compare generic Host, Host plus Legal Capabilities, and native Domain-aware Runtime under matched budgets?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q090

- Question ID: Q090
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: Which evidence metrics expose unsupported claims, citation errors, conflicts, applicability, and reviewer acceptance?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q091

- Question ID: Q091
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: Why should reviewer acceptance and task outcome complement, rather than be replaced by, an LLM judge?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q092

- Question ID: Q092
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: How are benchmark cases, denominators, abstentions, stale inputs, and human adjudication recorded?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q093

- Question ID: Q093
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: Can quality, latency, token, cost, model calls, retrieval rounds, and state reuse show a real tradeoff?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q094

- Question ID: Q094
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 10 Observability & Eval
- Canonical Owner Doc: docs/project/eval/legal-eval-and-benchmark.md
- Target Component: 10 Observability & Eval Part A / Part B contract
- Question: What release gate remains honest when runtime, Court QA, security, and production evidence are still incomplete?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 10 Observability & Eval; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q095

- Question ID: Q095
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: Why are workload heterogeneity and failure domains stronger service-boundary evidence than registered user count?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q096

- Question ID: Q096
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: Which operations are synchronous CRUD and which must be asynchronous ingestion, Agent, graph, eval, or sandbox jobs?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q097

- Question ID: Q097
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: How do Job Identity, idempotency, retry, timeout, cancellation, dead-letter, and backpressure behave under redelivery?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q098

- Question ID: Q098
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: What independent resource, security, scaling, or failure boundary justifies a worker or service split?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q099

- Question ID: Q099
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: Can a shared PostgreSQL cluster with logical ownership satisfy V1 better than database-per-service?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P2
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL

## Q100

- Question ID: Q100
- Round ID: RB-WORKFLOW-V3-ROUND-003
- 11+1 Lens: 11 Infrastructure
- Canonical Owner Doc: docs/project/deployment/microservice-deployment.md
- Target Component: 11 Infrastructure Part A / Part B contract
- Question: What evidence would justify Kafka, Kubernetes, gRPC, or a larger service topology instead of the smallest deployable system?
- Attack Intent: Attack whether the documented responsibility is necessary, bounded, testable and replaceable.
- Assumption Being Attacked: The current Target boundary is sufficiently justified without a concrete failure, simpler alternative or evidence gate.
- Failure Scenario: A version, permission, retry, provider or partial-failure boundary changes while this scenario is in flight.
- Simpler Alternative: A shorter narrative, typed library, independent worker, Host integration or PostgreSQL-backed workflow could be sufficient.
- OSS Alternative: An existing provider or framework could implement the mechanism behind the same stable Contract.
- Severity: P1
- Closure Class: NONE
- Expected Depth: Problem + Scenario + Owner + State + Failure + Recovery + Evidence + Reversal
- Required Evidence: Document review, contract test or benchmark appropriate to 11 Infrastructure; no Current claim without runtime evidence.
- Part A Concern: Explain why this boundary exists, what it owns, what it does not own, the happy path, failure, tradeoff and deletion condition.
- Part B Concern: Define input/output, state/version, failure propagation, retry/recovery, idempotency, security, audit, observability and verification.
- Kill Condition: Remove or externalize the boundary if the simpler alternative passes the same scenario, safety and evidence test.
- Question Type: NOVEL
