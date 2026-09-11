# Round 012 — Irreversibility Alternate-Scenario Retest

Base: `04c40dbb0e16dc3576473110e3c6f3c5d83ea77e`

This retest starts from the repaired Human Architecture and deliberately changes timing and actors from Round 011.

## Turn 1 — Formal Admission committed, response lost, then cancellation arrives

**Red**

Domain commits a WorkProduct and its matching completion proof. The caller loses the response and Runtime has not yet recorded the next control projection. During restart, the user cancels the task. Which fact wins: the newer cancellation request or the already committed admission?

**Blue**

The two facts answer different questions. The committed admission proves what already became formal business history. Cancellation governs future work that can still be stopped. Restart first queries the Domain completion proof and repairs Runtime; cancellation can then prevent additional work, publication or later actions when their own rules allow it, but it cannot erase the admitted WorkProduct.

**Verdict**

PASS. The repaired Part A explicitly says that after Formal Admission, Cancel cannot make the AdmissionReceipt/WorkProduct disappear and that current eligibility/control can change without rewriting history.

## Turn 2 — Old Plan effect succeeds after a new Plan is active

**Red**

Plan P17 sends an external action. Before the response returns, new evidence causes P18 to become active. The remote system then confirms that P17's action succeeded. Runtime now considers P17 stale. Can the new plan discard that Effect because its originating branch is no longer current?

**Blue**

No. Plan validity is a control/eligibility question; external Effect truth is historical reality. Once the action crossed the send boundary and may have occurred, the stale branch cannot negate it. The system records/reconciles the Effect and lets P18 decide whether any follow-up, invalidation or new compensating action is needed.

**Verdict**

PASS. The new irreversibility section explicitly separates pre-boundary Replan from post-boundary Reconcile/new Effect/Compensation.

## Turn 3 — Delivered result becomes unusable and must be withdrawn externally

**Red**

WorkProduct V8 was admitted and delivered to an external consumer. Later, new Evidence makes V8 stale and a Security decision forbids future use. The business now wants a real withdrawal notice sent to the consumer. Can Zuno mark the original Delivery or Effect receipt as rolled back so the history looks clean?

**Blue**

No. Admission, prior Delivery and any confirmed external Effect remain historical facts. Domain records the new invalidation/current-validity fact; Security governs future protected actions. If reality must be changed again, the withdrawal is a new controlled external action with its own authorization, identity, Attempt and outcome. Its success does not mutate the old receipt into “never happened.”

**Verdict**

PASS. The repaired Part A directly states that post-boundary correction is represented by invalidation/supersession, Reconcile, or a new controlled Effect/Compensation rather than hidden rollback.

## Retest conclusion

All three alternate scenarios preserve the same invariant without adding a global rollback protocol, Event Sourcing requirement, or new architecture object:

- historical Domain/Effect facts remain true once their authority boundary has been crossed;
- current eligibility, visibility and future permission may change;
- corrective real-world change is represented by a new fact/action rather than mutation of old history.

Round 011 F1 is resolved. No new decision-impact Architecture or Narrative finding was produced.
