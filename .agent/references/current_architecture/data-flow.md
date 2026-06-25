# Data Flow

This is a documentation-level flow, not a claim about uninspected code internals.

## Documentation Truth Flow

```text
formal decision
  -> docs/architecture/
  -> .agent/programs/ when it is active work
  -> docs/architecture/history/ when superseded
```

## Agent Workflow Flow

```text
task request
  -> AGENTS.md entry rules
  -> .agent/references for navigation
  -> .agent/templates for repeatable prompts
  -> .agent/scripts for read-only checks
  -> verification evidence in final response or docs
```

## Runtime Orientation Flow

The current documented runtime orientation remains:

```text
apps/web or apps/desktop
  -> src/backend/zuno
  -> retrieval and GraphRAG runtime surfaces
  -> tests and eval evidence
```

Do not add lower-level runtime details here unless they are verified from code.
