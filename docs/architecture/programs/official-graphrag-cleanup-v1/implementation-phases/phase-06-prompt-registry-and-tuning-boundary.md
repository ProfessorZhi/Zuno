# Phase 06: Prompt Registry And Tuning Boundary

## Goal

Define and implement the Prompt Registry and indexing-side Prompt Tuning
boundary.

## Why This Phase Exists

Prompt Tuning controls graph extraction, summarization, and community report
generation. It is not the same as ordinary answer-template text.

## Required Reading

- Phase 05 evidence package
- `.agent/architecture/near-term/11-graphrag-project-architecture.md`
- `.agent/architecture/near-term/12-enhanced-mode-pipeline.md`

## Scope

Prompt registry, prompt version metadata, indexing-side prompt categories, and
rebuild impact rules.

## Non-goals

- automatic prompt optimization
- frontend prompt editor
- full graph rebuild implementation

## Candidate Files

- `src/backend/zuno/prompts/`
- new `src/backend/zuno/services/graphrag/prompts/`
- `src/backend/zuno/services/graphrag/extractor.py`
- `src/backend/zuno/services/graphrag/community/service.py`
- `tests/test_hardening01_config_impact_contract.py`
- new `tests/test_graphrag_prompt_registry.py`

## Execution Order

1. Add tests for prompt categories: `extract_graph`, `summarize`,
   `community_report`, `local_query`, `global_query`, and `drift_query`.
2. Add prompt version metadata and registry lookup.
3. Encode rebuild impact rules: extraction/chunking/schema prompts can require
   rebuild; query prompts usually do not.
4. Update project settings docs.
5. Run config impact tests.

## Acceptance Criteria

- `prompt_version` is recordable and testable.
- Indexing-side prompts are separate from answer templates.
- Prompt changes have explicit rebuild impact.
- Tests prove query prompt changes do not automatically rebuild graph.

## Verification Commands

```powershell
pytest -q tests/test_graphrag_prompt_registry.py
pytest -q tests/test_hardening01_config_impact_contract.py
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
git commit -m "feat: define graphrag prompt registry"
git push
```

Forbidden: force push, force-with-lease, amend, unrelated files, or success
claims after failed validation.

## Stop Conditions

- Prompt categories cannot be separated from Domain Pack templates.
- Rebuild impact cannot be represented without Phase 07 versioning decisions.

## Evidence Package Required

- prompt category table
- rebuild impact examples
- test outputs
- commit hash and push result

## Risks

- Treating Prompt Tuning as answer-prompt customization.
- Rebuilding graph for harmless query prompt changes.

## Follow-up Phase

Phase 07: Index / Update / Versioning.
