# Docs Freeze Target Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze the documentation target mode so future code refactors follow `src/backend/zuno`, clean entry links, and the current GraphRAG phase model.

**Architecture:** Tighten the architecture entry docs and GraphRAG spec without touching backend code. Extend documentation tests first so legacy target paths, abnormal long links, and default-mainline confusion fail before any doc edits.

**Tech Stack:** Markdown, pytest, lightweight docs verification script

---

### Task 1: Lock failing docs expectations

**Files:**
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\tests\test_graphrag_architecture_positioning.py`
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\tests\test_docs_entrypoints.py`
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\tools\scripts\verify_docs_entrypoints.py`

- [ ] Step 1: Add failing assertions for `src/backend/zuno`, clean relative links, and non-default Community GraphRAG wording
- [ ] Step 2: Run docs tests and verify they fail for the expected legacy phrases
- [ ] Step 3: Update the verifier script to track the same entrypoint expectations

### Task 2: Freeze architecture and phase docs

**Files:**
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\docs\architecture\README.md`
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\docs\architecture\phases\README.md`
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\docs\architecture\specs\domain-pack-langgraph-graphrag-architecture.md`

- [ ] Step 1: Replace legacy `src/backend/zuno/` target-path wording with `src/backend/zuno/`
- [ ] Step 2: Replace abnormal long local links with clean relative links in the architecture entry docs
- [ ] Step 3: Clarify how `Knowledge Config V2` and `Agent GraphRAG Pluginization` fit the current phase model without changing backend code

### Task 3: Verify and publish

**Files:**
- Modify: `F:\internship-work\resume&resume project\02_projects\Zuno\README.md` if entrypoint verification requires alignment

- [ ] Step 1: Run `pytest .\tests\test_graphrag_architecture_positioning.py .\tests\test_docs_entrypoints.py -q`
- [ ] Step 2: Run `python tools/scripts/verify_docs_entrypoints.py`
- [ ] Step 3: Review `git diff` for docs-only scope, then commit and push
