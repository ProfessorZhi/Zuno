# Architecture Review Report

## 当前结论

Python-only 和 Microservice 是 Owner Constraint/Accepted Target，但服务数量和边界仍需证据。Legal Domain Kernel、Domain-aware Runtime、GraphRAG、Multi-Agent、Memory Provider 和自研 Tool Runtime 均不能仅凭命名保留。

## 本轮研究输入后的收敛

LawBench、LJPCheck、JIA、Fact–Article Correspondence 和 InternLM-Law 的公开研究共同
支持一条较窄的方向：法律系统应把领域能力、中间业务结构、功能行为和真实任务结果
分层评测；这可以支持 Legal Capability Contract 和 Legal Eval 的 Target 设计。
这仍然是 `PUBLIC_CONTEXT`，不是 Zuno 已经实现或优于竞品的证据。

产品 Thesis 应使用：

> 业务语义强集成，技术实现松耦合。

也就是 Legal Domain State 可以成为 Planner、Retrieval、Capability、Evidence Gate、
Finding 和 Review 的 first-class Contract，但 Domain Owner 不依赖某一 Host、模型或
Runtime Provider。`H2 — Runtime–Domain Integration Advantage` 继续由 A/B/C 决定；
若 `C ≈ B > A`，保留 Legal Backend、削薄或删除 Native Runtime；若 `C ≈ B ≈ A`，
删除没有测量收益的复杂度。

## 必须继续攻击

- WorkBuddy + Legal Backend 是否足够；
- Hybrid RAG 是否足够；
- Single Agent + parallel tools 是否足够；
- Matter DB + Checkpoint 是否足够；
- Modular Monolith + Workers 是否满足 Target Constraint 下的 workload/failure/security。

Survived 设计最终写回 `docs/project/architecture/` 和 ADR，不在本报告形成第二套 Canonical Architecture。
