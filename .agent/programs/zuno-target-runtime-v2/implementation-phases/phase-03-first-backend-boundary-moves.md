# Phase 03 First Backend Boundary Moves

## Goal

Move one low-risk backend use-case service toward the target application
boundary.

## Preferred Move

```text
src/backend/zuno/api/services/knowledge_query.py
-> src/backend/zuno/services/application/knowledge/query_service.py
```

## Rules

- Prefer updating all imports and tests over adding a shim.
- If a compatibility re-export is temporarily required, document its deletion
  phase and guard it with the module boundary verifier.
- Do not move whole packages.
- Do not change retrieval behavior.

## Verification

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py -p no:cacheprovider
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py -p no:cacheprovider
python .agent/scripts/verify_module_boundaries.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
git diff --check
```
