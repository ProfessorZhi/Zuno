# 架构决策记录

这里只保留仍然影响当前主线的正式 ADR。

当前有效决策：

- [ADR 0002：退休 compat namespace](0002-retire-compat-namespace.md)
- [ADR 0004：补登记既有 QueueClient 旁路](0004-corrective-queue-bypass-registration.md)
  - 当前状态：`accepted`；只纠正 PHASE01 遗漏的 pre-existing bypass，不授权新增 caller 或延长 removal deadline。

正式 Target 决议：

- [ADR 0003：Wave 1 跨模块 Contract 与 Infrastructure 物理边界冻结](0003-wave1-cross-module-contract-freeze.md)
  - 当前状态：`accepted-target`；已合并到 `main`，是正式共享 Target Contract，但不是 Current 或实现证据。
  - 冻结范围：服务端权威产品边界、`zuno/platform/**` 物理 Ownership、共享 Envelope、Security Epoch、Secret/Credential、Audit、Model Gateway、派生索引、PreparedToolAction、Failure Code 与 Retry/Recovery Owner。
- [ADR 0006：Evidence-Driven Conditional Retrieval Decision Architecture](0006-evidence-driven-agentic-graphrag.md)
  - 当前状态：`accepted-target`；定义 Architecture v2 的 Broad Evidence Discovery、Evidence Deliberation、Evidence Reasoning Graph、ClaimEvidenceState、Targeted Probe 与安全停止。
  - 不修改现有 Program 与 PHASE01–PHASE22，不构成代码、Migration、质量或生产就绪证据。
- [ADR 0007：Reuse-first 与可替换能力 Provider 边界](0007-reuse-first-provider-boundary.md)
  - 当前状态：`accepted-target`；确立 Zuno Domain / Control Plane 与可替换能力 Provider 的边界，以及 `Reuse First, Build Requires Evidence` 的 G1–G5 评审闸门。
  - 不把 RAGFlow、OpenViking、Onyx、Coze 或其他候选标记为最终 Adopt；不授权本轮实现 Adapter、Runtime、Migration 或 Production Benchmark。
- [ADR 0008：Legal Domain Kernel 与 Host Boundary](0008-legal-domain-kernel-and-host-boundary.md)
  - 当前状态：`accepted-target`；定义最小法律 Domain Kernel、Proposal/Owner Commit、Host + Backend 最小方案和 Native Runtime 的验证门。
- [ADR 0009：Python-only Backend](0009-python-only-backend.md)
  - 当前状态：`accepted-target`；Python-only 是目标约束，Java/Spring 仅通过外部协议集成。
- [ADR 0010：Microservice Target 与 Service Boundaries](0010-microservice-target-and-service-boundaries.md)
  - 当前状态：`accepted-target`；固定微服务目标，服务数量、边界和 Worker 形态由独立扩缩容、失败和安全证据约束。
- [ADR 0011：Architecture Document Taxonomy](0011-architecture-document-taxonomy.md)
  - 当前状态：`accepted-target`；以 Product/Domain/Agents/Knowledge/Services/Data/Security/Eval/Deployment 重建专题文档体系，旧 11 模块降为 Superseded。

已被替换的决策不再伪造一个当前树目录；需要考古时使用 Git history，或在
`docs/history/` 的批准摘要中读取结论。

新增 ADR 时优先记录：

- 会长期影响 runtime 边界的决策。
- 会长期影响 retrieval / evidence contract 的决策。
- 会影响目录结构、服务边界或公开 API 的决策。
