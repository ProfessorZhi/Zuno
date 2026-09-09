# Legacy Automated Red/Blue Program Summary

archive_state: FROZEN_HISTORY_SUMMARY
owner: Red / Blue History Owner
execution_mode: AUTOMATED
scope: V2–V4.2 automated architecture review and workflow-engineering records

## Purpose and boundary

本文件是旧自动化 Red/Blue 程序的唯一当前树摘要。它保留每个程序的来源文件名、原始状态、
基线、主题、可审计发现和最终处置，但不复制旧 Questions、Answers、Scores、Decision 或
Verifier 全文。原始包已经从当前树移除，仍可通过 Git history 按 `source_file` 考古。

这些记录属于 `HISTORY`，不定义今天的 Current Facts、Canonical Architecture、ADR、Runtime
行为或新的 Red/Blue Protocol。历史记录中的 `CANONICAL_SYNC_COMPLETE` 只描述当时流程的收口，
不代表今天的设计已被重新验证。

## Summary index

| legacy_id | source_file | execution_mode | original_status | original_base_sha | theme | score_validity | final_disposition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `RB-WORKFLOW-V2-001` | `automated-round-001-project-architecture-v2.md` | `AUTOMATED` | `ARCHIVED` / historical round `COMPLETED` | `1155d696fa0dcc08a7682f3c873c345cfccf016a` | 项目真实性、业务起点、产品价值和初始架构 | `RECORDED_HISTORICAL` | `ROUND_REVIEW_PENDING`; 事实恢复与架构候选保持分离 |
| `RB-WORKFLOW-V3-ROUND-002` | `automated-round-002-architecture-v3.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETE` | `19ba6e050e1334f71c511a5968c9ea9d15c68111` | 11+1 责任域的全面架构攻击、分数和 Canonical Delta | `RECORDED_HISTORICAL` | Target refinement was applied in that historical program; no current authority |
| `RB-WORKFLOW-V3-ROUND-003` | `automated-round-003-document-quality-v31.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETE` | `f866ca4d748ba189a83a39fe75b92a6ba36f4e9d` | 文档质量、Part A/B 和可读性门禁 | `RECORDED_HISTORICAL` | `DOC_QUALITY_COMPLETE` in the historical workflow only |
| `RB-WORKFLOW-V3-ROUND-004` | `automated-round-004-human-writing-v312.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETE` | `166a54d51aba0a822c3b5c539d1c43435f8c203f` | 架构一致性、失败语义、组件存活和人工写作审查 | `RECORDED_HISTORICAL` | Architecture integrity passed historically; human writing remained `WARNING` |
| `RB-WORKFLOW-V3-ROUND-005` | `automated-round-005-failure-recovery-v313.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETE` | `4e3ab8773da4edfaa769d3d2f6c4dce3ea63ea15` | 深层失败、恢复、并发、Provider 替换和复杂度存活 | `RECORDED_HISTORICAL` | Target-only refinements; no Runtime or Production proof |
| `RB-WORKFLOW-V4.2-ROUND-006` | `automated-round-006-operational-pilot.md` | `AUTOMATED` | `ABORTED` / `ABORTED_OPERATIONAL_PILOT` | `55510d236bcc039ca255f59d07ea61b36e04143a` | Adaptive Red/Blue operational pilot and workflow evidence | `INVALID` | `WORKFLOW_EXECUTION_BLOCKER`; no valid architecture score or merge |
| `RB-ARCH-001` | `automated-architecture-baseline-001.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETED` | `a739f77e35a6ecfa73942fef707f740fade76128` | 初始架构基线、项目真实性和证据边界 | `RECORDED_HISTORICAL` | `CANONICAL_SYNC_COMPLETE` then superseded by later governance |
| `RB-KERNEL-V3` | `automated-domain-kernel-v3.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETED` | `0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f` | Domain Kernel、Host substitution、Legal capability 和 Graph/Multi-Agent 必要性 | `RECORDED_HISTORICAL` | Provider lock-in was rejected; Native Runtime and quality gains remained hypotheses |
| `RB-ARCH-REFRAME-V1` | `automated-architecture-reframe-v1.md` | `AUTOMATED` | `ARCHIVED` / `COMPLETED` | `0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f` | Python-only、FastAPI/LangGraph 边界、Logical/Physical separation 和服务边界 | `RECORDED_HISTORICAL` | Python-only/Microservice remained Target constraints; service count was not frozen |

