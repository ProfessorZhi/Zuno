# Architecture Upgrade Phases

This directory is the current phase program for the repo after the migration pause.

Use it to answer:

- what the current phase order is
- what each phase is trying to solve
- what must be verified before moving on

Do not use this directory for long-term architecture theory.
That belongs in `../specs/`.

## Current Phase Order

1. [Phase 0: Stable Runtime Recovery](phase-00-stable-runtime-recovery.md)
2. [Phase 1: LangGraph Runtime Deepening](phase-01-langgraph-runtime-deepening.md)
3. [Phase 2: GraphRAG Mainline Deepening](phase-02-graphrag-mainline-deepening.md)
4. [Phase 3: Domain Pack Formalization](phase-03-domain-pack-formalization.md)
5. [Phase 4: Knowledge Config V2 + Local Eval Strengthening](phase-04-local-eval-strengthening.md)
6. [Phase 5: Docs And Public Explanation Sync](phase-05-docs-and-public-explanation-sync.md)
7. Phase 6: Agent GraphRAG Pluginization / Future Platform Layer

## Current Execution Rule

Only one phase should be current at a time.

Right now the current phase is:

- [Phase 3: Domain Pack Formalization](phase-03-domain-pack-formalization.md)

Phase status:

1. `Phase 0` is complete
2. `Phase 1` is complete
3. `Phase 2` is complete
4. `Phase 2.5` is complete
5. the user has personally tried the recovered runtime
6. `Phase 3` is the active engineering track

## Current Track Notes

- `Phase 4` now explicitly carries two linked subtracks:
  - `Knowledge Config V2`
  - `Local Eval Strengthening`
- `Phase 6` is a future platform layer for `Agent GraphRAG Pluginization`.
- `Community GraphRAG` remains a later layer, not the current default retrieval mainline.

Relative path hints:

- `../history/README.md`

## Historical Rule

Older phase files from the paused service-migration-first program have been downgraded to:

- [Architecture History](../history/README.md)
