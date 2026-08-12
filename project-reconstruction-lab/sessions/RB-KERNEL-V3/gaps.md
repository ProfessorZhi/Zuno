# RB-KERNEL-V3 Gap Clusters

本轮结论不是“复杂架构正确”，而是把可删复杂度和仍值得验证的最小契约分开。所有 Gap 仍需代码、Migration、Trace、Eval、Spike 或用户证据关闭。

## CLUSTER-001

Gap IDs: GAP-V3-001, GAP-V3-002
Questions: Q001, Q002, Q003, Q024
Failed Claim: Zuno 必须拥有独立完整 Host 和 Native Runtime。
Root Cause: WorkBuddy + MCP/API Legal Backend 的能力边界和 C>B 的证据尚未测试。
Gap Types: BUILD_BUY_GAP, OVERENGINEERING_GAP, MEASUREMENT_GAP
Current Evidence: WorkBuddy 官方资料公开横向 Agent 能力；Zuno 当前没有法律 Domain Runtime 运行证据。
Required Research: 同模型/语料/工具/预算的 A/B/C；Host API contract fit；替换成本。
Suggested Blue Route: 先采用 Host + Backend；Native Runtime 只作为可逆 Provider。
Status: RESEARCH_REQUIRED

## CLUSTER-002

Gap IDs: GAP-V3-003, GAP-V3-005, GAP-V3-006
Questions: Q005, Q006, Q007, Q008, Q009
Failed Claim: 全部法律对象、Event Sourcing 和复杂 Domain State 都是必要的。
Root Cause: 业务对象的跨运行身份、版本、依赖失效和人工审查需求没有最小案例证据。
Gap Types: OVERENGINEERING_GAP, ARCHITECTURE_GAP, SECURITY_GAP
Current Evidence: 现有代码有通用 DocumentVersion/Claim/Evidence 结构；法律对象闭环未实现。
Required Research: 两个跨文档、带新证据和人工修订的真实案例；Postgres 版本化 spike。
Suggested Blue Route: 最小 Kernel + typed proposal + dependency invalidation；不默认 Event Sourcing。
Status: RESEARCH_REQUIRED

## CLUSTER-003

Gap IDs: GAP-V3-007
Questions: Q010, Q011
Failed Claim: Zuno 当前已有可宣称的 Legal Domain Kernel 和 first-class Domain Runtime。
Root Cause: Target 文档超前于代码、Migration、E2E Trace 和 Eval。
Gap Types: CURRENT_EVIDENCE_GAP
Current Evidence: BASE_SHA 未发现完整法律 Domain 类/表/运行闭环；Production Readiness 为 NOT_ESTABLISHED。
Required Research: 明确 implementation Program 后，才可建立 legal state code/trace/eval。
Suggested Blue Route: 正式文档标 Target/Hypothesis；不变更 Current status。
Status: USER_GATE

## CLUSTER-004

Gap IDs: GAP-V3-008, GAP-V3-009
Questions: Q012, Q013
Failed Claim: GraphRAG 默认优于 Hybrid RAG。
Root Cause: 没有按 query class 的 Kill Graph Test 和成本/错误传播数据。
Gap Types: BUILD_BUY_GAP, MEASUREMENT_GAP
Current Evidence: ADR 0006 已把 Graph 定义为 conditional，但没有本轮运行结果。
Required Research: Vector/Hybrid/Always Graph/Agentic no Graph/Conditional Graph 五路对照。
Suggested Blue Route: Graph 仅作为 Conditional Provider。
Status: RESEARCH_REQUIRED

## CLUSTER-005

Gap IDs: GAP-V3-010, GAP-V3-011, GAP-V3-012, GAP-V3-013
Questions: Q014, Q015, Q016, Q017, Q018
Failed Claim: Persistent Multi-Agent、独立 Memory、自研 Tool Runtime、十一微服务是默认必要条件。
Root Cause: 没有 L0-L3、Matter DB+Checkpoint、MCP/API Adapter、Modular Monolith+Workers 的对照证据。
Gap Types: OVERENGINEERING_GAP, BUILD_BUY_GAP
Current Evidence: 文档已描述部分边界；规模与真实 workload 仍 UNKNOWN，容量假设不是 Current。
Required Research: 逐项 kill test；保留可替换接口而不是预先部署复杂组件。
Suggested Blue Route: L0-L2 优先、Memory optional、MCP/API adapter、模块化单体+worker。
Status: RESEARCH_REQUIRED

## CLUSTER-006

Gap IDs: GAP-V3-004, GAP-V3-014
Questions: Q004, Q019, Q020
Failed Claim: Zuno 通过开源天然更安全，或 WorkBuddy 因闭源天然不安全。
Root Cause: 没有任何一方的同口径安全 Benchmark 和 attestation。
Gap Types: SECURITY_GAP, UNSUPPORTED_CLAIM
Current Evidence: WorkBuddy 公开企业能力存在；Zuno Security Verifiability 仍是 Target。
Required Research: no-egress、allowlist、secret、tenant、sandbox、injection、revocation、idempotency、SBOM、签名产物。
Suggested Blue Route: 以可验证性/部署主权为 Hypothesis，不做品牌攻击。
Status: RESEARCH_REQUIRED

## CLUSTER-007

Gap IDs: GAP-V3-015, GAP-V3-016
Questions: Q021, Q022
Failed Claim: 论文算法可直接写进 Agent，公开仓库即可商业复用。
Root Cause: Capability Contract、provider conformance 和 code/data/model license 还未完成。
Gap Types: ARCHITECTURE_GAP, LICENSE_GAP
Current Evidence: 公开论文和 InternLM-Law/LawBench 资料已记录；多数研究代码/数据授权 UNKNOWN。
Required Research: commit lock、输入输出 schema、复现、许可证与商用法律审查。
Suggested Blue Route: provider only returns proposals; no unreviewed source copy。
Status: RESEARCH_REQUIRED

## CLUSTER-008

Gap IDs: GAP-V3-017
Questions: Q023, Q024
Failed Claim: Zuno 当前已证明在法律质量、效率或生产性上优于通用 Host。
Root Cause: 没有 A/B/C 执行结果，也没有法律任务的 baseline、reviewer acceptance 或成本数据。
Gap Types: MEASUREMENT_GAP, CURRENT_EVIDENCE_GAP
Current Evidence: production readiness 与 eval baseline 明确保持未证明。
Required Research: 固定模型/语料/工具/提示预算/时间预算后执行 benchmark，并报告失败与成本。
Suggested Blue Route: 只把 benchmark protocol 进入 Target，不写 superiority。
Status: USER_GATE
