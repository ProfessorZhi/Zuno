# Knowledge Product Boundary

## Purpose

This spec defines the product boundary for the next knowledge-system round.

It exists because the repo already has backend capability growth that the old knowledge configuration UI no longer expresses clearly.

## Product Surface

The user-facing product layer should expose only two retrieval modes:

1. `标准检索`
2. `增强检索`

Normal users should not need to see internal runtime mode names.

## Internal Runtime Modes

The runtime may still use multiple internal modes:

- `rag`
- `hybrid_rag`
- `local_graphrag`
- `community_global`
- `drift_like`
- `rag_graph_deep`

These are runtime and trace concepts, not primary product labels.

## Core Resource Boundary

```text
Domain Pack = reusable domain template
Knowledge Base = indexed instance that binds a Domain Pack
Enhanced Retrieval = routed retrieval umbrella, not one fixed retriever
```

## Page Boundary

### Domain Pack Page

Responsible for:

1. draft creation
2. representative file selection
3. AI-assisted draft generation
4. manual review
5. publishable versions

Not responsible for:

1. building a knowledge index
2. automatically rebuilding bound knowledge bases

### Knowledge Creation Wizard

Responsible for:

1. naming the knowledge base
2. choosing standard vs enhanced retrieval
3. choosing models
4. binding a Domain Pack
5. uploading files
6. previewing the build plan
7. starting the build

Not responsible for:

1. authoring the Domain Pack itself

### Knowledge Maintenance Page

Responsible for:

1. status display
2. retrieval mode display
3. model changes
4. config impact review
5. reindex and graph/community actions

Not responsible for:

1. full Domain Pack authoring workflow

## Product Rule

The product surface must remain simpler than the runtime surface.

The frontend should not collapse all lifecycle stages into one giant technical form.
