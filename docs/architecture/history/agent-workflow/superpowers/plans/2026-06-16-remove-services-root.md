# Remove Services Root Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the root-level `services/` placeholder so the repo no longer presents any active or reserved services root in current truth.

**Architecture:** Keep `src/backend/zuno` as the only backend runtime truth, delete the `services/` directory itself, and rewrite front-path docs plus repo verifiers so future root-level services extraction is described only as a potential new architecture phase. Do not change GraphRAG, Domain Pack, or LangGraph runtime logic.

**Tech Stack:** Markdown docs, Python verification scripts, pytest

---

### Task 1: Remove front-path `services/` placeholder language

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture/current-architecture.md`
- Modify: `docs/architecture/transition-strategy.md`
- Modify: `docs/development/backend-layering-guidelines.md`

- [ ] **Step 1: Replace repository-layout and architecture wording**

Remove any claim that the repo still has a root-level `services/` placeholder or reserved future boundary in current structure. Replace it with wording that the repo has no active services root now, and any future root-level services tree would require a new architecture phase.

- [ ] **Step 2: Keep runtime-truth wording aligned**

Ensure the four files all reinforce the same rule: `src/backend/zuno` is the only backend runtime truth, and the old root-level services direction is fully retired.

### Task 2: Remove structure-verifier assumptions about `services/`

**Files:**
- Modify: `tools/scripts/verify_repo_structure.py`
- Modify: `tests/test_repo_structure_consistency.py`

- [ ] **Step 1: Remove required-path checks for `services/`**

Delete any required-path assertion that still expects the root-level `services/` directory to exist.

- [ ] **Step 2: Update required phrases**

Replace `services/`-related README phrase checks with wording that proves the repo no longer exposes an active services root.

### Task 3: Remove the physical directory and related boundary assertions

**Files:**
- Delete: `services/README.md`
- Delete: `services/`
- Modify: `tests/test_phase25_legacy_boundary_hardening.py`

- [ ] **Step 1: Remove the remaining placeholder files**

Delete `services/README.md` and the `services/` directory tree itself so no root-level services shell remains.

- [ ] **Step 2: Tighten retirement assertions**

Update the Phase 2.5 boundary test so it asserts that `services/` itself is absent in current truth, not just `services/api`.

### Task 4: Verify the new repo truth

**Files:**
- Verify only

- [ ] **Step 1: Run structure verifier**

Run: `python tools/scripts/verify_repo_structure.py`

Expected: `Repository structure verification passed.`

- [ ] **Step 2: Run required regression suite**

Run: `pytest -q tests/test_repo_structure_consistency.py tests/test_phase0_runtime_recovery.py tests/test_phase1_langgraph_runtime_deepening.py tests/test_phase2_graphrag_mainline_deepening.py tests/test_phase25_legacy_boundary_hardening.py`

Expected: all tests pass.
