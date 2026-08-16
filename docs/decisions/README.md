# Active Architecture Decisions

本目录只保留仍然影响 Zuno 长期设计的 ADR。ADR 记录 durable decision（长期设计决定），不是项目故事、Current 运行证据或 Red / Blue 原始讨论。当前总体 Target 的整合表达见 [`docs/architecture/architecture.md`](../architecture/architecture.md)，模块内部细化见 [`docs/modules/`](../modules/README.md)，架构审查过程见 [`docs/history/red-blue/`](../history/red-blue/README.md)。

## 怎样处理 ADR 之间的先后关系

ADR 会随着架构演进发生 supersede / refine（取代 / 细化）。读取时遵守以下规则：

1. 先读当前总体架构，确认今天的九模块责任域和全局不变量；
2. 再读与问题直接相关的 ADR；
3. 如果较早 ADR 使用宽泛责任描述，而后续 ADR 明确重新划分 Owner，以后续显式 supersession / refinement 为准；
4. 后续 ADR 只改变自己声明的范围，不自动废弃较早 ADR 的其他仍兼容决定；
5. 模块文档只能细化这些 accepted decision，不能自行重新分配跨模块 Owner；
6. 如果两个 active ADR 真正无法通过明确的 supersession / refinement 解释，应记录 Architecture Gap，而不是让代码或某篇模块文档自行选边。

当前最重要的例子是：ADR-0008 决定最小 Legal Domain Kernel、Generic Host 边界和 Native Runtime 的测量门；ADR-0013 后来冻结九个逻辑责任域；ADR-0014 再明确 Authorization / Approval / Lifecycle policy、Formal Admission、Historical Citation、Invalidation、Delivery 和 Recovery 的权威 Owner。ADR-0008 中早期宽泛的 permission / audit 文字必须按后两份 ADR 解释，但它的最小 Domain Kernel 和 Host / Runtime 取舍仍然有效。

## 当前有效 ADR

- [ADR 0003：共享跨层 Contract](0003-wave1-cross-module-contract-freeze.md)：冻结跨层 Envelope、Owner、Provenance、Version 和基础设施访问边界；其中与九模块 taxonomy 冲突的分类部分已经由 ADR-0013 supersede，其余兼容 Contract 继续有效。
- [ADR 0005：LangGraph PostgreSQL Checkpointer](0005-official-langgraph-postgres-checkpointer.md)：Runtime Checkpoint 复用 LangGraph / PostgreSQL 能力，并与 Domain State 分离。
- [ADR 0006：Evidence-Driven Agentic GraphRAG](0006-evidence-driven-agentic-graphrag.md)：Graph / Agentic Retrieval 作为有证据门控的能力，不因名称自动成为 Kernel；当前总体架构进一步限定为 query-class / evidence-gated。
- [ADR 0007：Reuse-First Provider Boundary](0007-reuse-first-provider-boundary.md)：通用 Host、Provider 和基础设施优先复用，Zuno 维护法律业务 Contract 与 Domain 深度。
- [ADR 0008：Legal Domain Kernel and Host Boundary](0008-legal-domain-kernel-and-host-boundary.md)：冻结七对象最小 Domain Kernel、Generic Host + Legal Backend 的默认最小边界，以及 Native Runtime / Graph / Memory / Multi-Agent 的测量门；Ownership 细节按 ADR-0013 / 0014 后续细化。
- [ADR 0009：Python-only Backend](0009-python-only-backend.md)：Python 是当前后端 Target 约束，具体物理服务仍需证据门控。
- [ADR 0012：Evidence-Gated Physical Service Split](0012-evidence-gated-physical-service-split.md)：模块化 Backend + Worker 是默认物理起点，独立 Network Service 只能由 Scaling、Failure、Security、Availability、Lifecycle 或稳定跨主机 Contract 等证据触发。
- [ADR 0013：Round 02 Responsibility Taxonomy](0013-round-02-responsibility-taxonomy.md)：冻结九个 Logical Responsibility Modules、Platform / Infrastructure Responsibility Layer 和 Optional Context Provider；显式 supersede 旧分类中与其冲突的部分。
- [ADR 0014：Round 02 Cross-boundary Authority and Recovery](0014-round-02-cross-boundary-authority-and-recovery.md)：冻结 Invocation / Publication Authority、Historical Citation Binding、Effective Lifecycle Policy、AdmissionReceipt、Invalidation / Delivery / Ack 分离和 Critical Reconstruction / Recovery 语义。

## 维护规则

新 ADR 只在决策具有长期、跨边界和非局部反转成本时创建。一次性施工记录、临时实现方案、字段级局部重构和已经被完全取代的工作过程不需要继续作为 active ADR。

ADR 不自动授权实现。实现必须读取总体架构 Part A / B、对应模块 Part A / B、相关 Evidence 和当前工程任务，并经过独立实现 Gate、测试和审查。Current 只由代码、Migration、Test、Trace、Eval 或真实运行证据证明。