## Historical records

### `RB-WORKFLOW-V2-001` — Project Architecture V2

- `what_was_tested`: 100-question architecture review，重点攻击法院原始任务、回答质量、产品成功标准、Domain 和 Agent 价值是否有事实基础。
- `important_findings`: 真实法院工作流和质量反馈根因仍是 `UNKNOWN`；不能从“法律材料复杂”直接推出 GraphRAG、Memory 或 Multi-Agent。
- `final_disposition`: 将业务事实恢复和分层 Eval 放入后续工作；架构只能作为候选，不能把历史猜测写成事实。
- `relation_to_current_architecture`: 提供早期问题清单和证据边界，已被后续 Canonical/Manual 治理吸收并取代。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-WORKFLOW-V3-ROUND-002` — Architecture V3

- `what_was_tested`: 100 Questions / Answers / Scores / Decisions，80 novel、20 regression，围绕 11+1 责任域、Canonical State admission、Evidence 和服务/Provider 边界。
- `important_findings`: Proposal 不能直接成为 Canonical State；Domain Owner、Evidence、Provenance、Version、Review 和 Recovery 必须分开；Provider lock-in 不应被假设为必要。
- `final_disposition`: 历史流程标记 `COMPLETE`，曾应用 Target refinement；本摘要不继承其旧 11+1 quota 或流程契约。
- `relation_to_current_architecture`: 只作为演进背景和历史攻击证据；当前总架构仍由 `docs/architecture/` 持有。
- `git_history_note`: 完整 100Q 包由 `source_file` 对应的 Git 历史恢复。

### `RB-WORKFLOW-V3-ROUND-003` — Document Quality V3.1

- `what_was_tested`: 文档质量的 100Q chain、Part A/B gate、Canonical sync、Novel/Regression 分布和 11+1 覆盖。
- `important_findings`: 历史记录报告 `DOC_QUALITY_COMPLETE`，但它是当时的文档门禁结果，不是当前架构、Runtime 或 Production 证据。
- `final_disposition`: 保留为文档治理演进证据；旧固定轮次和题量不再是当前 Protocol。
- `relation_to_current_architecture`: 说明为什么后来需要人工可读性和历史治理重构，而不是当前文档的 Canonical Owner。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-WORKFLOW-V3-ROUND-004` — Human Writing V3.1.2

- `what_was_tested`: Failure Semantics、Domain/Runtime consistency、Memory/Graph/Citation/Tool/Approval/Queue/Provider 边界和 Human Writing Review。
- `important_findings`: 历史 `architecture_integrity: PASS`、Part A/B gate `PASS`，但 Human Writing Review 为 `WARNING`，自动信号不能代替人工阅读。
- `final_disposition`: 记录为历史完成轮次；保留人工可读性问题，不把自动分数升级为事实。
- `relation_to_current_architecture`: 为后来的可读性重建和 Manual ChatGPT workflow 提供背景。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-WORKFLOW-V3-ROUND-005` — Failure / Recovery V3.1.3

- `what_was_tested`: 100Q failure/recovery review，80 novel、20 regression，覆盖版本屏障、stale、Citation provenance、未知副作用、撤权竞态、Queue、滚动升级和 A/B/C 归因。
- `important_findings`: 历史分数为 `400/500`、`80.00`，P0 为 0、P1 为 15；仍明确声明不是 Runtime integration、法院 QA 或 Production Readiness 证明。
- `final_disposition`: Target refinement only；没有提升 Current、Measured、Verified 或 Production 状态。
- `relation_to_current_architecture`: 其失败语义和替换边界是历史输入，当前文档不得复制其旧流程或固定题量。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-WORKFLOW-V4.2-ROUND-006` — Operational Pilot

