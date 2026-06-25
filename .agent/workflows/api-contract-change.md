# API Contract Change Workflow

## Trigger

Use for DTO, request/response, frontend type, or public API field changes.

## Steps

1. Identify backend DTO, frontend type, API client, route, and tests.
2. Confirm whether the field is Current, Target, or migration-only.
3. Change both sides of the contract together.
4. Keep old GraphRAG and Domain Pack names out of public target contracts unless
   explicitly migration-only.

## Verification

Run affected backend, frontend, and contract tests.
