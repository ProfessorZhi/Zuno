# Skills Map

## Purpose

Record repository-local Agent skill routing.

## Current Paths

- `.agent/skills/zuno-read-only-audit/SKILL.md`
- `.agent/skills/zuno-docs-maintenance/SKILL.md`
- `.agent/skills/zuno-repo-hygiene/SKILL.md`
- `.agent/skills/zuno-frontend-change/SKILL.md`
- `.agent/skills/zuno-backend-change/SKILL.md`
- `.agent/skills/zuno-api-contract-change/SKILL.md`
- `.agent/skills/zuno-architecture-refactor/SKILL.md`
- `.agent/skills/zuno-eval-change/SKILL.md`

## Rule

These are thin routing entries. The workflow remains the source of execution
steps. Do not duplicate workflow text inside skills.

## Automatic Discovery

Do not assume repository-level automatic skill discovery unless the current
Codex environment explicitly confirms it. If discovery is not confirmed, use
`AGENTS.md` to route Agents to these files manually.

Runtime product skills under `src/backend/zuno/system_skills/` are application
assets, not repository maintenance workflow skills.
