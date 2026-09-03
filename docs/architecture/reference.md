# Overall Architecture Machine Reference

status: canonical-architecture-machine-router
owner: Cross-cutting Architecture Owner
human_source: docs/architecture/architecture.md#part-a--human-narrative人类技术叙事
engineering_source: docs/architecture/architecture.md#part-b--engineering--agent-reference机器--工程参考
module_router: docs/modules/reference.md
decision_source: docs/decisions/
evidence_source: docs/evidence/

## Read order for implementation

1. Read `architecture.md` Part B for cross-cutting Authority and recovery invariants.
2. Read `modules/reference.md` to locate the current Target responsibility owner.
3. Read the selected Module Part B / Part C.
4. Read relevant ADRs.
5. Read Evidence before claiming anything is Current.
6. Only then inspect code, schema, migrations and tests.

## Cross-cutting facts that belong here

- responsibility / Authority registry;
- canonical fact ownership;
- cross-domain contract direction;
- completion-proof matrix;
- version / freshness rules;
- Retry / Replan / Reconcile semantics;
- cancellation and late-result rules;
- security authority boundaries;
- external-effect outcome semantics;
- persistence and recovery order;
- deployment constraints that change semantic boundaries;
- Current / Target / History / Unknown source precedence.

## Non-goals

Do not duplicate module-local fields, enums, full state machines, API schemas or migration plans here. Do not infer Current from Target. Do not treat current module count as a Documentation Architecture invariant.
