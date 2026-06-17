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
7. [Phase 6: Agent GraphRAG Pluginization / Future Platform Layer](phase-06-agent-graphrag-pluginization.md)

## Current Execution Rule

The migration-pause closure program is already complete.

The current rule is:

- treat `Phase 0-6` as completed closure truth
- keep future work aligned with the same runtime truth and documentation layering
- if a new architecture round starts, open it as a fresh phase program instead of reviving retired service-migration steps

Phase status:

1. `Phase 0` is complete
2. `Phase 1` is complete
3. `Phase 2` is complete
4. `Phase 2.5` is complete
5. the user has personally tried the recovered runtime
6. `Phase 3` is complete
7. `Phase 4` is complete
8. `Phase 5` is complete
9. `Phase 6` is complete

## Current Track Notes

- `Phase 4` now explicitly carries two linked subtracks:
  - `Knowledge Config V2`
  - `Local Eval Strengthening`
- `Phase 5` is the public explanation sync layer.
- `Phase 6` is the platform boundary layer for `Agent GraphRAG Pluginization`.
- `Community GraphRAG` remains a later layer, not the current default retrieval mainline.
- `DRIFT-like Search` remains a future slot, not a committed runtime feature.

Relative path hints:

- `../history/README.md`

## Historical Rule

Older phase files from the paused service-migration-first program have been downgraded to:

- [Architecture History](../history/README.md)
