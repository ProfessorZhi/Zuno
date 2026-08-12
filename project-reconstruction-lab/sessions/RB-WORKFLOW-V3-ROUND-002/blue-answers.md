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
