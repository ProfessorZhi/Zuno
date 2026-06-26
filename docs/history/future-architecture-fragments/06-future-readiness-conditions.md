# Future Readiness Conditions

## Purpose

State what must be true before future architecture becomes implementation work.

## Java Business Layer

- business workflows are specified
- Java owns business truth and audit
- Python/Java API contracts are written
- auth, tenant, trace, timeout, and idempotency rules exist

## Microservices

- module interfaces are stable in-process
- data ownership is explicit
- observability spans service boundaries
- local development cost is acceptable
- deployment and rollback story exists

## Multi-Agent

- single graph QA is reliable
- evidence and citation context are durable through handoff
- budget and loop guards are implemented
- specialist contracts are testable

## Event / Workers

- task state machine is defined
- retry and idempotency policy is defined
- artifact storage and trace propagation are defined
- operational monitoring exists
