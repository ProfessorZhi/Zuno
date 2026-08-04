# PHASE22 Nonbackend Legacy and Cutover Surface Cleanup

## Phase / Branch

- Phase: PHASE22
- Task: P22-T03 (Nonbackend Worker Branch)
- Worker: `claude/minimax-phase22-nonbackend-legacy-cleanup`
- Base: `origin/main` @ `83c1bbd0`
- Base branch for PR: `main`

This evidence directory records the surface audit for nonbackend (Web, Desktop,
Tools, Infra, Workflow, Governance) legacy/cutover residue. Backend Runtime,
Migration, Agent Core, Security, Benchmark thresholds and Dataset files are
explicitly out of scope and untouched.

## Scope (allowed paths)

```
apps/web/**
apps/desktop/**
tools/**
infra/**
.github/workflows/**
tests/frontend/**
tests/repo/**
.agent/programs/work-products/feature-flag-registry.yaml
.agent/programs/work-products/temporary-allowlist.yaml
.agent/programs/work-products/legacy-bypass-inventory.yaml
.agent/programs/work-products/phase22-removal-candidates.yaml
docs/evidence/goal05-phase22-nonbackend-legacy-cleanup/**
```

## Scope (forbidden)

```
src/backend/zuno/**                 # Runtime
infra/db/alembic/**                 # Migration
agents/**                           # Agent Core
security/**                         # Security
benchmarks/** thresholds            # Benchmark
datasets/**                         # Formal datasets
```

PR #119 evidence is also off limits.

## Classification taxonomy

Every hit must receive exactly one classification:

| Tag                          | Definition                                                             |
| ---------------------------- | ---------------------------------------------------------------------- |
| ACTIVE_NONBACKEND_BLOCKER    | Real runtime reader exists outside this worker's scope                |
| EXPIRED_CONFIG_RESIDUE       | Mechnical 1:1 replacement available                                    |
| ALLOWED_HISTORY_REFERENCE    | Kept on purpose to preserve legacy URL/DTO/form semantics              |
| ALLOWED_FAIL_CLOSED_TEST     | Fail-closed guard or rollback-mode coverage (e.g. Product Runtime)     |
| ALLOWED_VERSIONED_PUBLIC_API | Versioned public API that does not own domain facts                    |
| UNRESOLVED                   | Cannot resolve in this branch (escalate / deepen / leave untouched)    |

Worker policy: never delete by keyword.

## Manifest files

- `web_findings.md` — Web app findings
- `desktop_findings.md` — Desktop findings
- `tools_infra_findings.md` — Tools / Infra / Workflow findings
- `feature_flag_classification.md` — Feature flag registry classification
- `allowlist_classification.md` — Allowlist / bypass inventory classification
- `escalations.md` — DeepSeek escalations
- `sha_manifest.txt` — SHA-256 of evidence files
- `lockfile.txt` — Per-file SHA-256 of canonical inputs we read

## Out-of-scope deliverables

`docs/evidence/goal05-phase22-cleanup-start.md` and the rest of the
`docs/evidence/goal05-phase22-*` evidence are owned by previous worker
branches and PR #119. They are NOT modified by this worker.
