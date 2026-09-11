# Round 011 — Architecture Proof-Obligation Stress Test

Base: `1229b34064f6290a9a2fe9e27c9b902a189d9b9b`

Blue starts from `docs/architecture/architecture.md`; Engineering Reference and module docs are used only when exact ownership or completion-proof semantics must be checked.

## Turn 1 — Cancel after Domain commit, before Runtime checkpoint

**Red**

A professional reviewer completes Formal Admission. The Domain transaction commits, but Runtime crashes before its next Checkpoint. While the run is restarting, the user presses Cancel. Is the system allowed to treat cancellation as rollback and make the admitted WorkProduct disappear?

**Blue**

No. The Domain commit is already a durable business fact. Recovery must query the Domain completion proof, repair Runtime control state, and let cancellation stop only future work that can still be stopped safely. The already admitted WorkProduct remains historical truth; if it should no longer be current, that requires a new Domain decision such as invalidation/supersession, not deletion of the prior admission.

**Red verdict**

`NARRATIVE_GAP` at the overall Part A level. The answer is explicit in the cross-module Engineering Reference (`Cancellation 不是全局 rollback`) and is consistent with Part A's Domain/Checkpoint recovery story, but the Human Architecture does not yet state the general irreversible-boundary rule that makes this answer obvious without descending into Reference.

## Turn 2 — Replan after an external effect already occurred

**Red**

Plan P7 sends an external filing. The remote system accepts it. A new DocumentVersion arrives one second later and Runtime activates P8. Can the P7 branch now be discarded as stale together with the effect it caused?

**Blue**

No. Plan staleness affects whether a computation remains eligible for future acceptance; it cannot negate external reality. Once the effect may have happened, the system has crossed the effect boundary. P8 may decide that a new action, reconciliation, invalidation or compensation is needed, but the original Effect remains part of history.

**Red verdict**

PASS. Part A already distinguishes late-result eligibility from external reality and states that local recovery cannot rewind the outside world.

## Turn 3 — WorkProduct delivered, then later invalidated

**Red**

WorkProduct V5 was formally admitted and delivered to a Host. New evidence later makes V5 stale. Should Zuno overwrite V5, retract the Delivery fact, or mark the previous Tool/Delivery receipt as rolled back?

**Blue**

None of those. Domain owns the new invalidation/current-validity fact; Application owns invalidation delivery and consumer acknowledgement observations. If the external world needs an actual withdrawal or corrective action, that is a new controlled Effect with its own authorization and outcome. V5's historical admission and prior delivery stay true.

**Red verdict**

PASS. The current Part A already allows historical admission, delivery, current security denial and later staleness to coexist without a global status. Exact compensation ownership is correctly left to 01/06/08 references.

## Turn 4 — Failed Knowledge rebuild versus last-good serving truth

**Red**

Generation G7 is serving. G8 starts rebuilding. BM25 writes complete, vector build fails, and the build is marked failed. Is failure itself allowed to replace G7 as the current serving generation?

**Blue**

No in the Target Architecture. A failed or incomplete generation is a historical build attempt, not stronger serving truth. Only a fully validated generation can replace the last-good serving state. If Current code violates that property, it is an implementation defect, not a reason to weaken the architecture.

**Red verdict**

PASS at Architecture level. Part A already states that a new generation must be fully validated before it replaces current serving. The known Current generation-isolation defect belongs in Evidence / implementation review.

## Turn 5 — Security allow becomes deny

**Red**

At 10:00 a user lawfully reads Attachment A. At 10:12 SecurityEpoch changes and future access is denied. Does the new deny mean the 10:00 read was never authorized?

**Blue**

No. Security eligibility is time-sensitive. The old authorized access remains part of historical execution; the new decision governs future protected actions. A later deny can revoke future eligibility without rewriting the truth of an earlier lawful action.

**Red verdict**

PASS. The current Part A explicitly says lawful history remains while future protected operations consume current authorization facts.

## Turn 6 — What proof allows a state to become stronger?

**Red**

Suppose several subsystems each expose an easy local success: retriever found text, model returned JSON, Runtime marked a step done, HTTP returned 200, and a queue ACKed. Can the system promote any of those to formal business completion, confirmed external effect, or current eligibility just because all of them look successful?

**Blue**

No. Each stronger claim needs evidence owned by the corresponding Authority. Formal business completion requires the Domain's matching completion proof and still-valid causation; external-effect completion requires Effect truth or conclusive reconciliation; current authorization requires current Security facts; Knowledge serving requires validated generation/serving proof. Absence of the stronger proof leaves the state weaker even when nearby components report success.

**Red verdict**

PASS. The Part A now states that fact strength rises only when the required evidence exists; the consistency section also requires stable identity, version, causation refs and queryable completion proof across Owner boundaries.

## Round conclusion

Five of six scenarios are already reconstructable from the overall Human Architecture or are correctly owner-local. One cross-cutting rule remains implicit rather than explicit: after crossing a durable business or real-world side-effect boundary, later control decisions cannot erase the historical fact. That rule should be promoted into Part A without introducing a new object or global state machine.
