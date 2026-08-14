<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: 002
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 19ba6e050e1334f71c511a5968c9ea9d15c68111
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-WORKFLOW-V3-ROUND-002
# ARCHITECTURE_INTERVIEW — 002

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session README: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/README.md`

# RB-WORKFLOW-V3-ROUND-002

本目录是 `ZUNO-RED-BLUE-WORKFLOW-V3` 的不可变 Round Archive。它记录一次完整的
100Q 架构对抗审查，不是 Current Runtime、历史事实或 Production Readiness 证据。

## Round 状态

- Baseline：`19ba6e050e1334f71c511a5968c9ea9d15c68111`
- 结果：`COMPLETE`
- 问题 / 回答 / 评分 / 决策：`100 / 100 / 100 / 100`
- Canonical Sync：`APPLIED`，仅同步允许自动应用的 Target refinement
- 新增 A-P0：`0`
- 下一轮：`READY_NOT_STARTED`
- Implementation Program：`READY_FOR_TASK_DEFINITION`；本轮未创建实施任务

## 固定流水线

```text
Canonical Snapshot
→ Red 100Q
→ Blue 100 Answers
→ Red 100 Scores
→ Blue 100 Decisions
→ Architecture Deltas
→ Canonical Sync
→ Verification
→ Review Package
```

Round-002 没有修改 Runtime、UI、Schema、Migration、Infrastructure、Dependencies 或
事实文档，也没有把 Target、Hypothesis 或历史候选升级为 Current。

## 文件职责

| 文件 | 职责 |
|---|---|
| `manifest.yaml` | Round Contract、配额、计数和状态机器可读摘要 |
| `canonical-snapshot.md` | 审查前 Canonical 基线 |
| `11-plus-1-coverage-map.md` | 本轮审查 Lens 与 Owner 文档映射 |
| `questions.md` | 100 个 Red Attack Question |
| `blue-answers.md` | 100 个 Blue Answer |
| `red-scores.md` | 100 个 Red Score、严重度和闭环分类 |
| `blue-decisions.md` | 100 个 Blue Disposition |
| `architecture-deltas.md` | D001–D011 及其 Question/Canonical trace |
| `canonical-sync-record.md` | Delta 到 Canonical 文件的同步记录 |
| `scorecard.md` | 可重算的总分与 11+1 分数 |
| `gap-register.md` | Implementation / Measurement / External gaps |
| `adr-escalations.md` | ADR/User escalation 记录 |
| `chatgpt-review-package.md` | 面向外部审查的压缩包 |
| `round-report.md` | Round 结果与下一轮入口 |

Round 关闭后不得无痕改写 Question、Answer、Score 或 Decision；后续纠错必须使用 Errata
并保留 Git 追踪。

## Session Manifest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/manifest.yaml`

protocol_version: ZUNO-RED-BLUE-WORKFLOW-V3
session_id: RB-WORKFLOW-V3-ROUND-002
round_id: RB-WORKFLOW-V3-ROUND-002
baseline_sha: 19ba6e050e1334f71c511a5968c9ea9d15c68111
final_sha: recorded in final handoff
source_canonical_state: ACCEPTED_TARGET
question_budget: 100
actual_question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novelty_status: ASSESSED
novel_question_count: 80
regression_question_count: 20
novelty_threshold_percent: 70
regression_max_percent: 30
category_distribution:
  "00 Overall Architecture": 12
  "01 Product Surface": 6
  "02 Input / Document Ingestion": 7
  "03 Knowledge / Agentic GraphRAG": 11
  "04 Model Gateway": 6
  "05 Memory & Context": 8
  "06 Agent Core / Planning & Control": 14
  "07 Capability / Skill": 6
  "08 Tool Runtime": 10
  "09 Security": 8
  "10 Observability & Eval": 6
  "11 Infrastructure": 6
red_blue_order: RED_ATTACK -> BLUE_ANSWER -> RED_SCORE -> BLUE_DECISION -> DELTA -> CANONICAL_SYNC
canonical_sync_status: APPLIED
round_status: COMPLETE
new_a_p0: 0
original_p0_closed: 0
implementation_program: READY_FOR_TASK_DEFINITION
round_003_status: READY_NOT_STARTED
runtime_changed: NONE
schema_or_migration_changed: NONE
facts_changed: NONE
adr_escalation_count: 0
user_gate_escalation_count: 0

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/questions.md`

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

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/blue-answers.md`

# Round-002 Blue Answers

Answers are Target decisions, not Current implementation evidence.

## Q001

- Question ID: Q001
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. Product thesis acceptance must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: Product thesis acceptance contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Given the approved Part-A Target, which measurable business problem would falsify the Legal Case Intelligence thesis before any service is built?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: Product thesis acceptance records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: Product thesis acceptance is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for Product thesis acceptance.
- Remaining Gap: GAP-R2-001
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use Product thesis acceptance as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q002

- Question ID: Q002
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. Canonical state admission must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: Canonical state admission contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Provider returns a plausible FactProposal with three citations but no stable identity; exactly which gate prevents it becoming Canonical State?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: Canonical state admission records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: Canonical state admission is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for Canonical state admission.
- Remaining Gap: GAP-R2-002
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use Canonical state admission as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q003

- Question ID: Q003
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. Owner registry drift must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: Owner registry drift contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Domain and Data documents disagree about who owns DomainVersion; which document wins and how does the verifier detect drift?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: Owner registry drift records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: Owner registry drift is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for Owner registry drift.
- Remaining Gap: GAP-R2-003
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use Owner registry drift as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q004

- Question ID: Q004
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. main runtime flow must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: main runtime flow contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Run reaches Final Gate while one independent EvidenceRequirement is still pending; may the response be published?
- Target Decision: CLARIFY
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: main runtime flow records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: main runtime flow is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for main runtime flow.
- Remaining Gap: GAP-R2-004
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use main runtime flow as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q005

- Question ID: Q005
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. cross-state reconciliation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: cross-state reconciliation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is DomainVersion=D10, PlanVersion=P3, Checkpoint=C8 and EffectReceipt=R4 disagree after a crash; give the deterministic recovery order.
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: cross-state reconciliation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: cross-state reconciliation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for cross-state reconciliation.
- Remaining Gap: GAP-R2-005
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use cross-state reconciliation as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q006

- Question ID: Q006
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. new evidence invalidation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: new evidence invalidation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is EvidenceVersion=E11 invalidates two Findings but a parallel branch is still running on E10; which branch result may be joined?
- Target Decision: IMPLEMENTATION_GAP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: new evidence invalidation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: new evidence invalidation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for new evidence invalidation.
- Remaining Gap: GAP-R2-006
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use new evidence invalidation as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q007

- Question ID: Q007
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. accepted target maturity must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: accepted target maturity contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is What exact evidence is still missing between ACCEPTED_TARGET and IMPLEMENTED, VERIFIED, MEASURED, and PRODUCTION_PROVEN?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: accepted target maturity records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: accepted target maturity is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for accepted target maturity.
- Remaining Gap: GAP-R2-007
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use accepted target maturity as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q008

- Question ID: Q008
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. ordinary JSON alternative must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: ordinary JSON alternative contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is If ordinary JSON plus PostgreSQL passes identity, provenance, CAS, review and stale tests, what part of a named Domain Kernel survives?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: ordinary JSON alternative records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: ordinary JSON alternative is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for ordinary JSON alternative.
- Remaining Gap: GAP-R2-008
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use ordinary JSON alternative as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q009

- Question ID: Q009
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. host sufficiency must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: host sufficiency contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is WorkBuddy plus a Legal Backend satisfies Domain Conditions and Evidence Gate but has one extra network hop; what would justify Native Runtime?
- Target Decision: MEASUREMENT_GAP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: host sufficiency records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: host sufficiency is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for host sufficiency.
- Remaining Gap: GAP-R2-009
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use host sufficiency as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q010

- Question ID: Q010
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. architecture trace must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: architecture trace contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Canonical paragraph changes after Q042; how can a reviewer trace the change back to Red finding, Blue decision and Delta?
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: architecture trace records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: architecture trace is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for architecture trace.
- Remaining Gap: GAP-R2-010
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use architecture trace as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q011

- Question ID: Q011
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. necessary complexity floor must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: necessary complexity floor contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Which capability cannot be deleted without changing the real legal workflow, and what is the smallest evidence needed to prove that claim?
- Target Decision: DEFER
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: necessary complexity floor records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: necessary complexity floor is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for necessary complexity floor.
- Remaining Gap: GAP-R2-011
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use necessary complexity floor as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q012

- Question ID: Q012
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. failure invariant must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: failure invariant contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is State one invariant that must survive deletion of LangGraph, Graph DB, OpenViking, or a service boundary.
- Target Decision: KEEP
- Owner: Architecture Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Architecture Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: failure invariant records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: failure invariant is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for failure invariant.
- Remaining Gap: GAP-R2-012
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use failure invariant as a library, worker, provider or delete it.
- Delta Ref: D001
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q013

- Question ID: Q013
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. matter command must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: matter command contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A user submits the same Create Matter command twice after a timeout; how is one business Matter preserved?
- Target Decision: KEEP
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: matter command records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: matter command is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for matter command.
- Remaining Gap: GAP-R2-013
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use matter command as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q014

- Question ID: Q014
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. host mutation boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: host mutation boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is WorkBuddy calls an MCP command with a valid JSON payload that attempts to write FindingVersion; who rejects it?
- Target Decision: KEEP
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: host mutation boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: host mutation boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for host mutation boundary.
- Remaining Gap: GAP-R2-014
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use host mutation boundary as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q015

- Question ID: Q015
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. review delivery must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: review delivery contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A WorkProduct cites a stale Finding after HumanDecision changes it; what does the Product Surface show and what is withheld?
- Target Decision: KEEP
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: review delivery records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: review delivery is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for review delivery.
- Remaining Gap: GAP-R2-015
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use review delivery as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q016

- Question ID: Q016
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. court workflow unknown must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: court workflow unknown contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is The historical Court workflow is incomplete; which Product Target may be designed and which claim must remain UNKNOWN?
- Target Decision: KEEP
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: court workflow unknown records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: court workflow unknown is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for court workflow unknown.
- Remaining Gap: GAP-R2-016
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use court workflow unknown as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q017