- `what_was_tested`: 试图验证 Fresh Session、Part-A Cold Start、Adaptive Follow-up、Red-only calibration、Live Canonical write postponement、Candidate branch isolation 和外部 Merge Gate。
- `important_findings`: Q001–Q003 形成了真实 Answer-triggered follow-up，但新 Chain 的 Session API 返回旧完成响应，Main 无法证明 Question/Answer 身份对应关系，因此在 Q003 后停止。
- `final_disposition`: `state: ABORTED_OPERATIONAL_PILOT`; `round_status: ABORTED_OPERATIONAL_PILOT`; `workflow_status: BLOCKED`; `stop_reason: WORKFLOW_EXECUTION_BLOCKER`; `architecture_score: INVALID`; `score_validity: INVALID`。没有 Blue Synthesis、Candidate Branch、Red Judge 或 Main Merge。
- `relation_to_current_architecture`: 这是工作流执行失败证据，不是 Zuno Architecture Failure，也不是 A-class Architecture Blocker。
- `git_history_note`: 完整运行证据由 `source_file` 对应的 Git 历史恢复；不得补造后半轮答案。

### `RB-ARCH-001` — Architecture Baseline

- `what_was_tested`: 以事实和公开资料边界为前提的初始架构基线，攻击历史项目起点、用户、客户和架构候选的可证据性。
- `important_findings`: 历史用户、业务决策人和原始工作流不能在闭卷阶段被升级为已确认事实；需要保持 `UNKNOWN` 和 Evidence Gap。
- `final_disposition`: 历史标记 `CANONICAL_SYNC_COMPLETE`，随后被新的事实重建和架构治理吸收。
- `relation_to_current_architecture`: 仍可作为基线来源，但不是当前架构正文或当前事实源。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-KERNEL-V3` — Domain Kernel V3

- `what_was_tested`: WorkBuddy Host substitution、Legal Domain Kernel、Domain-aware Runtime、Security Verifiability、GraphRAG、Multi-Agent 和法律能力 Provider。
- `important_findings`: 不能证明独立 Native Runtime 必要；Legal Backend + 普通异步工作流是最小默认方案；Domain-aware Runtime 的质量/效率收益仍是 Hypothesis；WorkBuddy 安全攻击不能靠无证据绝对化；Provider 应可替换。
- `final_disposition`: `DEFER_NATIVE_RUNTIME`、`HYPOTHESIS_NOT_PROVEN`、`DELETE_UNSUPPORTED_ATTACK` 等历史处置，旧复杂度必须继续由 Benchmark 证明。
- `relation_to_current_architecture`: 提供 Build/Buy/Extend/Defer 的历史反证，不能冻结今天的服务或 Runtime 选择。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

### `RB-ARCH-REFRAME-V1` — Python Microservice Architecture Reframe

- `what_was_tested`: Python-only 与 Java/Spring 的边界、CPU/IO/GPU 工作负载、FastAPI/LangGraph 分工、Logical/Physical separation 和服务拆分理由。
- `important_findings`: Python-only 是 Target 约束而非历史事实；Python 主要承担控制/API/IO，重计算进入 Worker 或 native backend；Microservice 不等于 11 modules = 11 services；服务数不应由用户数推导。
- `final_disposition`: `KEEP_PYTHON_ONLY_TARGET`、`KEEP_MICROSERVICE_TARGET`，但服务数量和具体边界未冻结。
- `relation_to_current_architecture`: 这些是历史 Target reasoning；Current backend、真实服务数量和生产状态仍由代码与证据定义。
- `git_history_note`: 完整记录由 `source_file` 对应的 Git 历史恢复。

## Future handling

正式 Red/Blue 历史入口只保留 Manual full record 和本 Legacy Summary。未来 Manual Round 使用
`manual-round-NN-<theme>.md`；若用户明确重启 Automated Program，必须先建立新的治理决定，不能
把旧自动化文件格式默认为当前 Protocol。
