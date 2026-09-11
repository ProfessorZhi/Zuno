# Findings — Round 011

## F1 — Overall Architecture does not yet state the irreversible-boundary rule

- Type: `NARRATIVE_GAP`
- Severity: `MEDIUM`
- Decision impact: overall architecture understanding
- Architecture / Authority change: **NO**
- New object / state / service required: **NO**

### What the current design already knows

The exact semantics are already present across Engineering Reference and module design:

- cancellation stops future work; it is not a global rollback;
- a committed Domain fact does not disappear because Runtime later cancels or replans;
- a confirmed or possibly-real external Effect cannot be denied by a stale branch;
- compensation is a new controlled action rather than mutation of the old receipt;
- invalidation/supersession changes current validity without rewriting historical admission;
- Security revocation changes future eligibility without making earlier authorized activity retroactively unauthorized;
- an incomplete Knowledge generation cannot become serving merely because work started.

### Why this is still an overall narrative gap

`architecture.md` contains the individual failure stories, and the new thesis sections correctly separate historical truth from current validity. A reader can infer the rule, but the document never states the common boundary that determines which recovery vocabulary applies.

That omission matters because the distinction explains several otherwise separate mechanisms at once:

```text
before durable authority / real-world boundary
→ recompute / retry / reject / replan may still be enough

after durable Domain admission
→ preserve history; later change is version / invalidation / supersession

after possible or confirmed external effect
→ preserve external reality; later change is reconcile / new effect / compensation
```

Without that rule, Cancel, Replan, Invalidation and Compensation can still look like unrelated module features rather than consequences of one system property.

### Bounded repair

Add one short Human Architecture section that explains:

1. some work remains safely replaceable before it crosses a durable authority or external-effect boundary;
2. crossing Formal Admission or an Effect send/confirmation boundary creates history that later workflow control cannot erase;
3. current eligibility can be revoked even while the historical fact remains true;
4. post-boundary correction is expressed as new version, invalidation, reconciliation or compensation rather than destructive rollback;
5. this does **not** require a global event-sourcing model, a new `IrreversibilityReceipt`, or another state machine.

### Explicit non-findings

The round did **not** find a new Architecture Gap in:

- transition proof ownership — already covered by owner completion proofs and the evidence-strength thesis;
- Security history/current eligibility — already explained in Part A;
- Knowledge last-good serving semantics — already Target-correct, with Current defect tracked separately;
- post-delivery invalidation ownership — already split among Domain, Application and Effects;
- effect compensation semantics — exact contract correctly remains in module reference.