- Question ID: Q017
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. partial response must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: partial response contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is One of five EvidenceRequirements is unresolved but the user asks for an answer now; how is partial output labeled?
- Target Decision: KEEP
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: partial response records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: partial response is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for partial response.
- Remaining Gap: GAP-R2-017
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use partial response as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q018

- Question ID: Q018
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. external host replacement must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: external host replacement contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is If WorkBuddy is replaced by Dify, which Product contract must remain byte-for-byte or semantically stable?
- Target Decision: CLARIFY
- Owner: Product / Domain Surface
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Product / Domain Surface.
- Failure: Failure is classified at the boundary instead of being converted to success: external host replacement records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: external host replacement is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for external host replacement.
- Remaining Gap: GAP-R2-018
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use external host replacement as a library, worker, provider or delete it.
- Delta Ref: D002
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q019

- Question ID: Q019
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. document identity must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: document identity contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Two uploads have the same filename and bytes but different tenant scopes; are they one DocumentVersion or two?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: document identity records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: document identity is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for document identity.
- Remaining Gap: GAP-R2-019
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use document identity as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q020

- Question ID: Q020
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. ingestion ordering must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: ingestion ordering contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Embedding finishes before OCR provenance is committed; can the index become visible?
- Target Decision: CLARIFY
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: ingestion ordering records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: ingestion ordering is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for ingestion ordering.
- Remaining Gap: GAP-R2-020
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use ingestion ordering as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q021

- Question ID: Q021
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. parser provenance must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: parser provenance contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is OCR changes a character in a statute quotation; how does SourceSpan preserve raw and normalized text?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: parser provenance records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: parser provenance is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for parser provenance.
- Remaining Gap: GAP-R2-021
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use parser provenance as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q022

- Question ID: Q022
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. duplicate upload must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: duplicate upload contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is The ingestion queue delivers the same JobId three times; what makes object, parse and index publication idempotent?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: duplicate upload records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: duplicate upload is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for duplicate upload.
- Remaining Gap: GAP-R2-022
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use duplicate upload as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q023

- Question ID: Q023
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. retention deletion must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: retention deletion contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A user requests deletion of a source artifact that is cited by a Finding; which object is deleted and which audit reference remains?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: retention deletion records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: retention deletion is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for retention deletion.
- Remaining Gap: GAP-R2-023
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use retention deletion as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q024

- Question ID: Q024
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. corrupt artifact must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: corrupt artifact contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Object storage returns a checksum mismatch after DocumentVersion commit; what state transition prevents retrieval?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: corrupt artifact records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: corrupt artifact is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for corrupt artifact.
- Remaining Gap: GAP-R2-024
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use corrupt artifact as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q025

- Question ID: Q025
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. ingestion security must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: ingestion security contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A PDF contains instructions to call a tool during parsing; where is it represented as untrusted content?
- Target Decision: CLARIFY
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: ingestion security records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: ingestion security is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for ingestion security.
- Remaining Gap: GAP-R2-025
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use ingestion security as a library, worker, provider or delete it.
- Delta Ref: D003
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q026

- Question ID: Q026
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. query class routing must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: query class routing contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An Exact Statute query is routed to dense retrieval only and misses an exact version; who selects the retrieval plan?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: query class routing records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: query class routing is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for query class routing.
- Remaining Gap: GAP-R2-026
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use query class routing as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q027

- Question ID: Q027
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. hybrid fusion must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: hybrid fusion contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is BM25 ranks an exact article while dense retrieval ranks a semantically similar but obsolete article; how are scores fused?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: hybrid fusion records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: hybrid fusion is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for hybrid fusion.
- Remaining Gap: GAP-R2-027
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use hybrid fusion as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q028

- Question ID: Q028
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. query rewrite budget must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: query rewrite budget contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An Agent rewrites a query four times without improving Evidence Sufficiency; which budget and stop condition apply?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: query rewrite budget records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: query rewrite budget is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for query rewrite budget.
- Remaining Gap: GAP-R2-028
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use query rewrite budget as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q029

- Question ID: Q029
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. reranker attribution must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: reranker attribution contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A relevant chunk is retrieved at rank 20 then lost after rerank; which component receives the defect?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: reranker attribution records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: reranker attribution is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for reranker attribution.
- Remaining Gap: GAP-R2-029
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use reranker attribution as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q030

- Question ID: Q030
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. graph admission must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: graph admission contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is What evidence must a Query Class show before Graph projection is enabled instead of Hybrid retrieval?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: graph admission records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: graph admission is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for graph admission.
- Remaining Gap: GAP-R2-030
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use graph admission as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q031

- Question ID: Q031
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. graph edge correction must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: graph edge correction contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An Event edge links the wrong Party because coreference was wrong; how is the projection corrected without rewriting Domain Fact?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: graph edge correction records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: graph edge correction is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for graph edge correction.
- Remaining Gap: GAP-R2-031
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use graph edge correction as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q032

- Question ID: Q032
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. cross document path must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: cross document path contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A graph path joins two documents but one edge has no SourceSpan; can it satisfy an EvidenceRequirement?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: cross document path records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: cross document path is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for cross document path.
- Remaining Gap: GAP-R2-032
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use cross document path as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q033

- Question ID: Q033
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. citation binding must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: citation binding contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Claim C7 cites the right document but the wrong span and wrong DocumentVersion; what is the final answer state?
- Target Decision: IMPLEMENTATION_GAP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: citation binding records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: citation binding is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for citation binding.
- Remaining Gap: GAP-R2-033
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use citation binding as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q034

- Question ID: Q034
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. stale index must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: stale index contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is DocumentVersion D3 is superseded while an old Milvus result is in flight; may the result enter a Proposal?
- Target Decision: CLARIFY
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: stale index records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: stale index is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for stale index.
- Remaining Gap: GAP-R2-034
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use stale index as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q035

- Question ID: Q035
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. evidence sufficiency must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: evidence sufficiency contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Three high-scoring chunks support two of four Claim elements; who marks the task insufficient?
- Target Decision: DEFER
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: evidence sufficiency records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: evidence sufficiency is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for evidence sufficiency.
- Remaining Gap: GAP-R2-035
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use evidence sufficiency as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q036

- Question ID: Q036
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. scope and ACL must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: scope and ACL contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Matter Scope and Public Legal Scope return the same text with different permissions; which retrieval result is visible?
- Target Decision: KEEP
- Owner: Knowledge Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Knowledge Service.
- Failure: Failure is classified at the boundary instead of being converted to success: scope and ACL records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: scope and ACL is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for scope and ACL.
- Remaining Gap: GAP-R2-036
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use scope and ACL as a library, worker, provider or delete it.
- Delta Ref: D004
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q037

- Question ID: Q037
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. provider normalization must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: provider normalization contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Provider A returns a tool call and Provider B returns plain JSON for the same Model Contract; where is normalization?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: provider normalization records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: provider normalization is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for provider normalization.
- Remaining Gap: GAP-R2-037
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use provider normalization as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q038

- Question ID: Q038
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. fallback semantic drift must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: fallback semantic drift contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A fallback model uses a different context window and changes the Plan; may it silently continue the same PlanVersion?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: fallback semantic drift records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: fallback semantic drift is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for fallback semantic drift.
- Remaining Gap: GAP-R2-038
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use fallback semantic drift as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q039

- Question ID: Q039
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. quota budget must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: quota budget contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Run has enough token budget but no provider quota; which state is recorded and who decides fallback or stop?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: quota budget records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: quota budget is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for quota budget.
- Remaining Gap: GAP-R2-039
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use quota budget as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q040

- Question ID: Q040
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. call trace must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: call trace contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A wrong answer could originate in prompt, model, retrieval or reducer; what correlation fields identify one invocation?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: call trace records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: call trace is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for call trace.
- Remaining Gap: GAP-R2-040
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use call trace as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q041

- Question ID: Q041
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. offline model must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: offline model contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A fully offline profile cannot reach a hosted model; which provider capability is degraded and which data boundary remains?
- Target Decision: CLARIFY
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: offline model records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: offline model is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for offline model.
- Remaining Gap: GAP-R2-041
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use offline model as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q042

- Question ID: Q042
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. gateway service boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: gateway service boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is When does shared quota, secret isolation or model-serving SLA justify a Model Gateway service rather than a provider library?
- Target Decision: EXTERNALIZE
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: gateway service boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: gateway service boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for gateway service boundary.
- Remaining Gap: GAP-R2-042
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use gateway service boundary as a library, worker, provider or delete it.
- Delta Ref: D005
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q043

- Question ID: Q043
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. context precedence must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: context precedence contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Matter Fact, Session Observation and User Preference conflict in one ContextPack; which source has precedence?
- Target Decision: KEEP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: context precedence records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: context precedence is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for context precedence.
- Remaining Gap: GAP-R2-043
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use context precedence as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q044

- Question ID: Q044
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. write gate must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: write gate contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A model proposes a durable memory from an unverified answer; which Write Gate rejects or quarantines it?
- Target Decision: KEEP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: write gate records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: write gate is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for write gate.
- Remaining Gap: GAP-R2-044
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use write gate as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q045

- Question ID: Q045
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. promotion gate must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: promotion gate contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An Observation is useful in three Runs; what evidence allows promotion to Matter Context?
- Target Decision: KEEP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: promotion gate records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: promotion gate is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for promotion gate.
- Remaining Gap: GAP-R2-045
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use promotion gate as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q046

- Question ID: Q046
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. stale memory must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: stale memory contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A HumanDecision supersedes a remembered Finding; how is recall prevented from returning the old conclusion?
- Target Decision: KEEP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: stale memory records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: stale memory is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for stale memory.
- Remaining Gap: GAP-R2-046
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use stale memory as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q047

- Question ID: Q047
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. deletion tombstone must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: deletion tombstone contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A user deletes Matter memory while a Run checkpoint still references it; what may be loaded on resume?
- Target Decision: KEEP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: deletion tombstone records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: deletion tombstone is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for deletion tombstone.
- Remaining Gap: GAP-R2-047
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use deletion tombstone as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q048

