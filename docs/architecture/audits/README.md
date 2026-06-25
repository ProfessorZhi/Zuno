# Architecture Audits

This directory stores current-state audits that prepare a later implementation
phase. Audits are evidence documents, not execution plans.

Rules:

- Audits must describe what the repository supports now.
- Audits must distinguish backend support, frontend support, eval support, and
  documentation-only expectations.
- Audits must not silently change runtime architecture.
- Raw datasets, generated eval outputs, and large artifacts do not belong here.

## Current Audits

- [Benchmark Corpus Ingestion Plan](./benchmark-corpus-ingestion-plan.md)
- [Current Model And Retrieval Config Audit](./current-model-and-retrieval-config-audit.md)
- [Eval Graph Index Persistence Plan](./eval-graph-index-persistence-plan.md)
- [GraphRAG Retrieval Quality Optimization](./graphrag-retrieval-quality-optimization.md)
- [GraphRAG Forced Vs Auto Route Report](./graphrag-forced-vs-auto-route-report.md)
- [GraphRAG Route Activation Calibration](./graphrag-route-activation-calibration.md)
- [HotpotQA Hard-subset GraphRAG Tuning](./hotpotqa-hard-subset-graphrag-tuning.md)
- [Retrieval Mode Semantics Alignment](./retrieval-mode-semantics-alignment.md)
- [Retrieval Eval Mode Contract](./retrieval-eval-mode-contract.md)
- [Local Model Default Cleanup Plan](./local-model-default-cleanup-plan.md)
- [Model Registry And Defaults Audit](./model-registry-and-defaults-audit.md)
- [Real Runtime Multihop Eval Results](./real-runtime-multihop-eval-results.md)
- [Real Runtime Multihop Eval Standards](./real-runtime-multihop-eval-standards.md)
