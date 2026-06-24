# Design Options And Decisions

## Purpose

Record v0.1 decisions and alternatives.

## Decision 1: GraphRAG Integration

Options: direct Microsoft GraphRAG dependency, Zuno-native official-compatible,
hybrid adapter.

Decision: Zuno-native official-compatible now, adapter later.

Consequences: lowest immediate integration risk, keeps current Neo4j/retrieval
work useful, requires careful naming alignment.

## Decision 2: Query Method Naming

Options: `community`, `global`.

Decision: use `global`; community reports are assets.

Consequences: aligns with official GraphRAG concepts and avoids making storage
assets look like a first-class query method.

## Decision 3: Basic Definition

Options: vector-only, BM25 + vector + rerank.

Decision: Basic = BM25 + dense vector + fusion + rerank.

Consequences: Basic becomes the strong baseline and fallback path.

## Decision 4: Domain Pack Exit

Options: long-term shim, direct retirement.

Decision: direct retirement as target, with short migration bridges only.

Consequences: less legacy surface, but replacement GraphRAG project contracts
must be ready before deletion.

## Decision 5: Java Backend Integration

Options: Python calls Java, Java calls Python, gateway/event bus hybrid.

Decision: Python AI runtime calls Java business capability APIs; complex tasks
may become event-driven.

Consequences: Java owns business truth while Python remains AI runtime.

## Decision 6: Microservices

Options: immediate split, modular monolith first, gradual split.

Decision: modular monolith first, gradual split after interfaces stabilize.

## Decision 7: Multi-Agent

Options: default multi-agent for all tasks, complex-task only.

Decision: complex-task only; normal QA remains single-pipeline.