- Question ID: Q048
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. OpenViking failure must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: OpenViking failure contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is OpenViking is unavailable during a Run; which Memory contract is preserved and what fallback is allowed?
- Target Decision: EXTERNALIZE
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: OpenViking failure records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: OpenViking failure is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for OpenViking failure.
- Remaining Gap: GAP-R2-048
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use OpenViking failure as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q049

- Question ID: Q049
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. tenant isolation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: tenant isolation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A shared context index returns a similar memory from another tenant; which gate blocks it before the model?
- Target Decision: MEASUREMENT_GAP
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: tenant isolation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: tenant isolation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for tenant isolation.
- Remaining Gap: GAP-R2-049
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use tenant isolation as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q050

- Question ID: Q050
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. checkpoint distinction must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: checkpoint distinction contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A LangGraph checkpoint contains prior messages; why is that not permission to treat them as Canonical Fact?
- Target Decision: CLARIFY
- Owner: Memory Policy Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Memory Policy Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: checkpoint distinction records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: checkpoint distinction is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for checkpoint distinction.
- Remaining Gap: GAP-R2-050
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use checkpoint distinction as a library, worker, provider or delete it.
- Delta Ref: D006
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q051

- Question ID: Q051
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. plan for one step must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: plan for one step contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is For deterministic Retrieve→Answer, what does a Plan record that prevents it becoming hidden execution?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: plan for one step records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: plan for one step is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for plan for one step.
- Remaining Gap: GAP-R2-051
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use plan for one step as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q052

- Question ID: Q052
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. plan activation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: plan activation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A PlanVersion is activated and then a user changes the task; may the existing Plan be mutated?
- Target Decision: CLARIFY
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: plan activation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: plan activation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for plan activation.
- Remaining Gap: GAP-R2-052
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use plan activation as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q053

- Question ID: Q053
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. dag dependency must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: dag dependency contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Step B requires Evidence from Step A but the scheduler sees only completion flags; what contract prevents early dispatch?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: dag dependency records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: dag dependency is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for dag dependency.
- Remaining Gap: GAP-R2-053
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use dag dependency as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q054

- Question ID: Q054
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. parallel barrier must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: parallel barrier contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Three parallel research steps finish at different DomainVersions; what exactly does the Join Barrier compare?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: parallel barrier records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: parallel barrier is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for parallel barrier.
- Remaining Gap: GAP-R2-054
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use parallel barrier as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q055

- Question ID: Q055
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. reducer determinism must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: reducer determinism contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Two equivalent Proposal messages arrive in different order; can the reducer produce different Domain output?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: reducer determinism records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: reducer determinism is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for reducer determinism.
- Remaining Gap: GAP-R2-055
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use reducer determinism as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q056

- Question ID: Q056
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. replan trigger must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: replan trigger contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is What domain or evidence change is strong enough to create P4 instead of allowing the model to improvise?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: replan trigger records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: replan trigger is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for replan trigger.
- Remaining Gap: GAP-R2-056
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use replan trigger as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q057

- Question ID: Q057
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. retry vs replan must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: retry vs replan contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A transient Retriever timeout occurs under the same DomainVersion; why is Retry not Replan?
- Target Decision: CLARIFY
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: retry vs replan records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: retry vs replan is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for retry vs replan.
- Remaining Gap: GAP-R2-057
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use retry vs replan as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q058

- Question ID: Q058
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. reflection trigger must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: reflection trigger contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is What measurable condition causes Step Reflection, and when is reflection deleted as no-value overhead?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: reflection trigger records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: reflection trigger is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for reflection trigger.
- Remaining Gap: GAP-R2-058
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use reflection trigger as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q059

- Question ID: Q059
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. reflexion bound must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: reflexion bound contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Reflexion loop keeps criticizing its own answer; which budget, state and stop gate end it?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: reflexion bound records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: reflexion bound is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for reflexion bound.
- Remaining Gap: GAP-R2-059
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use reflexion bound as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q060

- Question ID: Q060
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. budget exhaustion must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: budget exhaustion contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Token budget ends after a tool Proposal but before Domain validation; what is persisted and what is not complete?
- Target Decision: DEFER
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: budget exhaustion records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: budget exhaustion is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for budget exhaustion.
- Remaining Gap: GAP-R2-060
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use budget exhaustion as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q061

- Question ID: Q061
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. hitl resume must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: hitl resume contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A reviewer approves a Finding after the SecurityEpoch changed; can the interrupt resume directly?
- Target Decision: CLARIFY
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: hitl resume records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: hitl resume is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for hitl resume.
- Remaining Gap: GAP-R2-061
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use hitl resume as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q062

- Question ID: Q062
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. cancellation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: cancellation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Cancellation arrives while a read-only retrieval and an irreversible Tool Effect are both active; how do their states differ?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: cancellation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: cancellation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for cancellation.
- Remaining Gap: GAP-R2-062
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use cancellation as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q063

- Question ID: Q063
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. run generation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: run generation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Two workers resume the same AgentRun generation; which CAS or lease prevents duplicate Domain commit?
- Target Decision: KEEP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: run generation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: run generation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for run generation.
- Remaining Gap: GAP-R2-063
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use run generation as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q064

- Question ID: Q064
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. checkpoint compatibility must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: checkpoint compatibility contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A deployed graph changes node names while an old checkpoint is pending; how is compatibility checked?
- Target Decision: IMPLEMENTATION_GAP
- Owner: Agent Runtime Service
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Agent Runtime Service.
- Failure: Failure is classified at the boundary instead of being converted to success: checkpoint compatibility records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: checkpoint compatibility is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for checkpoint compatibility.
- Remaining Gap: GAP-R2-064
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use checkpoint compatibility as a library, worker, provider or delete it.
- Delta Ref: D007
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q065

- Question ID: Q065
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. capability version must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: capability version contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is EVENT_EXTRACTION v2 adds a required field; can a v1 Agent accept the proposal without an adapter?
- Target Decision: KEEP
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: capability version records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: capability version is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for capability version.
- Remaining Gap: GAP-R2-065
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use capability version as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q066

- Question ID: Q066
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. proposal validation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: proposal validation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A ConflictProposal has valid JSON but references an inaccessible EvidenceCandidate; which validator rejects it?
- Target Decision: KEEP
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: proposal validation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: proposal validation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for proposal validation.
- Remaining Gap: GAP-R2-066
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use proposal validation as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q067

- Question ID: Q067
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. deterministic algorithm must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: deterministic algorithm contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A legal algorithm and an LLM disagree on Fact–Article Mapping; how are candidates compared and who commits?
- Target Decision: KEEP
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: deterministic algorithm records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: deterministic algorithm is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for deterministic algorithm.
- Remaining Gap: GAP-R2-067
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use deterministic algorithm as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 5/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q068

- Question ID: Q068
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. license boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: license boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An official repository has no LICENSE but its paper is public; what can be used, linked, or reimplemented?
- Target Decision: EXTERNALIZE
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: license boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: license boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for license boundary.
- Remaining Gap: GAP-R2-068
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use license boundary as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q069

- Question ID: Q069
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. capability timeout must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: capability timeout contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A capability provider times out after producing a partial result; is that Observation, Failure, or Unknown Effect?
- Target Decision: KEEP
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: capability timeout records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: capability timeout is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for capability timeout.
- Remaining Gap: GAP-R2-069
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use capability timeout as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q070

- Question ID: Q070
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. skill capability boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: skill capability boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Skill says how to identify a dispute while Capability exposes detection; which layer owns legal semantics?
- Target Decision: KEEP
- Owner: Legal Capability Contract Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Legal Capability Contract Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: skill capability boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: skill capability boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for skill capability boundary.
- Remaining Gap: GAP-R2-070
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use skill capability boundary as a library, worker, provider or delete it.
- Delta Ref: D008
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q071

- Question ID: Q071
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. tool visibility must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: tool visibility contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Tool is visible in a prompt but not authorized for the Matter; which catalog state is returned?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: tool visibility records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: tool visibility is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for tool visibility.
- Remaining Gap: GAP-R2-071
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use tool visibility as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q072

- Question ID: Q072
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. prepared action hash must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: prepared action hash contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Arguments change after approval but before execution; which canonical hash invalidates the action?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: prepared action hash records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: prepared action hash is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for prepared action hash.
- Remaining Gap: GAP-R2-072
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use prepared action hash as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q073

- Question ID: Q073
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. execute authorization must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: execute authorization contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A tenant grant is revoked after approval and before execution; which service performs the final check?
- Target Decision: IMPLEMENTATION_GAP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: execute authorization records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: execute authorization is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for execute authorization.
- Remaining Gap: GAP-R2-073
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use execute authorization as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q074

- Question ID: Q074
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. unknown effect must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: unknown effect contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An external court API times out after accepting a request; why is retry forbidden before reconciliation?
- Target Decision: CLARIFY
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: unknown effect records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: unknown effect is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for unknown effect.
- Remaining Gap: GAP-R2-074
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use unknown effect as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q075

- Question ID: Q075
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. operation identity must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: operation identity contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is The provider lacks idempotency but returns an operation ID only after execution; how is duplicate risk contained?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: operation identity records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: operation identity is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for operation identity.
- Remaining Gap: GAP-R2-075
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use operation identity as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q076

- Question ID: Q076
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. receipt persistence must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: receipt persistence contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Tool succeeded but EffectReceipt write failed; what durable record is reconstructed first?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: receipt persistence records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: receipt persistence is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for receipt persistence.
- Remaining Gap: GAP-R2-076
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use receipt persistence as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q077

- Question ID: Q077
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. tool version must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: tool version contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is MCP ToolVersion changes a side-effect schema while a Plan is paused; can the old PreparedAction run?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: tool version records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: tool version is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for tool version.
- Remaining Gap: GAP-R2-077
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use tool version as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q078

- Question ID: Q078
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. sandbox boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: sandbox boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Python parser needs filesystem access but no network; which sandbox policy is least privilege?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: sandbox boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: sandbox boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for sandbox boundary.
- Remaining Gap: GAP-R2-078
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use sandbox boundary as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q079

