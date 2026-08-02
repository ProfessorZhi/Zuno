# Goal05 PHASE22 Commit Attribution Blocked Contract

status: BLOCKED_GOVERNANCE_CONTRACT
phase: PHASE22
parent_pr: 97

## Frozen Facts

- PHASE22 = in_progress
- Program = active
- Fixed Benchmark = BLOCKED / blocked_not_measured
- actual_case_count = 0
- reviewer_approved_count = 0
- benchmark_eligible_count = 0
- Production Readiness = not established

## Contract

`tools/scripts/verify_agent_commit_attribution.py` enforces the
`Agent / Agent-Mode / Human-Owner / Architecture-Reviewer / Work-Package`
trailer set on every non-merge, non-bot commit reachable from the
integration branch tip.

## Why This Is BLOCKED (not bypassed)

- The integration branch `codex/phase22-final-closure` was created at
  2026-08-02 and contains 15 commits ahead of `main` @ `dfb99819…`.
- 14 of those 15 commits were authored under the previous attribution
  contract (Agent / Provider / Role / Parent-PR / Metrics-Run) and lack
  the four newly required trailers.
- The spec for this round explicitly forbids:
  - `amend`, `rebase`, `reset`, `force push`
  - Lowering, bypassing or deleting the verifier
  - Rewriting history
- The verifier reports the historical commits as missing trailers. This is
  the correct, real behaviour.

## Resolution Path (No Fake)

New commits on the integration branch from this round onward must include
all 5 trailers:

```text
Agent: Claude-Code
Provider: MiniMax
Model: MiniMax-M3
Agent-Mode: Codex
Human-Owner: ProfessorZhi
Architecture-Reviewer: ChatGPT
Work-Package: PHASE22-PR97-REVIEW-FIX
Parent-PR: #97
Metrics-Run: <真实RUN_ID或NOT_AVAILABLE_INTERACTIVE_SESSION>
```

The integration branch tip after this round will be a new commit that
satisfies the contract. The historical commits remain BLOCKED.

A clean state requires one of:

1. Squashing or rebasing the integration branch — **forbidden** by this
   round's contract.
2. Resetting the integration branch to `main` and re-applying only the
   work that meets the new contract — this would discard prior
   context; not taken in this round.
3. A governance change that admits historical commits under
   `BLOCKED_GOVERNANCE_CONTRACT` until the integration branch is
   squashed at merge time — proposed, not enacted.

## Verifier Status

```text
$ python tools/scripts/verify_agent_commit_attribution.py --base origin/main --allow-human-only
Agent Commit Attribution Verification Failed:
  - Commit 6a340068 missing required trailers: ['Agent-Mode', 'Human-Owner', 'Architecture-Reviewer', 'Work-Package']
  - Commit 13486bf9 missing required trailers: ['Agent-Mode', 'Human-Owner', 'Architecture-Reviewer', 'Work-Package']
  - ... (10 more historical commits)
  - Commit 757cfe4c has invalid Agent: 'Claude Code'. Allowed: [..., 'Claude-Code', ...]
  - Commit 757cfe4c has invalid Agent-Mode: 'implementation'. Allowed: [..., 'Codex', 'Standard', ...]
```

## Conflict Between Spec Trailer Format and Verifier Allowlist

This round's spec prescribes new commit trailers as:

```text
Agent: Claude Code           (with space)
Agent-Mode: implementation   (literal "implementation")
```

The verifier's allowlist is:

```text
ALLOWED_AGENTS = {"Antigravity", "Qoder", "Codex", "Claude-Code", "Trae", "ChatGPT-Docs", "Human"}
ALLOWED_MODES  = {"Standard-Conversation", "Expert-Team", "Codex", "Standard", "Docs-Maintenance", "Human", "Goal"}
```

The spec's values `Agent: Claude Code` and `Agent-Mode: implementation`
are **not** in the verifier's allowlist. Adding new commits with the
spec's exact values therefore extends the failure list rather than
fixing it. The controller cannot resolve this conflict from within
this round's contract (no amend, rebase, reset, force-push, or
verifier mutation).

A new commit at the integration branch tip has been added that uses
the spec's exact format. The verifier flags it too, but the commit
is on record as a faithful attempt to follow the round's spec. The
verifier cannot pass until either:

1. The verifier's allowlist is updated to include the spec's values,
   OR
2. The spec is reconciled with the verifier's existing allowlist.

This is recorded as `BLOCKED_GOVERNANCE_CONTRACT` (verifier/spec
mismatch). The integration branch remains Draft.

## Boundary

This evidence does not claim PHASE22 completed, fixed benchmark measured,
release gate passed, production ready, archive or no-active reset. It
records an honest governance blocker, not a fake pass.