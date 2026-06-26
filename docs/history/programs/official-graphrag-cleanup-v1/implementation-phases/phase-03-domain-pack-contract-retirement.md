# Phase 03: Domain Pack Contract Retirement

## Goal

Retire Domain Pack from public contracts and DTOs first, before deleting runtime
implementation paths.

## Why This Phase Exists

The frontend and API still expose `domain_pack_id`, `/domain-packs`, and
Domain Pack UI flows. Contract migration must precede runtime deletion.

## Required Reading

- Phase 01 inventory
- Phase 02 updated current docs
- `.agent/architecture/near-term/13-frontend-api-contract.md`
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`

## Scope

Public API contracts, DTOs, frontend API types, compatibility window, and tests
for contract behavior.

## Non-goals

- deleting `src/backend/zuno/services/domain_pack/`
- deleting `domain-packs/`
- graph runtime rewrite
- long-term Domain Pack shim

## Later Status

This Phase 03 non-goal is historical. The
`src/backend/zuno/services/domain_pack/` runtime service package was retired
during later Phase 11C dependency-removal work. Root `domain-packs/` assets
were later archived under
`docs/history/domain-packs/root-contract-review/`, and Docker no
longer copies or mounts `/app/domain-packs`.

## Candidate Files

- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/schema/knowledge.py`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `tests/test_product_wiring_v1_api_contract.py`
- `tests/test_knowledge_api_contract.py`

## Execution Order

1. Add failing contract tests for target public fields.
2. Introduce `graphrag_project_id` and target project fields at the contract
   edge.
3. Accept `domain_pack_id` only as a migration input where explicitly tested.
4. Stop exposing Domain Pack as the preferred public field.
5. Update docs and frontend API types.
6. Run contract and docs tests.

## Acceptance Criteria

- Public contract prefers `graphrag_project_id`.
- Domain Pack fields are migration-only and not the mainline.
- Compatibility reads are bounded and documented.
- Tests prove target field names and reject accidental long-term shim behavior.

## Verification Commands

```powershell
pytest -q tests/test_product_wiring_v1_api_contract.py
pytest -q tests/test_knowledge_api_contract.py
python tools\scripts\verify_docs_entrypoints.py
git diff --check
git grep -n "domain_pack_id"
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
git commit -m "refactor: retire domain pack public contract"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Active imports require broad runtime deletion in the same phase instead of
  bounded contract retirement.
- Frontend cannot preserve Standard/Enhanced UX without broader runtime work.
- Contract tests cannot express a bounded compatibility window.

## Evidence Package Required

- public field diff summary
- compatibility read list
- grep classification for `domain_pack_id`
- test outputs
- commit hash and push result

## Risks

- Breaking existing saved knowledge configs.
- Replacing names without preserving runtime semantics.

## Follow-up Phase

Phase 04: GraphRAG Project Contracts.
