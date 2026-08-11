# RED-KERNEL-V3 红队报告

## 结论先行

本轮没有证明 Zuno 需要独立的完整 Agent Host 或自研 Agent Runtime。最强的可被保留命题更窄：在跨文档、跨运行、需要人工修订、证据依赖失效和审计的法律任务中，可能需要一个法律业务状态后端；这个后端可以由 WorkBuddy、Dify、Pi 或其他 Host 通过 MCP/API 调用。

这不是 Zuno 当前能力优于 WorkBuddy 的结论。BASE_SHA 上没有足够的法律 Domain Kernel 代码、Migration、运行 Trace 或 Eval；质量、效率、安全和生产性均保持 Hypothesis/UNKNOWN。仓库侦察记录见 `project-red-blue/sources/repository-current-inventory.md`。

## 最强的十个反对理由

1. WorkBuddy 已公开横向 Agent、Skills、MCP 和任务执行能力；独立 Host 的增量价值没有证明。
2. WorkBuddy + 普通 MCP/API Legal Backend 可能覆盖 Domain-aware Runtime 的大部分收益；Runtime 可能只是搬运 orchestration。
3. Zuno 当前代码没有可证明的完整 Matter/Fact/Conflict/FindingVersion 法律状态闭环，Target 不能冒充 Current。
4. 全部候选法律对象会制造 identity、version、owner、dependency 和 migration 负担；多数对象应先是 projection 或 provider proposal。
5. New Evidence 的 stale/re-evaluation 可以用 PostgreSQL 当前事实、版本和依赖引用加异步工作流处理，不需要 Event Sourcing。
6. Exact statute 和语义检索可能由 lexical/dense/hybrid 解决；GraphRAG 的额外成本和错误传播尚未被 Kill Test 抵消。
7. Single Controller + parallel tools 或 ephemeral worker 可能足够；Persistent Multi-Agent Team 没有质量/效率证据。
8. Matter DB + checkpoint 可能覆盖工作上下文和恢复；独立 Long-term Memory 不应成为硬依赖。
9. MCP/API/CLI/现有 Sandbox 加授权、幂等、Receipt 和审计适配器可能足够；自研 Tool Runtime 没有独立必要性。
10. 数千用户的假设不能推出十一微服务；工作负载异构才是拆分理由，必须先证明模块化单体 + worker 不足。

## Domain Model 的最小定义

Domain Model 是软件对法律业务世界的正式、可审计表示，不是 LLM Model、Prompt、Knowledge Base、Memory、Skill、Tool、GraphRAG 或 LangGraph State。

V3 只保留以下最小 Canonical 候选：

| 层级 | 对象 | 规则 |
|---|---|---|
| 根与来源 | `Matter`、`DocumentVersion` | `Case` 是场景别名或 Profile，除非司法案件身份带来独立权限/生命周期，不能再造一个根对象 |
| 主张与证据 | `Claim`、`Evidence` | Claim 是待验证主张；Evidence 有来源、版本、引用位置和权限 |
| 结论与人工权威 | `Finding`、`HumanDecision`、`WorkProduct` | Finding 是受证据约束的工作结论；HumanDecision 是人工权威；WorkProduct 是发布物 |

`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase` 不删除其业务含义，但在没有稳定身份、版本、Owner、审查和跨运行复用证据前，只作为 typed proposal、retrieval projection、derived view 或 Capability Provider 输出。

每一个进入 Canonical Store 的对象必须回答：Identity、Version、Provenance、State、Ownership、Mutation Authority、Staleness、Dependency、Review、Audit。Provider 或 Agent 只能产生 `Proposal`、`Candidate`、`Observation`、`Reference`、`Receipt`，不能直接写 `FactVersion`、`ConflictVersion` 或 `FindingVersion`。

## New Evidence 的最小传播协议

```text
EvidenceVersion committed
  -> find dependent Claim / derived object
  -> mark affected Fact/Finding STALE or REVIEW_REQUIRED
  -> enqueue bounded re-evaluation when policy says so
  -> create new proposal/run
  -> Canonical Owner + human gate commit a new version
```

这不是自动全量重算，也不是默认 Event Sourcing。PostgreSQL 可以保存当前业务事实、不可变版本、依赖引用和审计记录；Checkpoint 只保存控制流恢复位置。恢复时以两者对账结果决定继续、补偿、阻塞或重评估。

## KEEP / SIMPLIFY / EXTERNALIZE / DEFER / DELETE