- Question ID: Q079
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. mcp metadata must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: mcp metadata contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is An MCP server returns a malicious description that asks the model to reveal a secret; where is it untrusted?
- Target Decision: KEEP
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: mcp metadata records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: mcp metadata is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for mcp metadata.
- Remaining Gap: GAP-R2-079
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use mcp metadata as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q080

- Question ID: Q080
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. effect reconciliation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: effect reconciliation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Domain commit references an EffectReceipt whose provider status is unknown; which state remains visible to the user?
- Target Decision: CLARIFY
- Owner: Tool / Sandbox Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Tool / Sandbox Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: effect reconciliation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: effect reconciliation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for effect reconciliation.
- Remaining Gap: GAP-R2-080
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use effect reconciliation as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q081

- Question ID: Q081
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. tenant isolation must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: tenant isolation contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A valid user token is replayed with another tenant ID in a Tool request; what decision input catches it?
- Target Decision: KEEP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: tenant isolation records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: tenant isolation is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for tenant isolation.
- Remaining Gap: GAP-R2-081
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use tenant isolation as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q082

- Question ID: Q082
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. prompt injection must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: prompt injection contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A court PDF asks the Agent to disable approval; which untrusted-data boundary prevents policy mutation?
- Target Decision: CLARIFY
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: prompt injection records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: prompt injection is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for prompt injection.
- Remaining Gap: GAP-R2-082
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use prompt injection as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q083

- Question ID: Q083
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. secret scope must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: secret scope contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A secret is mounted for one Tool Attempt; how do Model, Trace, Memory and error logs prove they did not receive it?
- Target Decision: KEEP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: secret scope records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: secret scope is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for secret scope.
- Remaining Gap: GAP-R2-083
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use secret scope as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q084

- Question ID: Q084
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. no egress must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: no egress contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Offline mode starts with a permissive dependency that attempts telemetry; what test and allowlist prove zero egress?
- Target Decision: MEASUREMENT_GAP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: no egress records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: no egress is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for no egress.
- Remaining Gap: GAP-R2-084
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use no egress as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q085

- Question ID: Q085
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. sandbox escape must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: sandbox escape contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A parser executes a subprocess outside its intended filesystem; which boundary and evidence classify the failure?
- Target Decision: KEEP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: sandbox escape records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: sandbox escape is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for sandbox escape.
- Remaining Gap: GAP-R2-085
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use sandbox escape as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q086

- Question ID: Q086
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. approval expiry must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: approval expiry contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Human approval expires while a queue message is delayed; can the Worker use the old Approval?
- Target Decision: KEEP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: approval expiry records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: approval expiry is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for approval expiry.
- Remaining Gap: GAP-R2-086
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use approval expiry as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q087

- Question ID: Q087
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. audit tamper must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: audit tamper contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A service reports a successful Domain Decision but omits the model and Tool traces; which audit completeness gate rejects release?
- Target Decision: DEFER
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: audit tamper records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: audit tamper is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for audit tamper.
- Remaining Gap: GAP-R2-087
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use audit tamper as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q088

- Question ID: Q088
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. artifact supply chain must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: artifact supply chain contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A container image digest differs from the signed release manifest; which deployment state is allowed?
- Target Decision: KEEP
- Owner: Security Decision Owner
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Security Decision Owner.
- Failure: Failure is classified at the boundary instead of being converted to success: artifact supply chain records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: artifact supply chain is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for artifact supply chain.
- Remaining Gap: GAP-R2-088
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use artifact supply chain as a library, worker, provider or delete it.
- Delta Ref: D009
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q089

- Question ID: Q089
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. metric denominator must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: metric denominator contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A system abstains on unsupported Claims; how do Evidence Sufficiency, Task Completion and Unsupported Claim Rate count it?
- Target Decision: KEEP
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: metric denominator records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: metric denominator is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for metric denominator.
- Remaining Gap: GAP-R2-089
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use metric denominator as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 5/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q090

- Question ID: Q090
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. abc randomization must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: abc randomization contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A/B/C variants see different case difficulty; what split and assignment protocol keeps comparison fair?
- Target Decision: MEASUREMENT_GAP
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: abc randomization records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: abc randomization is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for abc randomization.
- Remaining Gap: GAP-R2-090
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use abc randomization as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q091

- Question ID: Q091
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. ablation attribution must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: ablation attribution contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Graph, Memory and Multi-Agent are enabled together; which ablation isolates their causal contribution?
- Target Decision: KEEP
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: ablation attribution records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: ablation attribution is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for ablation attribution.
- Remaining Gap: GAP-R2-091
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use ablation attribution as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q092

- Question ID: Q092
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. court qa review must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: court qa review contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Court QA reference answers disagree among reviewers; who resolves the rubric before scoring?
- Target Decision: MEASUREMENT_GAP
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: court qa review records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: court qa review is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for court qa review.
- Remaining Gap: GAP-R2-092
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use court qa review as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q093

- Question ID: Q093
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. release regression must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: release regression contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A new Reranker improves Recall but worsens Citation Correctness; which release gate blocks adoption?
- Target Decision: DEFER
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: release regression records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: release regression is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for release regression.
- Remaining Gap: GAP-R2-093
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use release regression as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q094

- Question ID: Q094
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. telemetry and eval must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: telemetry and eval contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Operational traces contain secrets or hidden reasoning; what is retained for audit without persisting chain of thought?
- Target Decision: KEEP
- Owner: Eval / Observability
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Eval / Observability.
- Failure: Failure is classified at the boundary instead of being converted to success: telemetry and eval records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: telemetry and eval is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for telemetry and eval.
- Remaining Gap: GAP-R2-094
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use telemetry and eval as a library, worker, provider or delete it.
- Delta Ref: D010
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q095

- Question ID: Q095
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. service boundary must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: service boundary contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A candidate service has no independent scaling or security need but has a clean package boundary; why is it not a library?
- Target Decision: KEEP
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: service boundary records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: service boundary is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for service boundary.
- Remaining Gap: GAP-R2-095
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use service boundary as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q096

- Question ID: Q096
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. queue semantics must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: queue semantics contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A Job is delivered twice after lease expiry; how do JobId, Attempt, Idempotency and DLQ interact?
- Target Decision: KEEP
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: queue semantics records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: queue semantics is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for queue semantics.
- Remaining Gap: GAP-R2-096
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use queue semantics as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q097

- Question ID: Q097
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. physical database must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: physical database contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Knowledge wants its own PostgreSQL instance for autonomy but no distinct SLO exists; what evidence is missing?
- Target Decision: IMPLEMENTATION_GAP
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: physical database records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: physical database is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for physical database.
- Remaining Gap: GAP-R2-097
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use physical database as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 2/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q098

- Question ID: Q098
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. retry storm must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: retry storm contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A model timeout causes three queues to retry simultaneously; where are budgets, backpressure and circuit breaks enforced?
- Target Decision: KEEP
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: retry storm records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: retry storm is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for retry storm.
- Remaining Gap: GAP-R2-098
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use retry storm as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q099

- Question ID: Q099
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. rollback compatibility must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: rollback compatibility contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is A service rolls back code while messages use a newer schema; how is the compatibility window enforced?
- Target Decision: EXTERNALIZE
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: rollback compatibility records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: rollback compatibility is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for rollback compatibility.
- Remaining Gap: GAP-R2-099
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use rollback compatibility as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 3/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

## Q100

