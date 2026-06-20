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
- [Local Model Default Cleanup Plan](./local-model-default-cleanup-plan.md)
- [Model Registry And Defaults Audit](./model-registry-and-defaults-audit.md)
- [Real Runtime Multihop Eval Standards](./real-runtime-multihop-eval-standards.md)
- [Tests Folder Organization Audit](./tests-folder-organization-audit.md)
