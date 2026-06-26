# Phase 05: GraphRAG Project Loader / Settings

## Goal

Implement the GraphRAG Project loader and settings validation boundary.

## Why This Phase Exists

The target project layout needs `settings.yaml`, `prompts/`, readiness checks,
and clear validation errors before indexing or routing can depend on it.

## Required Reading

- Phase 04 evidence package
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `docs/history/specs/enterprise-retrieval-governance.md`

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
- `examples/graphrag-projects/contract_review/` as the current project fixture
- `docs/history/domain-packs/root-contract-review/` as archived
  migration evidence only
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

## Implemented Loader Boundary

Phase 05 adds a loader boundary only. Retrieval, indexing, prompt tuning, and
frontend migration are still later phases.

Loader API:

- `GraphRAGProjectLoader(projects_root=None).load(project_id)`
- `GraphRAGSettingsValidator.parse_settings(text, settings_path=...)`
- `GraphRAGSettingsValidator.validate_contract(payload, project_id=..., settings_path=...)`
- `GraphRAGSettingsValidator.prompt_manifest(payload)`
- `KnowledgeService.describe_graphrag_project_readiness(config, projects_root=None)`

Loaded project metadata:

- `base_path`
- `contract`
- `settings`
- `prompt_paths`
- `prompt_texts`
- `readiness`

Validator/readiness error examples:

- `settings.yaml not found: <project_id>`
- `query_method` validation errors
- `missing prompt: <prompt_name>`

Fixture policy:

- Unit tests create temporary GraphRAG Project directories with `settings.yaml`
  and `prompts/`.
- Current Contract Review fixture coverage uses
  `examples/graphrag-projects/contract_review/`.
- Archived root Domain Pack assets remain migration evidence only under
  `docs/history/domain-packs/root-contract-review/`; do not
  restore `domain-packs/` as a current root directory.

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
- GraphRAG Project fixtures cannot be validated without either current project
  assets or archived migration evidence.

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