| 动作 | 保留内容 |
|---|---|
| KEEP | 最小 Canonical Domain State；Proposal → Owner → Version → Review；Evidence provenance；Security/approval/idempotency/audit；Legal Capability Contract；A/B/C 与安全 Benchmark |
| SIMPLIFY | Domain Object 集合；Postgres 当前事实+版本；Memory 先 Working/Session；模块化单体 + 独立 worker；普通 MCP/API Tool Adapter |
| EXTERNALIZE | Agent Host、模型、向量/混合/图检索、OCR/解析、Sandbox、LangGraph/Pi/WorkBuddy Runtime、法律算法 Provider |
| DEFER | Native Domain-aware Runtime；Persistent Multi-Agent；Always-on GraphRAG；Long-term Memory；微服务；Event Sourcing；自研 Tool Runtime |
| DELETE | 针对 WorkBuddy 的安全负面断言、闭源天然不安全、开源天然安全、GraphRAG 必优于 Hybrid、Multi-Agent 必优于 Single Agent、当前已领先或 production ready 等无证据陈述 |

## 三个最小充分架构

| 方案 | 概念/组件 | 新代码与运维成本 | 质量假设 | 替换成本 |
|---|---|---|---|---|
| A：WorkBuddy Host | WorkBuddy + Legal Knowledge Scopes + Skills + MCP/API capabilities；必要时一个事实存储 | 最低；Host 合同和数据边界需要核验 | 通用 Host 已覆盖单次/低状态任务；法律 Backend 价值未验证 | 最低，Host 可换 |
| B：Legal Backend | A + 最小 Canonical Domain Store + Evidence/Review API + typed capability providers + 轻量 async worker | 中等；仍不拥有 Native Runtime | 跨文档、跨运行、人工复核和 stale 传播可能改善质量/返工 | 中等；Host 与 Runtime 解耦 |
| C：Conditional Native Runtime | B + 可替换 Runtime Provider；Domain State 作为 typed input/output；不是 LangGraph checkpoint | 最高；只有 Benchmark 证明收益才承担 | C > B 才支持 first-class runtime；C ≈ B 时删除 C | 最高，应延后到可逆 Spike |

推荐顺序：先 A 做 Kill Zuno；若 Domain State/证据/审查无法稳定由 A 承载，进入 B；只有 C 在相同模型、语料、工具、提示、时间和 Token 预算下重复优于 B，才允许保留 C。

## 公平 Benchmark A/B/C

| 变体 | 固定条件 | 唯一变量 |
|---|---|---|
| A | 同一 Base Model、原始语料、外部工具、法律 Prompt/Skills、Token/时间预算 | WorkBuddy Generic Legal Agent |
| B | 同 A | WorkBuddy 调用 Zuno Legal Capabilities：event.extract/align、conflict.detect、fact_article.match、evidence.retrieve、similar_case.search、legal_applicability |
| C | 同 A/B；Capabilities 与输出格式相同 | Zuno Native Runtime + first-class Domain State、Evidence Requirement、Domain-aware Planning、Staleness、HITL |

必须按任务切片：cross-document analysis、multi-evidence reasoning、dispute identification、Fact–Article mapping、evidence sufficiency、legal applicability、similar case、long-running matter update。指标不能只用 LLM Judge：

- 质量：Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion。
- 效率：Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Domain State Reuse Rate、重复提取率、重试/重规划率。

解释规则：`C > B > A` 才同时支持 Legal Intelligence 与 Native Runtime；`C ≈ B > A` 只支持 Legal Backend，Host 可作为主要宿主；`C ≈ B ≈ A` 删除对应自研复杂度。

## Graph / Multi-Agent / Memory Kill Tests

- Graph：Fixed Vector、Fixed Hybrid、Always Graph、Agentic RAG without Graph、Conditional Legal Graph；按 Exact Statute、Similar Case、Claim→Evidence、Fact→LegalElement→Statute、cross-document chain 等 query class 测试 Recall@K、nDCG、证据充分性、引用正确性、Unsupported Claim、Latency/Token/Cost。
- Multi-Agent：L0 Single Agent、L1 Role Pipeline、L2 Ephemeral Worker、L3 Specialized Domain Agent、L4 Persistent Team；先比较 L0-L2，禁止把多个 Agent 等同多套法律代码。
- Memory：Single-run Context、Matter DB + Checkpoint、Working/Session Memory、Long-term Memory；只有跨任务复用收益超过污染、权限和维护成本才升级。

## 安全可验证性假设

不对 WorkBuddy 做安全负面断言。Zuno 只有一个待验证差异假设：更容易提供 Source-level Audit、Build Reproducibility、SBOM、Signed Artifact、Network Egress Audit、Secret/Model/Tool/Domain/Human Decision Trace、Sandbox Boundary Test。必须执行 no-egress、allowlist、secret leakage、cross-tenant、prompt injection + tool、sandbox escape、revoked permission、stale credential、duplicate side effect 等测试；在产生 attestation 前不能写成安全优势。

## 进入正式 Target 的结论

本轮允许进入正式 Target 的是“最小 Legal Domain Kernel + Host-agnostic Legal Backend + 可替换 Provider + Benchmark Gate”。Native Domain-aware Runtime 只进入 `DEFERRED / HYPOTHESIS`，不进入默认 Current 或不可替换架构。该边界由 ADR 0008 记录，若后续 C>B 未成立，ADR 的 reversal criteria 要求删除 C。
