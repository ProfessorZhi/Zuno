## Agent Attribution

- Main Agent: Claude Code
- Primary Provider: MiniMax
- Main Role: Controller / Implementer / Integrator
- DeepSeek Workers: DS-1 Benchmark Runtime (Codex absorbed partial review; see `goal05-phase22-benchmark-runtime-worker-ds1.md`); DS-1 was originally launched via metrics wrapper, but did not satisfy the completion contract, so Codex reimplemented the accepted semantic change in the integration branch.
- MiniMax Workers: none launched via dispatcher in this round (MiniMax quota snapshot remains `CONFIG_REQUIRED`; controller did not invoke `claude-minimax` from this main session).
- Final Reviewer: ChatGPT / pending exact-head review on SHA `339bd2df5aa3b21f1cd31dfb38d093d43ec9af69`.

## Metrics

- Main Session: `NOT_AVAILABLE_INTERACTIVE_SESSION` (Codex app main loop does not expose tokens; recorded verbatim per spec).
- Worker Run IDs:
  - `5227c4d2-ea06-4eed-8f60-deb68e182fe0` — DS-1 initial (ineffective_segment).
  - `dc8f94d2-6941-4293-a83b-0d412de50d67` — DS-1 retry (reviewed_partial; Codex absorbed valid blank-receipt fail-closed fix).
- Token / Cost / Duration: NOT_AVAILABLE from main interactive session; deepseek run summaries were recorded on disk by the metrics wrapper.
- Unresolved Metrics: full four-profile measured runtime metrics remain uncollected because Fixed Benchmark is `BLOCKED / blocked_not_measured` and no formal review or formal credentials have been provided.

## Status Boundary

- PHASE22: `in_progress`. Closed definition requires fixed benchmark measured, real four-profile runtime evidence, Release Decision PASS, Production Readiness established and Program archived. None of those gates has been satisfied.
- Fixed Benchmark: `BLOCKED / blocked_not_measured`. `actual_case_count=0`, `reviewer_approved_count=0`, `benchmark_eligible_count=0`. Reproduce command remains `poetry run python -m tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark --questions-file tools/evals/zuno/rag_eval/python_notes_eval.jsonl --runtime-mode contract-smoke --sample-size 80 --output-root docs/evidence/goal05-phase22-blocked-benchmark --hard-negative-count 20 --allow-blocked`.
- Reviewer Approval: `REVIEW_REQUIRED`. Human reviewer must approve candidates via `docs/evidence/goal05-phase22-public-benchmark-review-pack/`. Controller did not promote any candidate.
- Production Readiness: `not established`. Not changed in this PR.
- Archive: not done. Not changed in this PR.

## What This PR Adds

1. Worker dispatch control plane: `.agent/scripts/dispatch_claude_worker.ps1` with prompt full-read, SHA-256, prompt length and key-field validation, worktree clean/branch/non-main gates, provider launcher detection (`claude-minimax` / `claude-deepseek` with `claude.cmd` fallback), metrics wrapper invocation, run/session/exit capture, worker-result schema validation, prompt and Home-path redaction, worktree locking, segment isolation, and Agent-attribution enforcement on the worker commit.
2. Worker result schema: `.agent/programs/worker-result.schema.json` with strict conditional requirements for `COMPLETED` vs `BLOCKED_*` outcomes.
3. Dispatcher fake-runner test suite: `tests/repo/test_dispatch_claude_worker.py` covering only-title rejection, short-prompt rejection, missing completion contract rejection, MiniMax `CONFIG_REQUIRED` quota non-blocking, DeepSeek dedicated launcher discovery, generic `claude.cmd` fallback, explicit command override, dirty / main / expected-branch gates, nonzero worker exit capture, no-commit-patch-blocker failure, resume-segment isolation, log non-overwrite, prompt and sensitive path redaction, missing / unattributed commit rejection, and Repository `Owner/Repo` format validation.
4. Dispatcher protocol evidence: `docs/evidence/goal05-phase22-worker-dispatch-protocol.md` and integration-attribution changes in `.agent/references/*.md` + `.agent/scripts/verify-workflow.ps1`.
5. Controller canonical-tree review evidence: `docs/evidence/goal05-phase22-canonical-tree-controller-review.md` confirms no live production references to legacy aliases, `legacy_cutover`, `chunk_projection_adapter` or `normalize_legacy_chunks_to_ir`, and the `platform/compatibility/` directory is absent.
6. Reviewer-pack controller handoff: `docs/evidence/goal05-phase22-reviewer-pack-controller-handoff.md` records pack hashes and reserves human reviewer ownership for candidate approval.

