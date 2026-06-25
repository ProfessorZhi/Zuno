# Phase 6: Agent GraphRAG Pluginization / Future Platform Layer

## Goal

Define the platform boundary for how an Agent binds Domain Pack, retrieval profile, Local GraphRAG capability, and eval profile without turning the repo into a full multi-agent production system.

## Focus

- Agent runtime can resolve Domain Pack from agent-side binding when knowledge runtime does not already provide one
- retrieval profile is a typed runtime concept, not only an implicit internal knob
- GraphRAG is described as an Agent platform capability, not a contract-review-only hardcoded feature
- Domain Pack can declare future-facing defaults for retrieval and eval alignment
- Community GraphRAG and DRIFT-like Search stay documented as future slots only

## Closure Gate

- one Agent can bind Domain Pack, retrieval profile, Local GraphRAG capability, and eval profile through runtime-facing configuration
- knowledge defaults, agent defaults, and domain-pack defaults have an explicit precedence story
- no `services/` or `services/api` route is reintroduced
- no full Community GraphRAG or DRIFT-like runtime is implemented under this phase
