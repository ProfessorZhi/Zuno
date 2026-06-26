# Phase 10: Frontend API Contract Migration

## Goal

Migrate frontend API and product contract to GraphRAG Project and public query
methods while keeping Standard and Enhanced Mode simple.

## Why This Phase Exists

Frontend currently exposes Domain Pack pages, `domain_pack_id`,
`rag_graph_deep`, and graph capability names in API/config utilities.

## Required Reading

- Phase 03 and Phase 09 evidence packages
- `.agent/architecture/near-term/13-frontend-api-contract.md`
- `.agent/architecture/near-term/12-enhanced-mode-pipeline.md`

## Scope

Frontend API types, config utilities, settings pages, advanced query method
controls, trace display, and contract tests.

## Non-goals

- backend router redesign
- deleting runtime Domain Pack paths
- large visual redesign unrelated to contract migration

## Candidate Files

- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `apps/web/src/utils/retrieval.ts`
- `apps/web/src/pages/knowledge/`
- `apps/web/src/pages/workspace/components/WorkspaceSettingsShell.vue`
- `apps/web/src/router/index.ts`
- `tests/test_frontend_model_page.py`
- `tests/test_frontend_workspace_features.py`
- `tests/test_product_wiring_v1_api_contract.py`

## Execution Order

1. Added tests that frontend payloads use `graphrag_project_id`,
   `graphrag_project.query_method`, prompt/index versions, and trace contract
   fields.
2. Removed old runtime route names from `apps/web`.
3. Preserved Standard and Enhanced Mode product language.
4. Kept advanced `auto/basic/local/global/drift` methods in the API/type
   contract rather than adding a broad UI redesign.
5. Exposed requested/resolved method, retrievers, evidence bundle, citation
   coverage, and pipeline trace in frontend API types without old internal
   names.

## Implemented Frontend Contract

Enhanced product configs now write:

```json
{
  "index_capability": "rag_graph",
  "graphrag_project_id": "contract_review",
  "domain_pack_id": null,
  "graphrag_project": {
    "graphrag_project_id": "contract_review",
    "query_method": "auto",
    "prompt_version": "default",
    "index_version": "v1"
  },
  "retrieval_settings": {
    "default_mode": "rag_graph"
  }
}
```

`rag_graph_deep`, `local_graphrag`, `community_global`, and `drift_like` no
longer appear under `apps/web`.

## Trace Type Contract

`apps/web/src/apis/knowledge.ts` accepts retrieval `query_method` and types
metadata for:

- `requested_query_method`
- `resolved_query_method`
- `query_method_fallback_reason`
- `retrievers_used`
- `evidence_bundle`
- `citation_coverage`
- `pipeline_trace`

## Acceptance Criteria

- UI does not display old internal terms.
- API payloads do not use Domain Pack as the mainline.
- Trace shows requested and resolved query method.
- Frontend tests or equivalent route checks pass.

Status: satisfied for frontend API/types/config utilities and page-level
contract tests. Domain Pack pages and runtime compatibility paths remain for
Phase 11 deletion/classification.

## Verification Commands

```powershell
pytest -q tests/test_frontend_model_page.py
pytest -q tests/test_frontend_workspace_features.py
pytest -q tests/test_product_wiring_v1_api_contract.py
git grep -n "rag_graph_deep" -- apps/web
git grep -n "local_graphrag" -- apps/web
git grep -n "community_global" -- apps/web
git grep -n "drift_like" -- apps/web
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
git add apps/web tests docs .agent
git commit -m "refactor: migrate frontend graphrag contract"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Backend contract is not stable enough for frontend migration.
- Old terms are still required in user-facing labels.
- UI changes require unrelated design work.

## Evidence Package Required

- frontend payload examples
- user-facing term grep summary
- route/test outputs
- commit hash and push result

## Risks

- Breaking saved workspace settings.
- Hiding advanced methods too early or exposing them with unclear status.

## Follow-up Phase

Phase 11: Runtime Legacy Deletion.
