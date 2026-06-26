# Future Direction Overview

## Future Direction

Zuno may eventually grow beyond a modular Python monorepo into a platform with
Java business services, service extraction, event-driven workers, independent
GraphRAG/evaluation runtimes, and multi-agent orchestration.

## Why It May Matter

- enterprise workflows may need stronger transaction and audit boundaries
- indexing and evaluation may need independent scaling
- complex tasks may need specialist planning and tool execution
- deployment ownership may diverge between AI runtime and business systems

## Possible Shape

```text
Frontend / Desktop
  -> API Gateway
  -> Python AI Runtime
  -> Java Business Services
  -> Knowledge / GraphRAG / Tool / Eval services
  -> Event bus and workers
  -> Observability stack
```

## Do Not Do Yet

Do not make these future pieces near-term acceptance gates. Near-term work
should only reserve clean context, trace, adapter, and version seams.
