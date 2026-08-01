# Programming Agent Performance Ledger

Status: governance bootstrap

This directory defines the auditable performance ledger for programming-agent pull requests.

## Ownership

- Programming Agent owns execution facts: shell, provider, model, timing, tokens, cost, commits, tests, CI, Git operations, limitations, and scope deviations.
- ChatGPT owns review facts: reviewed head SHA, decision, severity counts, dimension scores, strengths, required changes, and task-fit recommendations.
- GitHub owns remote facts: PR state, head SHA, commit count, diff statistics, CI result, merged time, and merge commit SHA.

When self-reported facts conflict with GitHub, GitHub is authoritative and the mismatch is recorded under `reporting_truthfulness`.

## Record model

Each PR uses one unique record file:

```text
docs/governance/agent-performance/records/pr-NNNN.json
```

Parallel PRs must not edit another PR's record. Shared Markdown and CSV ledgers are maintained by ChatGPT during reconciliation/finalization to avoid merge conflicts.

Required top-level keys:

```json
{
  "schema_version": 1,
  "pr_number": 57,
  "pr_url": "https://github.com/ProfessorZhi/Zuno/pull/57",
  "work_package": "...",
  "agent": {
    "shell": "Claude Code",
    "provider": "MiniMax",
    "visible_model": "MiniMax-M3",
    "actual_model": "not reported",
    "reasoning_effort": "not reported",
    "permission_mode": "bypassPermissions",
    "usage_source": "CLI"
  },
  "git": {
    "base_branch": "...",
    "base_sha": "...",
    "initial_head_sha": "...",
    "current_head_sha": "...",
    "final_approved_head_sha": null,
    "reset_used": false,
    "rebase_used": false,
    "force_push_used": false
  },
  "rounds": [],
  "reviews": [],
  "aggregate": {
    "implementation_rounds": 0,
    "repair_rounds": 0,
    "total_wall_clock_seconds": null,
    "total_tokens": null,
    "provider_reported_cost": null,
    "current_score": null,
    "final_score": null
  },
  "status": "SUBMITTED_FOR_REVIEW",
  "merge": {
    "merged_at": null,
    "merge_commit_sha": null
  }
}
```

Unknown numeric telemetry is `null`; unknown text telemetry is `"not reported"`. Values must never be estimated.

## Review decisions

Allowed review decisions:

- `REQUEST_CHANGES`
- `BOUNDARY_ACCEPTED_NOT_MERGE_READY`
- `MERGE_APPROVED`

Allowed lifecycle statuses:

- `SUBMITTED_FOR_REVIEW`
- `REPAIR_IN_PROGRESS`
- `BOUNDARY_ACCEPTED_NOT_MERGE_READY`
- `MERGE_APPROVED`
- `MERGED`
- `CLOSED_UNMERGED`
- `SUPERSEDED`

An Agent may copy a ChatGPT review block into its record only verbatim. It may not change scores, severity counts, decisions, or reviewed SHA.

## Merge safety

A PR may be merged only after an exact `MERGE_APPROVED` decision is bound to the full current Head SHA. Any later commit invalidates that approval.

Default merge method is merge commit. Squash, rebase merge, admin merge, reset, rebase, and force push are prohibited unless a later explicit governance decision says otherwise.

## Commit attribution

Claude Code is represented in commit trailers as:

```text
Agent: Claude-Code
Agent-Mode: Standard
```

Provider and model are recorded separately in the PR record and PR body. A Claude Code session must not claim to be Codex, Antigravity, Human, or another harness.
