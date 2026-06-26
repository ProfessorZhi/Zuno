# Zuno Neo4j GraphRAG Design

## Goal

Add a real GraphRAG path using Neo4j for graph storage and graph retrieval, while preserving a clean boundary between standard RAG, graph retrieval, and future hybrid orchestration.

## Scope

This spec defines:

- Neo4j graph model
- graph extraction targets
- graph retrieval capabilities
- retrieval mode behavior
- first-version boundaries

## Why Neo4j

Neo4j is a graph database, not a relational database.

It models:

- nodes
- relationships
- properties

This is a better natural fit than PostgreSQL or MySQL for:

- multi-hop relation traversal
- neighborhood expansion
- path-oriented reasoning
- entity-centric retrieval

## Delivery Principle

The first version targets:

- real graph storage
- real graph lookup
- limited-hop expansion
- grounding graph results back to chunk evidence

It does not attempt to make GraphRAG the entire dominant retrieval engine on day one.

## Graph Model

### Node Types

#### `Entity`

Fields:

- `entity_id`
- `knowledge_id`
- `name`
- `type`
- `aliases`
- `attrs`

#### `Chunk`

Fields:

- `chunk_id`
- `knowledge_id`
- `file_id`
- `summary`
- `content_ref`

#### Optional `Document`

Fields:

- `file_id`
- `knowledge_id`
- `file_name`

### Relationship Types

- `(:Entity)-[:RELATES_TO {relation_type, confidence}]->(:Entity)`
- `(:Chunk)-[:MENTIONS]->(:Entity)`
- `(:Document)-[:HAS_CHUNK]->(:Chunk)`

## Extraction Model

Graph extraction consumes chunks and produces:

- normalized entity candidates
- normalized relation candidates
- chunk-to-entity references

The first version should keep extraction explicit and inspectable rather than overly clever.

## Retrieval Modes

### `rag`

Use standard chunk retrieval only.

### `graphrag`

Use:

- entity recognition from query
- entity lookup in Neo4j
- 1-hop or 2-hop expansion
- relation path collection
- chunk grounding where available

### `hybrid`

Run standard RAG and GraphRAG in parallel, then normalize and fuse results.

### `auto`

Use a conservative router:

- relation-heavy queries prefer GraphRAG
- direct evidence queries prefer RAG
- uncertain cases fall back to hybrid

## Orchestration Rule

The retrieval layer, not the agent, decides how retrieval is run.

This is critical.

Meaning:

- do not give the agent two raw result sets and ask it to choose blindly
- retrieval strategy belongs in a retrieval orchestrator
- the agent consumes normalized context

## First-Version Graph Retrieval Capabilities

Must support:

- exact or fuzzy entity hit
- neighbor expansion
- limited path context
- graph result to chunk grounding

Need not support yet:

- global graph ranking
- graph communities
- advanced graph algorithms
- graph embeddings as the primary ranker

## Frontend Product Behavior

Knowledge base configuration includes:

- `default_retrieval_mode`

Workspace can override per query:

- `default`
- `rag`
- `graphrag`
- `hybrid`
- `auto`

## Acceptance Criteria

- a knowledge base can build graph data in Neo4j
- graph queries can return relation-aware context
- retrieval mode can be selected from the API and UI
- at least one scenario demonstrates GraphRAG providing relation information that standard RAG misses
- LangSmith traces show when GraphRAG or hybrid was selected

## Upgrade Path

This design must allow later evolution to a stronger GraphRAG-primary system by:

- keeping retrieval strategy outside the agent
- normalizing retrieval result shapes
- separating graph storage from answer prompting

That lets the project move later from:

- "GraphRAG as a real retrieval enhancer"

to:

- "GraphRAG as a main retrieval engine"
