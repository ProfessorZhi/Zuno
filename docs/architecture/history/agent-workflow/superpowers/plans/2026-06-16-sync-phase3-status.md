# Sync Phase 3 Status Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update the architecture phase docs so the repo's current engineering track is Phase 3: Domain Pack Formalization.

**Architecture:** Keep runtime and product code unchanged. Only update phase-status documentation and any verifier/test expectations that read phase-state wording, then run the required doc and structure validations.

**Tech Stack:** Markdown docs, Python verification scripts, pytest

---

### Task 1: Update current phase index

**Files:**
- Modify: `docs/architecture/phases/README.md`

- [ ] **Step 1: Change the current phase pointer**

Set the current phase from `Phase 2` to `Phase 3: Domain Pack Formalization`.

- [ ] **Step 2: Expand the phase status block**

Make the status block explicitly state:
- `Phase 0` complete
- `Phase 1` complete
- `Phase 2` complete
- `Phase 2.5` complete
- `Phase 3` active engineering track

### Task 2: Update phase-specific status docs

**Files:**
- Modify: `docs/architecture/phases/phase-02-graphrag-mainline-deepening.md`
- Modify: `docs/architecture/phases/phase-03-domain-pack-formalization.md`

- [ ] **Step 1: Close Phase 2**

Mark `phase-02` as closed/completed while preserving its goal, focus, and closure gate.

- [ ] **Step 2: Mark Phase 3 active**

Add an explicit active status to `phase-03` so it matches the new current track.

### Task 3: Verify doc and structure entrypoints

**Files:**
- Verify only

- [ ] **Step 1: Run docs entrypoint verifier**

Run: `python tools/scripts/verify_docs_entrypoints.py`

Expected: `documentation entrypoint verification passed.`

- [ ] **Step 2: Run repo structure verifier**

Run: `python tools/scripts/verify_repo_structure.py`

Expected: `Repository structure verification passed.`

- [ ] **Step 3: Run required tests**

Run: `pytest -q tests/test_docs_entrypoints.py tests/test_graphrag_architecture_positioning.py tests/test_repo_structure_consistency.py`

Expected: all tests pass.
