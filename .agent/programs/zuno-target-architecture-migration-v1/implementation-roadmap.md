# Zuno Target Architecture Migration V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move Zuno from the current Phase 11A/11B state to the near-term target architecture and repository layout.

**Architecture:** Keep the current Python/FastAPI modular monolith, finish GraphRAG Project migration, remove Domain Pack from the active path, then add Context/Memory and Capability boundaries around the single `GeneralAgent`. Historical and superseded plans stay in `docs/architecture/history/`; executable Agent work stays in `.agent/programs/`.

**Tech Stack:** Python, FastAPI, LangGraph, Vue, GraphRAG/RAG services, pytest, `.agent` workflow verifiers.

---

## Program Gate

Do not start implementation phases until Phase 00 proves current state from
Git, code, tests, and grep. Do not remove any Blocked Legacy surface until the
phase that owns it proves active dependency removal.

## Phase Overview

| Phase | Status | Main Output |
| --- | --- | --- |
| 00 | complete | current-state and dependency gate |
| 01 | in progress / blocked | official cleanup 11C dependency removal |
| 02 | asset-only migration complete / formal closure blocked by 01 and remaining migration compatibility evidence | Contract Review asset migration |
| 03 | safe prework started / full closure blocked by 01-02 | GraphRAG Project mainline hardening |
| 04 | safe prework started / full closure blocked by 01-03 | repository layout cleanup |
| 05 | blocked by 04 | Context contract foundation |
| 06 | blocked by 05 | Memory layer foundation |
| 07 | blocked by 05-06 | Capability System |
| 08 | blocked by 05-07 | single GeneralAgent runtime integration |
| 09 | final | full tests, eval, trace, docs, and grep closure |

## Execution Rules

- [ ] Run the phase gate before editing phase files or runtime code.
- [ ] Keep one active phase at a time unless independent read-only audits are
  explicitly requested.
- [ ] Write failing tests before implementation changes.
- [ ] Commit after each verified phase.
- [ ] Push only after required verification passes.

## Phase Dependencies

```text
00
  -> 01 -> 02 -> 03 -> 04
  -> 05 -> 06 -> 07 -> 08 -> 09
```

Phase 01 continues `official-graphrag-cleanup-v1` 11C/12 work. Phases 05-08
replace the archived `context-memory-agent-runtime-v1` candidate path.

## Required Global Verifiers

```powershell
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
git diff --check
```

Phase 09 adds full `pytest -q` and formal Eval baseline comparison.
