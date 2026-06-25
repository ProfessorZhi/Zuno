# Task Closure Workflow

## Trigger

Use before ending any modification task.

## Steps

1. Run the smallest meaningful verification.
2. Run `git diff --check`.
3. Review `git status --short`.
4. Commit and push modification tasks unless verification or push is blocked.
5. Report verification commands, commit hashes, push result, and remaining
   blockers.

## Rule

Do not claim completion without fresh verification evidence.
