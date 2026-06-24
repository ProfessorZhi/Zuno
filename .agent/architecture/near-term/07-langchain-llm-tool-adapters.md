# LangChain LLM Tool Adapters

## Purpose

Define provider and tool boundaries without letting provider details leak into
routes or graph state.

## Current Evidence

- `src/backend/zuno/core/models/` and `src/backend/zuno/services/llm/` contain
  model configuration and provider logic.
- `src/backend/zuno/prompts/` contains prompt modules.
- `src/backend/zuno/services/embedding/` contains embedding providers.
- `src/backend/zuno/services/rag/rerank.py` isolates rerank calls and fallback.
- MCP code exists in `services/mcp`, `services/mcp_openai`, and `mcp_servers`.
- Local tools live in `src/backend/zuno/tools/`.

## Target Design

Adapter types:

```text
LLMProviderAdapter
EmbeddingProviderAdapter
RerankProviderAdapter
PromptRenderer
OutputParser
MCPToolAdapter
LocalToolAdapter
```

## Responsibilities

- normalize provider config
- render prompts by id/version
- hide provider request/response shape
- expose token/cost/latency metadata
- normalize errors and fallback reasons
- expose tool schemas and results consistently

## Non-Responsibilities

Adapters should not choose query method, decide business use cases, or mutate
GraphRAG project settings.

## Migration Notes

Future Java business adapters belong in `../future/`. Near-term adapter design
may reserve a generic service/tool adapter shape, but does not implement Java
business workflows.

## Acceptance Direction

Provider failures should be testable as normalized adapter failures, not route
or graph crashes.
