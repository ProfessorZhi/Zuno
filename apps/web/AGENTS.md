# Zuno Web Agent Rules

Before changing `apps/web`, read:

1. `.agent/references/frontend-map.md`
2. `.agent/references/api-contract-map.md`
3. `.agent/workflows/frontend-change.md`

For frontend/API contract migration or repository layout work, also read
`.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`.

Rules:

- API field changes must sync backend DTOs, frontend types, and contract tests.
- Visual, interaction, and page-layout changes must first produce an isolated
  preview under `.agent/local/previews/<task-id>/`.
- Provide desktop and needed mobile screenshots for user confirmation.
- Do not implement visual prototypes into production pages before user
  confirmation.
- Run lint, build, and affected tests after changes.
- Do not expose internal routes, old GraphRAG names, or migration-only fields in
  user-facing UI.
