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
5. [Phase 4: Local Eval Strengthening](phase-04-local-eval-strengthening.md)
6. [Phase 5: Docs And Public Explanation Sync](phase-05-docs-and-public-explanation-sync.md)

## Current Execution Rule

Only one phase should be current at a time.

Right now the entry phase is:

- [Phase 0: Stable Runtime Recovery](phase-00-stable-runtime-recovery.md)

Do not begin Phase 1 until:

1. the runtime baseline is stable again
2. focused startup and import checks pass
3. the user has personally tried the recovered runtime

## Historical Rule

Older phase files from the paused service-migration-first program have been downgraded to:

- [Architecture History](05_TopDown_题库学习/项目/02_项目映射/Zuno/docs/architecture/history/README.md)