- Question ID: Q100
- Round ID: RB-WORKFLOW-V3-ROUND-002
- Blue Answer: The attacked assumption is not accepted as an unqualified fact. capacity heterogeneity must expose a typed boundary, record the owner and version it consumes, reject unsafe completion, and leave an auditable gap when the required evidence is absent.
- Current / Target / Future / History: Current: repository/design surface only where recorded; Target: capacity heterogeneity contract; Future: provider or topology refinement only after evidence; History: prior 11-module interpretation remains Superseded.
- Problem: The concrete risk is Peak users fall but concurrent Sandbox and OCR jobs rise; which scaling signal justifies separate workers?
- Target Decision: KEEP
- Owner: Service Architecture / Infrastructure
- State Transition: proposed → validated → authorized or review_required → committed, rejected, stale or reconciled; the exact terminal state is owned by Service Architecture / Infrastructure.
- Failure: Failure is classified at the boundary instead of being converted to success: capacity heterogeneity records the failed, unknown, stale or blocked condition.
- Failure Propagation: Downstream steps receive a typed failure, stale marker or Proposal status; Final Gate cannot publish an unsupported business result.
- Retry: Retry only transient, bounded, and idempotent work under the same input version; unknown side effects require reconciliation, not blind retry.
- Recovery: Reload the last valid DomainVersion, Runtime generation, receipt and policy epoch; reconcile before resume and create a new PlanVersion when the input contract changed.
- Idempotency: Use a stable operation identity derived from Run, Step, input version and provider operation; duplicate delivery must converge to one result.
- Security: Authorize the subject, tenant, scope, capability, tool/version and current SecurityEpoch at the execution boundary; untrusted content cannot change policy.
- Observability: Trace correlation includes Run, PlanVersion, StepRun, DomainVersion, Provider/Tool version, Evidence lineage, decision and receipt IDs without storing hidden chain of thought.
- Alternative: The simpler alternative remains valid if it passes the same contract, failure, security and benchmark checks: capacity heterogeneity is not protected by technology preference.
- OSS Alternative: An existing OSS or external Host may implement the mechanism; Zuno keeps only the domain contract, policy, evidence and audit boundary that must remain stable.
- Tradeoff: The refinement adds explicit state and trace fields but removes ambiguity, duplicate mutation and unmeasured provider coupling.
- Test / Benchmark: Replay the concrete scenario with stale input, duplicate delivery, permission change and provider failure; compare quality, latency, cost and recovery.
- Evidence: Target design is accepted; implementation, measured outcome and external qualification remain open for capacity heterogeneity.
- Remaining Gap: GAP-R2-100
- Reversal Condition: If the simpler alternative passes the same replay and benchmark with no quality, safety, recovery or ownership loss, use capacity heterogeneity as a library, worker, provider or delete it.
- Delta Ref: D011
- Red Score Context: 4/5 indicates the Blue defense still needs the recorded refinement or evidence boundary.

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/red-scores.md`

# Round-002 Red Scores

| Question ID | Lens | Score | Severity | Closure Class | Decision | Delta |
|---|---|---:|---|---|---|---|
| Q001 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q002 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q003 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q004 | 00 Overall Architecture | 3 | P1 | NONE | CLARIFY | D001 |
| Q005 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q006 | 00 Overall Architecture | 2 | P0 | P0-I | IMPLEMENTATION_GAP | D001 |
| Q007 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q008 | 00 Overall Architecture | 4 | P1 | NONE | KEEP | D001 |
| Q009 | 00 Overall Architecture | 4 | P2 | NONE | MEASUREMENT_GAP | D001 |
| Q010 | 00 Overall Architecture | 4 | P2 | NONE | KEEP | D001 |
| Q011 | 00 Overall Architecture | 4 | P2 | NONE | DEFER | D001 |
| Q012 | 00 Overall Architecture | 4 | P1 | NONE | KEEP | D001 |
| Q013 | 01 Product Surface | 4 | P2 | NONE | KEEP | D002 |
| Q014 | 01 Product Surface | 4 | P2 | NONE | KEEP | D002 |
| Q015 | 01 Product Surface | 4 | P2 | NONE | KEEP | D002 |
| Q016 | 01 Product Surface | 4 | P1 | NONE | KEEP | D002 |
| Q017 | 01 Product Surface | 4 | P2 | NONE | KEEP | D002 |
| Q018 | 01 Product Surface | 3 | P2 | NONE | CLARIFY | D002 |
| Q019 | 02 Input / Document Ingestion | 4 | P2 | NONE | KEEP | D003 |
| Q020 | 02 Input / Document Ingestion | 3 | P1 | NONE | CLARIFY | D003 |
| Q021 | 02 Input / Document Ingestion | 4 | P2 | NONE | KEEP | D003 |
| Q022 | 02 Input / Document Ingestion | 4 | P2 | NONE | KEEP | D003 |
| Q023 | 02 Input / Document Ingestion | 4 | P2 | NONE | KEEP | D003 |
| Q024 | 02 Input / Document Ingestion | 4 | P1 | NONE | KEEP | D003 |
| Q025 | 02 Input / Document Ingestion | 3 | P2 | NONE | CLARIFY | D003 |
| Q026 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | KEEP | D004 |
| Q027 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | KEEP | D004 |
| Q028 | 03 Knowledge / Agentic GraphRAG | 4 | P1 | NONE | KEEP | D004 |
| Q029 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | KEEP | D004 |
| Q030 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | KEEP | D004 |
| Q031 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | KEEP | D004 |
| Q032 | 03 Knowledge / Agentic GraphRAG | 4 | P1 | NONE | KEEP | D004 |
| Q033 | 03 Knowledge / Agentic GraphRAG | 2 | P0 | P0-I | IMPLEMENTATION_GAP | D004 |
| Q034 | 03 Knowledge / Agentic GraphRAG | 3 | P2 | NONE | CLARIFY | D004 |
| Q035 | 03 Knowledge / Agentic GraphRAG | 4 | P2 | NONE | DEFER | D004 |
| Q036 | 03 Knowledge / Agentic GraphRAG | 4 | P1 | NONE | KEEP | D004 |
| Q037 | 04 Model Gateway | 4 | P2 | NONE | KEEP | D005 |
| Q038 | 04 Model Gateway | 4 | P2 | NONE | KEEP | D005 |
| Q039 | 04 Model Gateway | 4 | P2 | NONE | KEEP | D005 |
| Q040 | 04 Model Gateway | 4 | P1 | NONE | KEEP | D005 |
| Q041 | 04 Model Gateway | 3 | P2 | NONE | CLARIFY | D005 |
| Q042 | 04 Model Gateway | 4 | P2 | NONE | EXTERNALIZE | D005 |
| Q043 | 05 Memory & Context | 4 | P2 | NONE | KEEP | D006 |
| Q044 | 05 Memory & Context | 4 | P1 | NONE | KEEP | D006 |
| Q045 | 05 Memory & Context | 4 | P2 | NONE | KEEP | D006 |
| Q046 | 05 Memory & Context | 4 | P2 | NONE | KEEP | D006 |
| Q047 | 05 Memory & Context | 4 | P2 | NONE | KEEP | D006 |
| Q048 | 05 Memory & Context | 4 | P1 | NONE | EXTERNALIZE | D006 |
| Q049 | 05 Memory & Context | 2 | P0 | P0-E | MEASUREMENT_GAP | D006 |
| Q050 | 05 Memory & Context | 3 | P2 | NONE | CLARIFY | D006 |
| Q051 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q052 | 06 Agent Core / Planning & Control | 3 | P1 | NONE | CLARIFY | D007 |
| Q053 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q054 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q055 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q056 | 06 Agent Core / Planning & Control | 4 | P1 | NONE | KEEP | D007 |
| Q057 | 06 Agent Core / Planning & Control | 3 | P2 | NONE | CLARIFY | D007 |
| Q058 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q059 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q060 | 06 Agent Core / Planning & Control | 4 | P1 | NONE | DEFER | D007 |
| Q061 | 06 Agent Core / Planning & Control | 3 | P2 | NONE | CLARIFY | D007 |
| Q062 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q063 | 06 Agent Core / Planning & Control | 4 | P2 | NONE | KEEP | D007 |
| Q064 | 06 Agent Core / Planning & Control | 2 | P0 | P0-I | IMPLEMENTATION_GAP | D007 |
| Q065 | 07 Capability / Skill | 4 | P2 | NONE | KEEP | D008 |
| Q066 | 07 Capability / Skill | 4 | P2 | NONE | KEEP | D008 |
| Q067 | 07 Capability / Skill | 5 | P2 | NONE | KEEP | D008 |
| Q068 | 07 Capability / Skill | 4 | P1 | NONE | EXTERNALIZE | D008 |
| Q069 | 07 Capability / Skill | 4 | P2 | NONE | KEEP | D008 |
| Q070 | 07 Capability / Skill | 4 | P2 | NONE | KEEP | D008 |
| Q071 | 08 Tool Runtime | 4 | P2 | NONE | KEEP | D009 |
| Q072 | 08 Tool Runtime | 4 | P1 | NONE | KEEP | D009 |
| Q073 | 08 Tool Runtime | 2 | P0 | P0-I | IMPLEMENTATION_GAP | D009 |
| Q074 | 08 Tool Runtime | 3 | P2 | NONE | CLARIFY | D009 |
| Q075 | 08 Tool Runtime | 4 | P2 | NONE | KEEP | D009 |
| Q076 | 08 Tool Runtime | 4 | P1 | NONE | KEEP | D009 |
| Q077 | 08 Tool Runtime | 4 | P2 | NONE | KEEP | D009 |
| Q078 | 08 Tool Runtime | 4 | P2 | NONE | KEEP | D009 |
| Q079 | 08 Tool Runtime | 4 | P2 | NONE | KEEP | D009 |
| Q080 | 08 Tool Runtime | 3 | P1 | NONE | CLARIFY | D009 |
| Q081 | 09 Security | 4 | P2 | NONE | KEEP | D009 |
| Q082 | 09 Security | 3 | P2 | NONE | CLARIFY | D009 |
| Q083 | 09 Security | 4 | P2 | NONE | KEEP | D009 |
| Q084 | 09 Security | 2 | P0 | P0-E | MEASUREMENT_GAP | D009 |
| Q085 | 09 Security | 4 | P2 | NONE | KEEP | D009 |
| Q086 | 09 Security | 4 | P2 | NONE | KEEP | D009 |
| Q087 | 09 Security | 4 | P2 | NONE | DEFER | D009 |
| Q088 | 09 Security | 4 | P1 | NONE | KEEP | D009 |
| Q089 | 10 Observability & Eval | 5 | P2 | NONE | KEEP | D010 |
| Q090 | 10 Observability & Eval | 2 | P0 | P0-E | MEASUREMENT_GAP | D010 |
| Q091 | 10 Observability & Eval | 4 | P2 | NONE | KEEP | D010 |
| Q092 | 10 Observability & Eval | 3 | P1 | NONE | MEASUREMENT_GAP | D010 |
| Q093 | 10 Observability & Eval | 4 | P2 | NONE | DEFER | D010 |
| Q094 | 10 Observability & Eval | 4 | P2 | NONE | KEEP | D010 |
| Q095 | 11 Infrastructure | 4 | P2 | NONE | KEEP | D011 |
| Q096 | 11 Infrastructure | 4 | P1 | NONE | KEEP | D011 |
| Q097 | 11 Infrastructure | 2 | P0 | P0-I | IMPLEMENTATION_GAP | D011 |
| Q098 | 11 Infrastructure | 4 | P2 | NONE | KEEP | D011 |
| Q099 | 11 Infrastructure | 3 | P2 | NONE | EXTERNALIZE | D011 |
| Q100 | 11 Infrastructure | 4 | P1 | NONE | KEEP | D011 |

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/chatgpt-review-package.md`

# ChatGPT Review Package — RB-WORKFLOW-V3-ROUND-002

BASE_SHA: 19ba6e050e1334f71c511a5968c9ea9d15c68111
FINAL_SHA: recorded in final handoff
Workflow Version: ZUNO-RED-BLUE-WORKFLOW-V3
Round ID: RB-WORKFLOW-V3-ROUND-002

## Scores

- Questions / Answers / Scores / Decisions: 100 / 100 / 100 / 100
- Raw Score: 371/500
- Normalized Score: 74.20/100
- Novel / Regression: 80 / 20
- 11+1 Scores: see scorecard.md
- P0/P1/P2/P3: 8 / 23 / 69 / 0
- A/I/E/X: 0 / 5 / 3 / 0

## Lowest 20 Questions

