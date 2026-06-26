# Read-Only Audit Workflow

## Trigger

Use when scope is unclear, when a deletion or move might be risky, or when the
user asks for reconnaissance.

## Steps

1. Read `AGENTS.md`.
2. Read formal docs relevant to the task.
3. Read `.agent/references/README.md`, `.agent/references/code-map.md`, and
   the relevant navigation map.
4. Run read-only discovery with `rg`, `git status --short`, and targeted path
   reads.
5. Classify findings as Current, Target, Future, History, Generated, Local,
   Dead, or Blocked.
6. Return evidence and recommended next action.

## Stop Conditions

- A requested deletion still has active imports or tests.
- A file is unique evidence or user-authored material.
- Docs and code conflict and evidence is insufficient.

## Verification

Read-only audits do not commit or push.