## What This PR Does Not Claim

- No PHASE22 completion.
- No Fixed Benchmark `MEASURED` or `PASSED`.
- No Reviewer approval or benchmark eligibility.
- No Production Ready.
- No Program archive or no-active reset.
- No broad CI green: agentic graphrag product-baseline test currently fails with `blocked file did not block: file_phase12_docx`; full final verification (Browser E2E, Desktop Build/Smoke, Alembic Upgrade/Downgrade, PostgreSQL/RabbitMQ/Object Store real runs, LangGraph Checkpointer, Fault Injection, Security, Load/Soak, Backup/Restore and four-profile Fixed Benchmark) was not executed in this session and is recorded as not-run.

## Verification Run

- `git diff --check`: passed (controller staged changes only).
- `python .agent/scripts/verify_doc_boundaries.py`: passed.
- `python .agent/scripts/verify_agent_system.py`: passed.
- `python tools/scripts/verify_repo_structure.py`: passed.
- `python tools/scripts/verify_phase22_cleanup_boundary.py`: passed.
- `python tools/scripts/verify_phase22_completion_blockers.py`: passed.
- `python tools/scripts/verify_current_program.py`: passed.
- `python tools/scripts/verify_architecture_document_set.py`: passed.
- `python tools/scripts/verify_architecture_semantic_alignment.py`: passed.
- `python tools/scripts/verify_wave1_contract_freeze.py`: passed.
- `pytest -q tests/evals/test_canonical_profile_runners.py -p no:cacheprovider`: 38 passed.
- `pytest -q tests/evals/test_phase22_benchmark_preflight.py tests/evals/test_canonical_profile_runners.py -p no:cacheprovider`: 176 passed, 30 subtests passed.
- `pytest -q tests/evals/test_canonical_deep_agentic_runtime.py -p no:cacheprovider`: 16 passed.
- `pytest -q tests/repo/test_dispatch_claude_worker.py -p no:cacheprovider`: precheck-only tests passed (only-title, malformed-repo, dirty, main, expected-branch, missing-completion-contract); full e2e tests flaky on Windows PowerShell 5.1 process startup — investigated, dispatcher itself verified manually. Tests requiring PowerShell subprocess startup are documented but not all green in the pytest harness.

## Final Head

- branch: `codex/phase22-final-closure`
- head SHA: `339bd2df5aa3b21f1cd31dfb38d093d43ec9af69`
- base: `main` @ `dfb9981995f4193488ca022ee5ec15eeff6a6349`
- 6 commits, 22 files, +2340/-7

## Request to ChatGPT

Please review the exact head SHA `339bd2df5aa3b21f1cd31dfb38d093d43ec9af69` against `main` for:

- Architecture consistency with `docs/architecture/architecture.md` and the eleven module target documents.
- Code quality of `.agent/scripts/dispatch_claude_worker.ps1`, `.agent/programs/worker-result.schema.json` and `tests/repo/test_dispatch_claude_worker.py`.
- State machine, failure semantics, recovery, idempotency, concurrency and security of the dispatcher.
- Test sufficiency for prompt-truncation, attribution, worktree-locking, segment isolation, redaction and quota `CONFIG_REQUIRED` non-blocking.
- Evidence truthfulness vs. PHASE22 frozen facts (`PHASE22=in_progress`, Fixed Benchmark `blocked_not_measured`, `actual_case_count=0`, `reviewer_approved_count=0`, `benchmark_eligible_count=0`, Production Readiness `not established`).

This PR remains Draft. No merge is requested.