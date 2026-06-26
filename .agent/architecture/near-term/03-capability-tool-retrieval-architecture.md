# Capability Tool Retrieval Architecture

## Purpose

Define how Zuno finds and injects tools, MCP connectors, skills, and knowledge
capabilities without loading every schema into every model call.

## Target Principle

Zuno should not inject all tool schemas on every turn. The target is fast tool
lookup and dynamic capability selection:

```text
Task / Context
  -> Capability Query
  -> ToolCard Retrieval
  -> Permission / Health / Cost Filter
  -> CapabilitySelectionTrace
  -> Selected schemas enter ModelContextPacket
```

## Capability Types

| Type | Meaning |
| --- | --- |
| Knowledge Capability | Read-only RAG, GraphRAG, project, search, or evidence capability. |
| Action Tools | Local functions, CLI actions, HTTP APIs, file/browser actions, and side-effecting tools. |
| MCP Connector | External tool/resource/prompt connection through MCP. |
| Skills | Agent operating instructions, workflows, examples, and rules loaded on demand. |

## ToolCard Registry

Every capability should have a ToolCard:

```text
ToolCard
  id
  name
  aliases
  type
  description
  input_schema_summary
  output_schema_summary
  permissions
  side_effects
  cost_hint
  latency_hint
  health
  examples
  owner_module
```

ToolCards are the retrieval corpus for capability selection. They are not the
same as full tool schemas. The selector retrieves and filters cards first, then
injects only the needed schemas.

## Retrieval Strategy

Capability lookup uses layered retrieval:

```text
1. keyword / alias exact lookup
2. Native BM25 over ToolCard text
3. optional vector retrieval over ToolCard embeddings
4. permission / health / cost filter
5. final selection and trace
```

Keyword and alias lookup handles exact names and stable product terms. Native
BM25 handles lexical matching without requiring Elasticsearch. Optional vector
retrieval handles semantic matches when embeddings are available.

## Native BM25 For Tools

Elasticsearch is an external retrieval backend. BM25 is a ranking algorithm.
Zuno target architecture needs a NativeBM25Retriever so capability and document
retrieval can work locally without equating Elasticsearch with BM25.

Target components:

```text
NativeBM25Index
  tokenizer
  inverted_index
  term_freq
  doc_freq
  doc_len
  avg_doc_len
  idf

NativeBM25Retriever
  build(documents)
  search(query, top_k)
  explain_score(query, doc_id)
```

Formula:

```text
score(q,d) =
Σ idf(t) * tf(t,d) * (k1 + 1)
 / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl))
```

Default parameters:

```text
k1 = 1.2 ~ 1.5
b = 0.75
```

## Selection Filter

After retrieval, selected candidates pass through:

- permission check
- user/project scope check
- health check
- side-effect policy
- cost and latency filter
- duplicate or alias collapse
- task relevance threshold

The result is a `CapabilitySelectionTrace` with:

- input task and context hash
- candidate ToolCard ids
- retrieval scores
- filters applied
- selected capability ids
- rejected capability ids and reasons
- injected schema ids

## Current / Target Boundary

Current code has capability metadata and a minimal selector foundation. The full
ToolCard retrieval system, Native BM25 over ToolCards, optional vector
capability search, production permission/health/cost filter, and complete
selection trace are Target.
