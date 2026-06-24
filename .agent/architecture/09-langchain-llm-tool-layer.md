# LangChain LLM Tool Layer

## Purpose

Define adapter boundaries for LLMs, prompts, tools, embeddings, and rerank.

## Current Evidence

- LLM and model config code exists in `src/backend/zuno/core/models/`,
  `src/backend/zuno/services/llm/`, and `src/backend/zuno/settings.py`.
- Prompts live in `src/backend/zuno/prompts/`.
- MCP services live in `src/backend/zuno/services/mcp/`,
  `src/backend/zuno/services/mcp_openai/`, and `src/backend/zuno/mcp_servers/`.
- Tool implementations live in `src/backend/zuno/tools/`.
- Rerank is isolated in `src/backend/zuno/services/rag/rerank.py`.
- Embedding providers live in `src/backend/zuno/services/embedding/`.

## Target Design

LLM and tool logic should be adapter-driven:

- LLM provider adapter
- embedding provider adapter
- rerank provider adapter
- prompt registry and renderer
- structured output parser
- MCP tool adapter
- local CLI tool adapter
- future Java business tool adapter

## Interfaces / Inputs / Outputs

Inputs: model slot, prompt id/version, messages, tool schema, user/tenant
context, trace id, budget policy.

Outputs: normalized model response, parsed structure, tool result, token/cost
metadata, latency, provider error, fallback reason.

## Failure / Fallback

Provider failures should not leak provider-specific exception shapes into
routes or graph state. The adapter should return normalized failure metadata and
allow graph-level fallback decisions.
