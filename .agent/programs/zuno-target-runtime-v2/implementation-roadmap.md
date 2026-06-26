# Zuno Target Runtime V2 Implementation Roadmap

## Objective

Implement the first controlled slice after the completed target architecture
migration closure.

Success for this round means:

- a new active executable Agent program exists.
- low-risk backend boundary migration starts without a broad package move.
- module boundary gates prevent known regressions.
- a minimal Context Orchestrator is callable and tested.
- the Single `GeneralAgent` and GraphRAG Project mainline do not regress.

## Phase List

| Phase | Status | Purpose |
| --- | --- | --- |
| 00 | Complete | Re-verify current state before writing. |
| 01 | Active | Open this executable program and update pointers. |
| 02 | Planned | Audit module boundaries and add migration gates. |
| 03 | Planned | Move the first low-risk backend boundary. |
| 04 | Planned | Add minimal Context Orchestrator runtime. |
| 05 | Future | Mature Memory Engine. |
| 06 | Future | Mature Capability Selector. |
| 07 | Future | Explicit `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime. |
| 08 | Future | Frontend feature boundaries. |
| 09 | Future | Tests, eval, trace, and closure evidence. |

## Guardrails

- Do not move whole packages at once.
- Do not rewrite `GeneralAgent.astream()` streaming behavior.
- Do not add database schema or dependency changes.
- Do not restore `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`,
  root `domain-packs/`, or Domain Pack frontend pages.
- Do not make `domain_pack_id` an active public target field.

## Evidence

Phase evidence belongs under this program's `evidence/` directory or in each
phase document. Local machine artifacts from a run must stay outside the repo
or in ignored local paths.
