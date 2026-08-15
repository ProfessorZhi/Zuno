# Active Architecture Decisions

本目录只保留仍然影响 Zuno 长期设计的 ADR。它们记录 durable decision，不是项目故事、当前运行证据或 Red / Blue 原始讨论。架构审查过程见 [`docs/history/red-blue/`](../history/red-blue/README.md)，当前总体结果见 [`docs/architecture/architecture.md`](../architecture/architecture.md)。

## 当前有效 ADR

- [ADR 0003：共享跨层 Contract](0003-wave1-cross-module-contract-freeze.md)：冻结跨层 Envelope、Owner、Provenance、Version 和基础设施访问边界。
- [ADR 0005：LangGraph PostgreSQL Checkpointer](0005-official-langgraph-postgres-checkpointer.md)：Runtime Checkpoint 复用 LangGraph/PostgreSQL 能力，并与 Domain State 分离。
- [ADR 0006：Evidence-Driven Agentic GraphRAG](0006-evidence-driven-agentic-graphrag.md)：Graph / Agentic Retrieval 作为有证据门控的能力，不因名称自动成为 Kernel。
- [ADR 0007：Reuse-First Provider Boundary](0007-reuse-first-provider-boundary.md)：通用 Host、Provider 和基础设施优先复用，Zuno 维护法律业务 Contract 与 Domain 深度。
- [ADR 0008：Legal Domain Kernel and Host Boundary](0008-legal-domain-kernel-and-host-boundary.md)：Generic Host + Legal Backend 是默认最小边界，Native Runtime 需通过测量证明。
- [ADR 0009：Python-only Backend](0009-python-only-backend.md)：Python 是当前后端 Target 约束，具体物理服务仍需证据门控。
- [ADR 0012：Evidence-Gated Physical Service Split](0012-evidence-gated-physical-service-split.md)：模块化 Backend + Worker 是默认物理起点，独立 Network Service 只能由 Scaling、Failure、Security、Availability 或 Lifecycle 证据触发。
- [ADR 0013：Round 02 Responsibility Taxonomy](0013-round-02-responsibility-taxonomy.md)：以九个 Logical Responsibility Modules、Platform / Infrastructure Responsibility Layer 和 Optional Context Provider 替代旧的 10-module taxonomy；只部分 supersede ADR-0003 的分类部分。
- [ADR 0014：Round 02 Cross-boundary Authority and Recovery](0014-round-02-cross-boundary-authority-and-recovery.md)：冻结 Invocation/Publication Authority、Historical Citation Binding、Lifecycle Policy、AdmissionReceipt、Invalidation 分离和 Critical Reconstruction。

## 维护规则

新 ADR 只在决策具有长期、跨边界和非局部反转成本时创建。一次性实施记录、临时方案、旧过程契约和被替换的 taxonomy 不在当前目录保留；Git history 是考古来源。

ADR 不自动授权实现。实现仍需读取项目文档、总体架构、Evidence 和当前 Program，并通过相应验证。
