# Phase 05: GraphRAG Project Loader / Settings

## Goal

Implement the GraphRAG Project loader and settings validation boundary.

## Why This Phase Exists

The target project layout needs `settings.yaml`, `prompts/`, readiness checks,
and clear validation errors before indexing or routing can depend on it.

## Required Reading

- Phase 04 evidence package
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `docs/architecture/specs/enterprise-retrieval-governance.md`

## Scope

Project loading, settings validation, prompt discovery, readiness state, and
unit tests.

## Non-goals

- prompt tuning logic
- full indexing
- frontend UI migration
- runtime legacy deletion

## Candidate Files

- new `src/backend/zuno/services/graphrag/project/`
- `src/backend/zuno/services/graphrag/models.py`
- `src/backend/zuno/api/services/knowledge.py`
- `domain-packs/contract_review/` as migration evidence only
- new `tests/test_graphrag_project_loader.py`

## Execution Order

1. Add failing tests for loading a project directory with `settings.yaml`.
2. Add tests for missing settings, invalid query method, missing prompts, and
   not-ready project state.
3. Implement `GraphRAGProjectLoader` and `GraphRAGSettingsValidator`.
4. Expose project readiness metadata without changing retrieval behavior.
5. Update docs with project layout and error contract.

## Acceptance Criteria

- Loader can load project settings.
- Validator gives explicit errors.
- Prompt files are discoverable.
- Readiness state is inspectable.
- Runtime behavior is not overclaimed.

## Verification Commands

```powershell
pytest -q tests/test_graphrag_project_loader.py
python tools\scripts\verify_docs_entrypoints.py
git diff --check
```

## GitHub Sync Requirements

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add src/backend/zuno tests docs .agent
git commit -m "feat: add graphrag project loader"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Loader cannot be added without deciding storage tables.
- Existing Domain Pack assets are the only available project fixture.

## Evidence Package Required

- loader API summary
- validator error examples
- fixture path
- test outputs
- commit hash and push result

## Risks

- Treating Domain Pack manifests as permanent GraphRAG Project settings.
- Hiding invalid project state behind fallback defaults.

## Follow-up Phase

Phase 06: Prompt Registry And Tuning Boundary.
