# Glossary

## Knowledge Base

A user-visible collection of files, chunks, indexes, and retrieval settings.

## GraphRAG Project

The target unit for GraphRAG settings, prompts, input, output, cache, indexes,
and query behavior.

## Prompt Tuning

Indexing-side process that adapts graph-generation prompts to project data.

## Index Version

Version identifier for vector, BM25, graph, and community assets.

## Prompt Version

Version identifier for extraction, indexing, or query prompts.

## Query Method

Answer strategy: `auto`, `basic`, `local`, `global`, or `drift`.

## Retriever

Recall channel such as BM25, dense vector, graph, community report, or requery.

## Evidence Bundle

The documents, graph paths, community reports, citations, and support verdict
used to justify an answer.

## Citation

A reference from answer content back to source chunk, file, or graph-supported
evidence.

## Requery

A conditional second retrieval attempt using rewritten or follow-up queries.

## Community Report

A GraphRAG asset summarizing a community in the graph. It supports global and
drift query methods.

## Local Search

GraphRAG query method for entity-specific questions using graph and raw chunks.

## Global Search

GraphRAG query method over community reports, often map-reduce style.

## DRIFT

GraphRAG query method that uses community context to expand local search with
follow-up questions.

## Basic

Zuno's strong non-graph RAG baseline: BM25, dense vector, fusion, rerank,
evidence check, requery, and citation.

## Java Business Service

Future business-truth service for rules, transactions, permissions, audit, and
enterprise workflows.

## Microservice

A separately deployable service with explicit API, data ownership, scaling, and
failure boundary.

## Multi-Agent

Future complex-task orchestration where a supervisor coordinates specialist
agents with explicit contracts.

## Tool Adapter

Boundary that normalizes local, MCP, remote API, or Java business capabilities
for graph/tool execution.

## Trace Context

Cross-layer metadata used to explain route, retrieval, fallback, model, tool,
cost, and evidence behavior.

## Retired Domain Pack

The current domain-specific packaging surface that is not the future GraphRAG
mainline.

## Retired agentchat

Legacy compatibility surface that should not remain a future front path.
