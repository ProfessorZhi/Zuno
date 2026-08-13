# Skill Spec: architecture-red-blue

## Purpose

攻击架构中没有证据的复杂度，经过 Blue Response 和 Counter Attack 后形成 KEEP、SIMPLIFY、EXTERNALIZE、DEFER 或 DELETE 决策。

## Inputs

Repository Reality、Fact Baseline、Target constraints、Canonical Docs、ADR、替代方案、Benchmark/Spike 结果。

## Workflow

```text
Claim Registry
→ Red Attack
→ Blue Contract
→ Counter Attack
→ Kill Test / Benchmark
→ Decision Candidate
→ ADR / Canonical Sync
```

## Outputs

Attack Registry、Blue Response、Counter Attack、Kill Tests、Decision Candidate、ADR Backlog 和 Architecture Review Report。

## V3 Scored Round Contract

`ZUNO-RED-BLUE-WORKFLOW-V3` 是可重复执行的 Round 协议，不是脱离项目上下文的静态题库。每个
Round 固定记录 100 个独立问题，按 11+1 Lens 配额分布；每题记录完整 Question、Blue Answer、
Red Score 和 Blue Decision。Round 还必须生成 Delta、Canonical Sync Record、完整性验证和
ChatGPT Review Package。

Round 完整记录位于 `project-reconstruction-lab/sessions/<session-id>/`，至少包含
`manifest.yaml`、`transcript.md`、`scorecard.md`、`gaps.md`、`blue-change-set.md`、`retest.md`
和 `round-report.md`。分数不能单独通过 Round：Canonical State、不可逆副作用、权限/审批、
重复执行、数据损坏、版本冲突、跨服务一致性和证据完整性等 Critical Gate 仍为 OPEN 时，
状态必须保持 `NOT_PASSED_PENDING_USER_GATE`。

Blue Decision 完成后，允许的 Contract/State/Failure/Owner/Provider/Eval/Reversal refinement
必须在同一 Round 通过 Delta trace 自动同步 Canonical Docs；改变基本原则、Active ADR、重大
安全边界或 Python-only/Microservice/Single Controller 的变化只能进入 ADR/User Gate Escalation。
Round 记录仍是 immutable history，后续错误使用 Errata，不无痕改写。

## V3.1 Document Quality Contract

V3.1 在每个 Canonical Owner Doc 内固定同文件双层结构：Part A — Architecture Narrative
回答问题、场景、职责边界、Happy Path、主要失败、取舍、替代方案、反转条件和
Current/Target/Gap；Part B — Detailed Architecture Specification 定义输入输出、状态/版本、
错误传播、重试恢复、幂等、安全、审计、可观测性、所有权、扩缩容、兼容性和验证证据。
不创建 `-human.md`、`-spec.md` 或第二套 Canonical 文档；Part A 与 Part B 不复制同一状态机。

每道 Round-003 问题必须记录 `document_impact: PART_A | PART_B | BOTH | NONE`，同时记录
Part A/Part B Change Required 和 Canonical Owner Doc。Part A 质量门槛为 80，Part B 为 85；
门槛只衡量文档可读性和契约完整性，不代表 Runtime、法律回答、安全或 Production 证据。
Round/Dxxx/Qxxx 追踪只保留在 Lab Session、Delta 和 Review Package，不写回 Canonical 正文。

## Guardrails

- 不因“企业级”保留服务；
- 不将 GraphRAG、Multi-Agent、Memory 或自研 Runtime 视为默认必要；
- WorkBuddy/Dify/Pi/LangGraph/RAGFlow 按层级比较；
- 任何质量、效率、安全和生产声明必须绑定测量证据。
- `AUTO_APPLY` 只允许不改变 Facts、Runtime、Schema/Migration、基础架构原则或 Active ADR 的
  Target/document refinement；否则必须升级 ADR 或 User Gate。

## V3.1.3 Review Contract

每题独立判断 Severity 和 Primary Closure Class：先排除架构矛盾，再判断实现、测量和外部资格；不能把“代码还没写”自动归为 `I`。记录 `secondary_gaps` 与一句 `closure_class_rationale`，Round 末生成 A/I/E/X 分布审计；任一类别超过 80% 时至少人工抽查 20 题。Part A 同步采用 Human Continuity Pass，从第一段读到最后一段，禁止把 Delta 逐条追加到结尾。

## V4 Fresh Context / Dual Thread

Round-006 以后，Architecture Review 必须由两个全新的逻辑 Session 执行：Red Challenger/Judge
与 Blue Canonical Writer。两者从同一个 `canonical-snapshot.yaml` 开始，只通过仓库 Artifact
交接；Red 只读且不能写 Canonical，Blue 不能改 Red Questions、Facts 或 Score。Red Questions
冻结后才能启动 Blue，Blue Sync 后 Red 才能读取 Judge Packet 进行 Counter Review。

Round 在用户提供 ChatGPT External Verdict 前保持 `WAITING_FOR_CHATGPT_REVIEW`；Skill 不能代签
`ACCEPT`，也不能把 Architecture Score 当作 `IMPLEMENTED` 或 `MEASURED`。本 Skill 可生成
Prompt、Context Packet、Manifest、Review Package 和 Manual Launch 指引，但当前没有可靠
Codex Thread API 时不得伪造 Session 已启动。Architecture Evolution 与 Implementation Evidence
是并行 Track，后者未完成不自动阻塞前者。

## V4.1 Interview-Calibrated Red Extension

Red 读取 Main Thread 为本轮生成的 `interview-calibration-packet.md`，但只把它当作提问行为
校准。默认使用 `Architecture Interviewer` 主画像，必要时加入 Open-source Skeptic 与
Failure/Counterfactual 交叉画像；不得把外部面经的答案、候选人话术或事实注入 Blue。

100Q 组织为 12–18 条 Deep-Dive Attack Chain。每条链从 Claim 连续追到必要性、边界、Owner、
失败、成本、替代和反转，并记录 `questioning_pattern_source`、至少一个压力类型和一个约束。
每条链的 `INTERVIEW_DEPTH: 0–5` 只用于问题质量，不进入 Architecture Score；问题质量不足时
输出 `QUESTION_QUALITY_BLOCKED`。Blue 不读取 calibration packet，仍按 Part-A Cold-Start 完成
概念防守；Red Judge 另记录 `INTERVIEW_EXPLAINABILITY: CLEAR | DENSE | TERM_DEPENDENT | MISSING`。

## V4.2 Adaptive Interrogation Contract

V4.2 以后采用 `QUESTION_BY_QUESTION_ADAPTIVE_INTERROGATION`。Main 每次只冻结一个 Question、
一个 Answer 和一个 Chain Decision；Red 必须读取上一 Answer 后决定下一问，不能预生成 Q001–Q100。
所有事件进入 append-only `question-answer-ledger.jsonl`，follow-up 记录 `followup_reason`、
触发说明和上一 Answer 引用。Blue Live 阶段只回答 BASE Snapshot，不读 calibration、不读代码、
不写 Canonical；`BLUE_ARCHITECTURE_SYNTHESIS` 只能在 `LIVE_ATTACK_COMPLETE` 后开始。验证入口为
`verify_red_blue_workflow_v42.py`，Round-006 仍须等待外部 ChatGPT Review，Bootstrap 不代表 Pilot 已运行。
