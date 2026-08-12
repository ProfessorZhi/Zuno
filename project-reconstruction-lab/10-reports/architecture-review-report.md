# Architecture Review Report

## 当前结论

Python-only 和 Microservice 是 Owner Constraint/Accepted Target，但服务数量和边界仍需证据。Legal Domain Kernel、Domain-aware Runtime、GraphRAG、Multi-Agent、Memory Provider 和自研 Tool Runtime 均不能仅凭命名保留。

## 必须继续攻击

- WorkBuddy + Legal Backend 是否足够；
- Hybrid RAG 是否足够；
- Single Agent + parallel tools 是否足够；
- Matter DB + Checkpoint 是否足够；
- Modular Monolith + Workers 是否满足 Target Constraint 下的 workload/failure/security。

Survived 设计最终写回 `docs/project/architecture/` 和 ADR，不在本报告形成第二套 Canonical Architecture。