Q006 new evidence invalidation — 2/5
Q033 citation binding — 2/5
Q049 tenant isolation — 2/5
Q064 checkpoint compatibility — 2/5
Q073 execute authorization — 2/5
Q084 no egress — 2/5
Q090 abc randomization — 2/5
Q097 physical database — 2/5
Q004 main runtime flow — 3/5
Q018 external host replacement — 3/5
Q020 ingestion ordering — 3/5
Q025 ingestion security — 3/5
Q034 stale index — 3/5
Q041 offline model — 3/5
Q050 checkpoint distinction — 3/5
Q052 plan activation — 3/5
Q057 retry vs replan — 3/5
Q061 hitl resume — 3/5
Q074 unknown effect — 3/5
Q080 effect reconciliation — 3/5

## Highest-risk 20 Questions

Q006 new evidence invalidation — P0 — P0-I
Q033 citation binding — P0 — P0-I
Q049 tenant isolation — P0 — P0-E
Q064 checkpoint compatibility — P0 — P0-I
Q073 execute authorization — P0 — P0-I
Q084 no egress — P0 — P0-E
Q090 abc randomization — P0 — P0-E
Q097 physical database — P0 — P0-I
Q004 main runtime flow — P1 — NONE
Q008 ordinary JSON alternative — P1 — NONE
Q012 failure invariant — P1 — NONE
Q016 court workflow unknown — P1 — NONE
Q020 ingestion ordering — P1 — NONE
Q024 corrupt artifact — P1 — NONE
Q028 query rewrite budget — P1 — NONE
Q032 cross document path — P1 — NONE
Q036 scope and ACL — P1 — NONE
Q040 call trace — P1 — NONE
Q044 write gate — P1 — NONE
Q048 OpenViking failure — P1 — NONE

## Architecture Deltas

D001 Overall architecture / Domain-State admission — AUTO_APPLY
D002 Product Host boundary and delivery semantics — AUTO_APPLY
D003 Ingestion provenance and idempotent publication — AUTO_APPLY
D004 Conditional retrieval and citation lineage — AUTO_APPLY
D005 Model Provider and Gateway replaceability — AUTO_APPLY
D006 Memory Policy and provider boundary — AUTO_APPLY
D007 PlanVersion, DAG, reflection and runtime recovery — AUTO_APPLY
D008 Capability Contract and legal provider governance — AUTO_APPLY
D009 Tool Effect, Approval and Security enforcement — AUTO_APPLY
D010 Legal Eval, attribution and release gates — AUTO_APPLY
D011 Service, Queue, Storage and Deployment evidence — AUTO_APPLY

## Components

- KEEP: Domain State, Evidence Contract, Single Controller, Plan/DAG, Human Review, Security/Eval boundaries.
- REFINE: Version admission, Citation, Memory Policy, Tool Receipt, Queue and Service evidence contracts.
- REPLACE / EXTERNALIZE: concrete Memory/Model/Graph/Tool providers when they lack independent value.
- DELETE: no required core deletion in this Round; unmeasured provider lock-in remains prohibited.

## Changes

- Service Boundary: candidate roles remain revisable; worker vs service evidence is explicit.
- Database / Storage: SoR, Projection, Runtime, Cache, Artifact and Queue roles clarified.
- Memory: OpenViking remains replaceable Provider under Zuno policy gates.
- Agent Runtime: PlanVersion, DomainVersion, reducer, barrier and reconciliation refinements.
- Tool / Security: approval binding, execute-time authorization and unknown-effect reconciliation.
- Eval: denominator, fair A/B/C, ablation, reviewer and release gate refinements.
- Canonical files: see canonical-sync-record.md.
- ADR/User Escalations: none.

## Contradictions / gaps

No new A-P0. I-P0, E-P0 and external security/deployment qualification remain open. Historical Facts,
Current implementation and Production Readiness were not promoted or changed.

## Proposed Round-003 Focus

Run only after user review of this package: cross-state implementation evidence, Court QA protocol,
real Sandbox qualification and provider ablation. Status: READY_NOT_STARTED.

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/scorecard.md`

# Round-002 Scorecard

```yaml
protocol_version: ZUNO-RED-BLUE-WORKFLOW-V3
round_id: RB-WORKFLOW-V3-ROUND-002
question_count: 100
answer_count: 100
score_count: 100
decision_count: 100
novelty_status: ASSESSED
novel_question_count: 80
regression_question_count: 20
raw_score: 371
normalized_score: 74.20
grade: Architecture Requires Significant Repair
new_a_p0: 0
p0_count: 8
p1_count: 23
p2_count: 69
p3_count: 0
closure_class_counts:
  A: 0
  I: 5
  E: 3
  X: 0
canonical_sync_status: APPLIED
round_status: COMPLETE
round_003_status: READY_NOT_STARTED
```

| Lens | Questions | Raw Score | Normalized |
|---|---:|---:|---:|
| 00 Overall Architecture | 12 | 45 | 75.00 |
| 01 Product Surface | 6 | 23 | 76.67 |
| 02 Input / Document Ingestion | 7 | 26 | 74.29 |
| 03 Knowledge / Agentic GraphRAG | 11 | 41 | 74.55 |
| 04 Model Gateway | 6 | 23 | 76.67 |
| 05 Memory & Context | 8 | 29 | 72.50 |
| 06 Agent Core / Planning & Control | 14 | 51 | 72.86 |
| 07 Capability / Skill | 6 | 25 | 83.33 |
| 08 Tool Runtime | 10 | 36 | 72.00 |
| 09 Security | 8 | 29 | 72.50 |
| 10 Observability & Eval | 6 | 22 | 73.33 |
| 11 Infrastructure | 6 | 21 | 70.00 |

Total Raw Score: 371/500
Normalized Score: 74.20/100

Score is a defense diagnostic, not Production Readiness.

## Decision summary

- AUTO_APPLY deltas: 11
- ADR Escalation: 0
- User Gate Escalation: 0
- New A-P0: 0
- I/E/X gaps remain open; no P0 is closed by this Round.

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/blue-decisions.md`

# Round-002 Blue Decisions

Each decision is final for this Round and traces to one Delta.

## Q001

- Question ID: Q001
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in Product thesis acceptance.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The Product thesis acceptance contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If Product thesis acceptance passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q002

- Question ID: Q002
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in Canonical state admission.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The Canonical state admission contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If Canonical state admission passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q003

- Question ID: Q003
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in Owner registry drift.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The Owner registry drift contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If Owner registry drift passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q004

- Question ID: Q004
- Red Score: 3/5
- Red Finding: The attack exposed a P1 boundary risk in main runtime flow.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The main runtime flow contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D001
- Reversal Condition: If main runtime flow passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q005

- Question ID: Q005
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in cross-state reconciliation.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The cross-state reconciliation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If cross-state reconciliation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q006

- Question ID: Q006
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in new evidence invalidation.
- Blue Decision: IMPLEMENTATION_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The new evidence invalidation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: YES
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If new evidence invalidation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q007

- Question ID: Q007
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in accepted target maturity.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The accepted target maturity contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If accepted target maturity passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q008

- Question ID: Q008
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in ordinary JSON alternative.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The ordinary JSON alternative contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If ordinary JSON alternative passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q009

- Question ID: Q009
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in host sufficiency.
- Blue Decision: MEASUREMENT_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The host sufficiency contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: YES
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If host sufficiency passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q010

- Question ID: Q010
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in architecture trace.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The architecture trace contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If architecture trace passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q011

- Question ID: Q011
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in necessary complexity floor.
- Blue Decision: DEFER
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The necessary complexity floor contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid premature implementation or topology commitment.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If necessary complexity floor passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q012

- Question ID: Q012
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in failure invariant.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The failure invariant contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D001
- Reversal Condition: If failure invariant passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q013

- Question ID: Q013
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in matter command.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The matter command contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D002
- Reversal Condition: If matter command passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q014

- Question ID: Q014
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in host mutation boundary.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The host mutation boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D002
- Reversal Condition: If host mutation boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q015

- Question ID: Q015
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in review delivery.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The review delivery contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D002
- Reversal Condition: If review delivery passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q016

- Question ID: Q016
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in court workflow unknown.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The court workflow unknown contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D002
- Reversal Condition: If court workflow unknown passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q017

- Question ID: Q017
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in partial response.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The partial response contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D002
- Reversal Condition: If partial response passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q018

- Question ID: Q018
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in external host replacement.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The external host replacement contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D002
- Reversal Condition: If external host replacement passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q019

- Question ID: Q019
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in document identity.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The document identity contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D003
- Reversal Condition: If document identity passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q020

- Question ID: Q020
- Red Score: 3/5
- Red Finding: The attack exposed a P1 boundary risk in ingestion ordering.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The ingestion ordering contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D003
- Reversal Condition: If ingestion ordering passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q021

- Question ID: Q021
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in parser provenance.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The parser provenance contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D003
- Reversal Condition: If parser provenance passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q022

- Question ID: Q022
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in duplicate upload.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The duplicate upload contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D003
- Reversal Condition: If duplicate upload passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q023

- Question ID: Q023
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in retention deletion.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The retention deletion contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D003
- Reversal Condition: If retention deletion passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q024

- Question ID: Q024
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in corrupt artifact.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The corrupt artifact contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D003
- Reversal Condition: If corrupt artifact passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q025

- Question ID: Q025
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in ingestion security.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The ingestion security contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D003
- Reversal Condition: If ingestion security passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q026

- Question ID: Q026
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in query class routing.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The query class routing contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If query class routing passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q027

- Question ID: Q027
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in hybrid fusion.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The hybrid fusion contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If hybrid fusion passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q028

- Question ID: Q028
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in query rewrite budget.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The query rewrite budget contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If query rewrite budget passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q029

- Question ID: Q029
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in reranker attribution.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The reranker attribution contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If reranker attribution passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q030

- Question ID: Q030
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in graph admission.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The graph admission contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If graph admission passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q031

- Question ID: Q031
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in graph edge correction.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The graph edge correction contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If graph edge correction passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q032

- Question ID: Q032
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in cross document path.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The cross document path contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If cross document path passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q033

- Question ID: Q033
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in citation binding.
- Blue Decision: IMPLEMENTATION_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The citation binding contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: YES
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If citation binding passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q034

- Question ID: Q034
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in stale index.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The stale index contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D004
- Reversal Condition: If stale index passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q035

