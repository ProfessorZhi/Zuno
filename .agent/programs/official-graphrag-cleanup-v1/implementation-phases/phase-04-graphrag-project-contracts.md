# Phase 04: GraphRAG Project Contracts

## Goal

Introduce the core GraphRAG Project contract so later phases can load settings,
prompts, index versions, and query methods against a stable type boundary.

## Why This Phase Exists

Zuno has graph index fields and Domain Pack fields, but not a first-class
GraphRAG Project contract.

## Required Reading

- Phase 03 evidence package
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `.agent/architecture/near-term/09-persistence-database-storage.md`

## Scope

Types, DTOs, schemas, config objects, and tests that express GraphRAG Project
identity and metadata.

## Non-goals

- full settings loader
- prompt tuning implementation
- index rebuild implementation
- runtime deletion

## Candidate Files

- `src/backend/zuno/schema/knowledge.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/services/graphrag/models.py`
- `src/backend/zuno/services/retrieval/models.py`
- `apps/web/src/apis/knowledge.ts`
- `tests/test_product_wiring_v1_api_contract.py`
- new `tests/test_graphrag_project_contracts.py`

## Execution Order

1. Add tests for `graphrag_project_id`, `settings_path`, `prompt_version`,
   `index_version`, `query_method`, `query_prompt_version`,
   `community_version`, `document_hash`, `chunk_hash`, and `status`.
2. Add minimal schema/DTO types.
3. Thread project metadata through contract objects without full runtime load.
4. Update docs with the exact contract surface.
5. Run targeted tests.

## Acceptance Criteria

- Contract layer can represent a GraphRAG Project.
- Target fields have explicit defaults or validation rules.
- Existing runtime still works.
- No full loader is claimed complete.

## Implemented Contract Surface

Phase 04 adds the contract surface only. It does not load a project directory or
run prompt tuning.

Fields:

- `graphrag_project_id`
- `settings_path`
- `prompt_version`
- `index_version`
- `query_method`
- `query_prompt_version`
- `community_version`
- `document_hash`
- `chunk_hash`
- `status`

Contract paths:

- `src/backend/zuno/services/graphrag/models.py`
- `src/backend/zuno/schema/knowledge.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/services/retrieval/models.py`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `tests/test_graphrag_project_contracts.py`

## Verification Commands

```powershell
pytest -q tests/test_graphrag_project_contracts.py
pytest -q tests/test_product_wiring_v1_api_contract.py
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
git add src/backend/zuno apps/web tests docs .agent
git commit -m "feat: add graphrag project contracts"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Contract work requires database migration before schema is agreed.
- Existing knowledge config tests fail in a way that needs contract redesign.

## Evidence Package Required

- contract field list
- DTO/schema paths
- tests proving old runtime still passes
- commit hash and push result

## Risks

- Creating fields that are not used later.
- Confusing Knowledge Base ownership with GraphRAG Project ownership.

## Follow-up Phase

Phase 05: GraphRAG Project Loader / Settings.
