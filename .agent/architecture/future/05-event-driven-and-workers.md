# Event Driven And Workers

## Future Direction

Event-driven workflows and independent workers may matter for indexing,
GraphRAG updates, prompt tuning, evaluation, report export, and long-running
tool jobs.

## Possible Shape

```text
FastAPI service
  -> enqueue job or publish event
  -> indexing worker / GraphRAG worker / eval worker
  -> status table and trace updates
  -> frontend polling or server event updates
```

## Readiness Conditions

- durable task model
- idempotency keys
- retry and dead-letter policy
- status transitions
- trace propagation
- artifact storage policy
- worker-local tests

## Risks

- duplicate execution
- stale status
- hard-to-debug async failures
- hidden dependency on local services

## Do Not Do Yet

Do not introduce an event bus or independent workers into the near-term
architecture unless a specific implementation phase proves it is necessary.