- Question ID: Q035
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in evidence sufficiency.
- Blue Decision: DEFER
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The evidence sufficiency contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid premature implementation or topology commitment.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If evidence sufficiency passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q036

- Question ID: Q036
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in scope and ACL.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The scope and ACL contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D004
- Reversal Condition: If scope and ACL passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q037

- Question ID: Q037
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in provider normalization.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The provider normalization contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D005
- Reversal Condition: If provider normalization passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q038

- Question ID: Q038
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in fallback semantic drift.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The fallback semantic drift contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D005
- Reversal Condition: If fallback semantic drift passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q039

- Question ID: Q039
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in quota budget.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The quota budget contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D005
- Reversal Condition: If quota budget passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q040

- Question ID: Q040
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in call trace.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The call trace contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D005
- Reversal Condition: If call trace passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q041

- Question ID: Q041
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in offline model.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The offline model contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D005
- Reversal Condition: If offline model passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q042

- Question ID: Q042
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in gateway service boundary.
- Blue Decision: EXTERNALIZE
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The gateway service boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid a Zuno-owned mechanism by using a replaceable provider or Host.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D005
- Reversal Condition: If gateway service boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q043

- Question ID: Q043
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in context precedence.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The context precedence contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If context precedence passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q044

- Question ID: Q044
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in write gate.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The write gate contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If write gate passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q045

- Question ID: Q045
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in promotion gate.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The promotion gate contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If promotion gate passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q046

- Question ID: Q046
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in stale memory.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The stale memory contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If stale memory passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q047

- Question ID: Q047
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in deletion tombstone.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The deletion tombstone contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If deletion tombstone passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q048

- Question ID: Q048
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in OpenViking failure.
- Blue Decision: EXTERNALIZE
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The OpenViking failure contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid a Zuno-owned mechanism by using a replaceable provider or Host.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If OpenViking failure passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q049

- Question ID: Q049
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in tenant isolation.
- Blue Decision: MEASUREMENT_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The tenant isolation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: YES
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D006
- Reversal Condition: If tenant isolation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q050

- Question ID: Q050
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in checkpoint distinction.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The checkpoint distinction contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D006
- Reversal Condition: If checkpoint distinction passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q051

- Question ID: Q051
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in plan for one step.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The plan for one step contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If plan for one step passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q052

- Question ID: Q052
- Red Score: 3/5
- Red Finding: The attack exposed a P1 boundary risk in plan activation.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The plan activation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D007
- Reversal Condition: If plan activation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q053

- Question ID: Q053
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in dag dependency.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The dag dependency contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If dag dependency passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q054

- Question ID: Q054
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in parallel barrier.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The parallel barrier contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If parallel barrier passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q055

- Question ID: Q055
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in reducer determinism.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The reducer determinism contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If reducer determinism passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q056

- Question ID: Q056
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in replan trigger.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The replan trigger contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If replan trigger passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q057

- Question ID: Q057
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in retry vs replan.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The retry vs replan contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D007
- Reversal Condition: If retry vs replan passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q058

- Question ID: Q058
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in reflection trigger.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The reflection trigger contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If reflection trigger passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q059

- Question ID: Q059
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in reflexion bound.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The reflexion bound contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If reflexion bound passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q060

- Question ID: Q060
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in budget exhaustion.
- Blue Decision: DEFER
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The budget exhaustion contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid premature implementation or topology commitment.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If budget exhaustion passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q061

- Question ID: Q061
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in hitl resume.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The hitl resume contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D007
- Reversal Condition: If hitl resume passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q062

- Question ID: Q062
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in cancellation.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The cancellation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If cancellation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q063

- Question ID: Q063
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in run generation.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The run generation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If run generation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q064

- Question ID: Q064
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in checkpoint compatibility.
- Blue Decision: IMPLEMENTATION_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The checkpoint compatibility contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: YES
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D007
- Reversal Condition: If checkpoint compatibility passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q065

- Question ID: Q065
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in capability version.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The capability version contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If capability version passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q066

- Question ID: Q066
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in proposal validation.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The proposal validation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If proposal validation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q067

- Question ID: Q067
- Red Score: 5/5
- Red Finding: The attack exposed a P2 boundary risk in deterministic algorithm.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The deterministic algorithm contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If deterministic algorithm passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q068

- Question ID: Q068
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in license boundary.
- Blue Decision: EXTERNALIZE
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The license boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid a Zuno-owned mechanism by using a replaceable provider or Host.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If license boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q069

- Question ID: Q069
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in capability timeout.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The capability timeout contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If capability timeout passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q070

- Question ID: Q070
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in skill capability boundary.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The skill capability boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D008
- Reversal Condition: If skill capability boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q071

- Question ID: Q071
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in tool visibility.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The tool visibility contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If tool visibility passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q072

- Question ID: Q072
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in prepared action hash.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The prepared action hash contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If prepared action hash passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q073

- Question ID: Q073
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in execute authorization.
- Blue Decision: IMPLEMENTATION_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The execute authorization contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: YES
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If execute authorization passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q074

- Question ID: Q074
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in unknown effect.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The unknown effect contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D009
- Reversal Condition: If unknown effect passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q075

- Question ID: Q075
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in operation identity.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The operation identity contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If operation identity passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q076

- Question ID: Q076
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in receipt persistence.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The receipt persistence contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If receipt persistence passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q077

- Question ID: Q077
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in tool version.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The tool version contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If tool version passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q078

- Question ID: Q078
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in sandbox boundary.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The sandbox boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If sandbox boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q079

- Question ID: Q079
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in mcp metadata.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The mcp metadata contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If mcp metadata passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q080

- Question ID: Q080
- Red Score: 3/5
- Red Finding: The attack exposed a P1 boundary risk in effect reconciliation.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The effect reconciliation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D009
- Reversal Condition: If effect reconciliation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q081

- Question ID: Q081
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in tenant isolation.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The tenant isolation contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If tenant isolation passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q082

- Question ID: Q082
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in prompt injection.
- Blue Decision: CLARIFY
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The prompt injection contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: A narrow contract/evidence rule and trace reference.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: Yes: refinement only; no change to approved core principles.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: Yes: explicit transition or gate added.
- Failure Semantics Changed: Yes: failure/unknown/stale is not success.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: AUTO_APPLY
- Delta Ref: D009
- Reversal Condition: If prompt injection passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q083

- Question ID: Q083
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in secret scope.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The secret scope contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If secret scope passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q084

- Question ID: Q084
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in no egress.
- Blue Decision: MEASUREMENT_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The no egress contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: YES
- External Gap: YES
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If no egress passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q085

- Question ID: Q085
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in sandbox escape.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The sandbox escape contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If sandbox escape passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q086

- Question ID: Q086
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in approval expiry.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The approval expiry contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If approval expiry passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q087

- Question ID: Q087
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in audit tamper.
- Blue Decision: DEFER
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The audit tamper contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid premature implementation or topology commitment.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If audit tamper passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q088

- Question ID: Q088
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in artifact supply chain.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The artifact supply chain contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D009
- Reversal Condition: If artifact supply chain passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q089

- Question ID: Q089
- Red Score: 5/5
- Red Finding: The attack exposed a P2 boundary risk in metric denominator.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The metric denominator contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If metric denominator passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q090

- Question ID: Q090
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in abc randomization.
- Blue Decision: MEASUREMENT_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The abc randomization contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: YES
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If abc randomization passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q091

- Question ID: Q091
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in ablation attribution.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The ablation attribution contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If ablation attribution passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q092

- Question ID: Q092
- Red Score: 3/5
- Red Finding: The attack exposed a P1 boundary risk in court qa review.
- Blue Decision: MEASUREMENT_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The court qa review contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: YES
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If court qa review passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q093

- Question ID: Q093
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in release regression.
- Blue Decision: DEFER
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The release regression contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid premature implementation or topology commitment.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If release regression passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q094

- Question ID: Q094
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in telemetry and eval.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The telemetry and eval contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/eval/legal-eval-and-benchmark.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D010
- Reversal Condition: If telemetry and eval passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q095

- Question ID: Q095
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in service boundary.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The service boundary contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If service boundary passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q096

- Question ID: Q096
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in queue semantics.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The queue semantics contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If queue semantics passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q097

- Question ID: Q097
- Red Score: 2/5
- Red Finding: The attack exposed a P0 boundary risk in physical database.
- Blue Decision: IMPLEMENTATION_GAP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The physical database contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: YES
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If physical database passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q098

- Question ID: Q098
- Red Score: 4/5
- Red Finding: The attack exposed a P2 boundary risk in retry storm.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The retry storm contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If retry storm passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q099

- Question ID: Q099
- Red Score: 3/5
- Red Finding: The attack exposed a P2 boundary risk in rollback compatibility.
- Blue Decision: EXTERNALIZE
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The rollback compatibility contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Avoid a Zuno-owned mechanism by using a replaceable provider or Host.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If rollback compatibility passes no independent value test, downgrade to the simpler alternative named in the Question.

## Q100

