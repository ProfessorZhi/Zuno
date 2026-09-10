# Findings — rb-2026-09-10-architecture-part-a-007

Round result: `PASS_WITH_ONE_NARRATIVE_GAP`  
Highest severity: `MEDIUM`

## F1 — Overall Architecture does not fully derive Application & Integration before the nine-domain summary

**Type:** `NARRATIVE_GAP`  
**Severity:** `MEDIUM`  
**Status:** `OPEN_AT_ROUND_CLOSE`

### Finding

`docs/architecture/architecture.md` now derives Knowledge, Capability, Domain, Runtime, Model Gateway, Effects, Security, and Observability / Evaluation from concrete constraints or failure windows before the nine-domain table. `01 Application & Integration` is weaker in the global running case.

The Architecture starts with an application service and mentions that a WorkProduct may later be delivered, but it does not explicitly walk the product-lifecycle failure that the 01 module itself explains well: one external task can be accepted, have computation finish, later become formally admitted, then be delivered, and later become stale after new evidence. A single product `success` cannot safely stand for all of those observations.

As a result, a reader who only follows the overall Architecture can explain why most long-term responsibility domains exist but needs to jump into `docs/modules/application/README.md` to explain why Application is an independent logical responsibility rather than a thin HTTP adapter.

### Decision impact

This does **not** justify changing the nine-domain decomposition, Authority, Contracts, or recovery semantics. It changes the Architecture Part A narrative order: the global running case should expose the external product-lifecycle tension before claiming that all nine responsibility domains have naturally appeared.

### Source support

- `docs/architecture/architecture.md` — running case before `这些反复出现的冲突才形成九个责任域`
- `docs/modules/application/README.md` — `同一个“完成”会在一项任务里发生好几次`
- `docs/modules/application/reference.md` remains the exact Engineering Reference and does not need a semantic change.

### Evidence needed

No new implementation evidence is required. This is a documentation narrative repair. Existing Architecture document-set semantic alignment must remain green.

### Bounded repair

Add one short product-lifecycle scene to the overall running case before the nine-domain summary. It should show an external Host observing accepted → draft/computation finished → formal result → delivered → later stale, and explain why Application composes Owner facts without owning Domain or Effect truth.

Do not introduce new states, Receipts, services, or Architecture objects.

### Retest scenario

Use a different surface from the original wording: an external court Host polls a task immediately after Runtime completion while professional admission is still pending; later the formal result is delivered, then new evidence invalidates it while the Host is offline. Ask who can truthfully answer each external status and whether Application becomes a new global truth owner.
