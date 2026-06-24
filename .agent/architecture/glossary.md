# Glossary

## Knowledge Base

A user-visible collection of files, chunks, indexes, and retrieval settings.

## GraphRAG Project

The target GraphRAG unit for settings, prompts, input, output, cache, indexes,
community assets, query methods, and trace metadata.

## Prompt Tuning

Indexing-side process that adapts graph-generation prompts to project data.

## Index Version

Version identifier for vector, BM25, graph, and community assets.

## Prompt Version

Version identifier for extraction, indexing, or query prompts.

## Query Method

Answering strategy: `auto`, `basic`, `local`, `global`, or `drift`.

## Retriever

Recall channel such as BM25, dense vector, graph, community report search, or
requery.

## Evidence Bundle

Documents, graph paths, community reports, citations, and support verdict used
to justify an answer.

## Citation

Reference from answer content to source chunk, file, or graph-supported
evidence.

## Requery

Conditional second retrieval attempt using rewritten or follow-up queries.

## Community Report

GraphRAG asset summarizing a graph community. It supports `global` and `drift`;
it is not a first-level query method.

## Basic

Near-term strong non-graph RAG baseline: BM25, dense vector, fusion, rerank,
evidence check, requery, and citation.

## Local

GraphRAG query method for entity-specific questions using graph paths/neighbors
and raw chunks.

## Global

GraphRAG query method over community reports, often map-reduce style.

## DRIFT

GraphRAG query method that uses community context to create follow-up local or
basic retrieval.

## Retired Domain Pack

Current domain-specific packaging surface that is not the future GraphRAG
mainline.

## Retired agentchat

Legacy compatibility surface that should not remain a future front path.