- Question ID: Q100
- Red Score: 4/5
- Red Finding: The attack exposed a P1 boundary risk in capacity heterogeneity.
- Blue Decision: KEEP
- Decision Rationale: Preserve the necessary business capability, but make the owner, state, failure, evidence and reversal contract explicit.
- Architecture Before: The boundary was stated as a Target principle but did not name this counterexample or acceptance test.
- Architecture After: The capacity heterogeneity contract records the counterexample, typed state, owner, recovery behavior and deletion condition.
- Complexity Added: No mandatory runtime component; only a gap or provider qualification record.
- Complexity Removed: Remove ambiguity and unsafe implicit transitions.
- Contract Changed: No accepted Contract change; record the evidence or implementation gap.
- Owner Changed: No; ownership is clarified, not duplicated.
- State Changed: No; existing state remains and is measured later.
- Failure Semantics Changed: No; existing failure remains an open qualification or measurement item.
- Canonical Doc: docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md
- ADR Required?: NO
- Fact Gap?: NO
- Implementation Gap: NO
- Measurement Gap: NO
- External Gap: NO
- Sync Mode: SYNC_NONE
- Delta Ref: D011
- Reversal Condition: If capacity heterogeneity passes no independent value test, downgrade to the simpler alternative named in the Question.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/gap-register.md`

# Round-002 Gap Register

| Gap ID | Source Questions | Type | Owner | Current Boundary | Required Closure | Status |
|---|---|---|---|---|---|---|
| GAP-R2-001 | Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012 | I-P0 / IMPLEMENTATION | Architecture Owner | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Overall architecture / Domain-State admission | OPEN |
| GAP-R2-002 | Q013, Q014, Q015, Q016, Q017, Q018 | I-P0 / IMPLEMENTATION | Product / Domain Surface | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Product Host boundary and delivery semantics | OPEN |
| GAP-R2-003 | Q019, Q020, Q021, Q022, Q023, Q024, Q025 | I-P0 / IMPLEMENTATION | Knowledge Service | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Ingestion provenance and idempotent publication | OPEN |
| GAP-R2-004 | Q026, Q027, Q028, Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036 | I-P0 / IMPLEMENTATION | Knowledge Service | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Conditional retrieval and citation lineage | OPEN |
| GAP-R2-005 | Q037, Q038, Q039, Q040, Q041, Q042 | I-P0 / IMPLEMENTATION | Agent Runtime Service | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Model Provider and Gateway replaceability | OPEN |
| GAP-R2-006 | Q043, Q044, Q045, Q046, Q047, Q048, Q049, Q050 | I-P0 / IMPLEMENTATION | Memory Policy Owner | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Memory Policy and provider boundary | OPEN |
| GAP-R2-007 | Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q059, Q060, Q061, Q062, Q063, Q064 | I-P0 / IMPLEMENTATION | Agent Runtime Service | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for PlanVersion, DAG, reflection and runtime recovery | OPEN |
| GAP-R2-008 | Q065, Q066, Q067, Q068, Q069, Q070 | I-P0 / IMPLEMENTATION | Legal Capability Contract Owner | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Capability Contract and legal provider governance | OPEN |
| GAP-R2-009 | Q071, Q072, Q073, Q074, Q075, Q076, Q077, Q078, Q079, Q080, Q081, Q082, Q083, Q084, Q085, Q086, Q087, Q088 | I/X-P0 / IMPLEMENTATION+EXTERNAL | Tool / Sandbox Owner | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Tool Effect, Approval and Security enforcement | OPEN |
| GAP-R2-010 | Q089, Q090, Q091, Q092, Q093, Q094 | E-P0 / MEASUREMENT | Eval / Observability | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Legal Eval, attribution and release gates | OPEN |
| GAP-R2-011 | Q095, Q096, Q097, Q098, Q099, Q100 | I-P0 / IMPLEMENTATION | Service Architecture / Infrastructure | Target contract only; no automatic Current promotion | Focused contract, failure, security or benchmark evidence for Service, Queue, Storage and Deployment evidence | OPEN |

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/architecture-deltas.md`

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

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/round-report.md`

# RB-WORKFLOW-V3-ROUND-002 Report

## Result

- BASE_SHA: 19ba6e050e1334f71c511a5968c9ea9d15c68111
- FINAL_SHA: recorded in final handoff
- Workflow: ZUNO-RED-BLUE-WORKFLOW-V3
- Questions Generated: 100
- Answers Completed: 100
- Scores Completed: 100
- Decisions Completed: 100
- Raw Score: 371/500
- Normalized Score: 74.20/100
- Grade: Architecture Requires Significant Repair
- Round Status: COMPLETE
- Round-003: READY_NOT_STARTED

## Gate counts

- New A-P0: 0
- Original P0 closed: 0/12
- Closure classes: A=0, I=5, E=3, X=0 in this Round; prior I/E/X P0 remain open.
- AUTO_APPLY Deltas: 11
- ADR Escalation: 0
- User Gate Escalation: 0

## Components

- KEEP: legal Domain State, Evidence semantics, Single Controller, Plan/DAG, Review, Security and Eval floors.
- REFINE: version barriers, citation provenance, Memory/Provider policy, Tool Receipt, Queue and service boundary evidence.
- EXTERNALIZE: concrete Model Gateway, OpenViking, Graph and other providers when replacement tests pass.
- DELETE: no core capability deleted; accidental provider lock-in remains deleted from Target assumptions.

## Current / Target / Facts

Facts changed: NONE.

Runtime, UI, Schema, Migration, Production Infra and Dependencies changed: NONE.

Only Target Contract clarifications/refinements were synchronized. No implementation, measurement or
production status was promoted.

## Validation

Passed before closure:

- `git diff --check`
- `python tools/scripts/verify_red_blue_round_v3.py`
- `python tools/scripts/verify_red_blue_score_v3.py`
- `python tools/scripts/verify_canonical_diff_v3.py`
- architecture document set, architecture render, docs entrypoint/link/writing/readability verifiers
- Agent System and document boundary verifiers
- `pytest -q tests/repo/test_red_blue_round_v3.py -p no:cacheprovider` (`3 passed`)

Full CI was not run; this Round does not claim `CI PASS` or Production Readiness.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/canonical-sync-record.md`

# Round-002 Canonical Sync Record

Status: APPLIED
Canonical Before SHA: 19ba6e050e1334f71c511a5968c9ea9d15c68111
Canonical After SHA: recorded in final handoff
Round: RB-WORKFLOW-V3-ROUND-002

## Sync rule

Only AUTO_APPLY refinements were synchronized. No Python-only, Microservice, Single Controller,
Domain-vs-Runtime State or Security Trust Boundary principle changed. No Current, Measured,
Production or Historical Fact was promoted.

## Delta mapping

| Delta | Source Questions | Canonical Files | Mode |
|---|---|---|---|
| D001 | Q001, Q002, Q003, Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012 | docs/project/architecture/architecture.md; docs/project/domain/domain-state-lifecycle.md | AUTO_APPLY |
| D002 | Q013, Q014, Q015, Q016, Q017, Q018 | docs/project/product/product-architecture.md; docs/project/domain/legal-domain-model.md | AUTO_APPLY |
| D003 | Q019, Q020, Q021, Q022, Q023, Q024, Q025 | docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/data/data-ownership-and-recovery.md | AUTO_APPLY |
| D004 | Q026, Q027, Q028, Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036 | docs/project/knowledge/knowledge-evidence-architecture.md; docs/project/eval/legal-eval-and-benchmark.md | AUTO_APPLY |
| D005 | Q037, Q038, Q039, Q040, Q041, Q042 | docs/project/agents/agent-platform.md; docs/project/services/service-architecture.md | AUTO_APPLY |
| D006 | Q043, Q044, Q045, Q046, Q047, Q048, Q049, Q050 | docs/project/agents/agent-platform.md; docs/project/data/data-ownership-and-recovery.md | AUTO_APPLY |
| D007 | Q051, Q052, Q053, Q054, Q055, Q056, Q057, Q058, Q059, Q060, Q061, Q062, Q063, Q064 | docs/project/agents/agent-platform.md; docs/project/domain/domain-state-lifecycle.md | AUTO_APPLY |
| D008 | Q065, Q066, Q067, Q068, Q069, Q070 | docs/project/agents/agent-platform.md; docs/project/domain/legal-domain-model.md | AUTO_APPLY |
| D009 | Q071, Q072, Q073, Q074, Q075, Q076, Q077, Q078, Q079, Q080, Q081, Q082, Q083, Q084, Q085, Q086, Q087, Q088 | docs/project/security/security-architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md | AUTO_APPLY |
| D010 | Q089, Q090, Q091, Q092, Q093, Q094 | docs/project/eval/legal-eval-and-benchmark.md | AUTO_APPLY |
| D011 | Q095, Q096, Q097, Q098, Q099, Q100 | docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/data/data-ownership-and-recovery.md; docs/project/deployment/microservice-deployment.md | AUTO_APPLY |

## Verification obligations

Every changed file is linked to at least one Delta; every Delta has a canonical file; the V3 verifier recomputes this relation. Implementation and evidence gaps remain open.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/canonical-snapshot.md`

# Round-002 Canonical Snapshot

BASE_SHA: 19ba6e050e1334f71c511a5968c9ea9d15c68111
Snapshot status: ACCEPTED_TARGET
Snapshot rule: Round-002 attacks current Canonical docs, not old Lab candidates.

## Sources

- docs/project/architecture/
- docs/project/product/
- docs/project/domain/
- docs/project/agents/
- docs/project/knowledge/
- docs/project/services/
- docs/project/data/
- docs/project/security/
- docs/project/eval/
- docs/project/deployment/
- docs/governance/architecture-gate-policy.md
- docs/status/production-readiness.md

## Frozen constraints

Python-only Target, Microservice Deployment Target, Domain Owner of Canonical State, Runtime/Domain
State separation, Single Controller, Provider Proposal boundary, Security/Approval/Evidence gates.

## Attackable candidates

Service count, Graph, Memory Provider, Model Gateway, LangGraph, Tool/Sandbox physical boundary,
Database/Queue/Storage providers, Multi-Agent profiles and all unmeasured quality or efficiency claims.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/adr-escalations.md`

# Round-002 ADR / User Escalations

```yaml
adr_escalations: 0
user_gate_escalations: 0
new_a_p0: 0
status: NONE
```

No decision changed Python-only, Microservice Target, Single Controller, Domain/Runtime ownership,
Provider Proposal boundary or Security Trust Boundary. Existing ADR-0008 through ADR-0011 remain
sufficient. Model Gateway, Graph, Memory Provider, Tool Runtime and service count remain replaceable
or evidence-gated candidates.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V3-ROUND-002/11-plus-1-coverage-map.md`

# Round-002 11+1 Coverage Snapshot

Source: `project-reconstruction-lab/05-red-blue/11-plus-1-canonical-coverage-map.md`

All 12 lenses are represented in the manifest and questions. Canonical Owner mapping is unchanged; Round deltas may refine documents but cannot create a second Owner.
