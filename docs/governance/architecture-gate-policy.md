# Architecture Gate Policy

## Canonical Question

如何在不降低安全、质量和生产证据门槛的前提下，区分“架构尚未设计清楚”和“架构已
设计清楚但尚未实现、测量或取得外部资格”？

## Owner / Scope

- Owner：Architecture Governance Owner。
- 依赖：[Project Reconstruction Lab](../../project-reconstruction-lab/README.md)、
  `docs/project/architecture/`、`docs/status/production-readiness.md` 和相关 ADR。
- 本文拥有 Gate 语义；不拥有 Domain、Runtime、Service、Security 或 Eval 的第二套状态机。
- `project-reconstruction-lab/sessions/RB-GATE-REALIGNMENT-001/` 保存本次可回放的分类与用户
  决策包；它不是 Canonical Architecture。

## Severity 与 Closure Class 分离

`P0/P1/P2/P3` 仍表示风险严重度，不得因 Gate Realignment 改写历史严重度。另加一个与
Severity 正交的 `Closure Class`：

| Class | 全称 | 表示 | 阻塞 |
|---|---|---|---|
| `A` | `ARCHITECTURE_BLOCKING` | Target 存在未解决矛盾、Owner/State/Fault Contract 空洞 | User Architecture Gate |
| `I` | `IMPLEMENTATION_BLOCKING` | Target Contract 可描述，但 Current 尚未实现，不能取得实现级证据 | Implementation Complete / I-P0 Closure |
| `E` | `EVIDENCE_MEASUREMENT_BLOCKING` | 设计可审阅，但质量、效率或效果需要 Benchmark/Eval | `MEASURED` / Quality Proven |
| `X` | `EXTERNAL_QUALIFICATION_BLOCKING` | 设计可审阅，但外部环境或资格验证不可用 | Security Qualification / Production / External Validation |

派生标记可以写为 `P0-A`、`P0-I`、`P0-E`、`P0-X`。它们不是新的 Severity，也不能把
`OPEN` 自动改为 `CLOSED`。

## 成熟度不可跨级

```text
PROPOSED
  → UNDER_ATTACK
  → SURVIVED
  → ACCEPTED_TARGET
  → IMPLEMENTED
  → VERIFIED
  → MEASURED
  → PRODUCTION_PROVEN
```

含义严格区分：

- `SURVIVED`：Red/Blue/Counter Attack 后设计暂时成立；不表示用户批准或已有代码。
- `ACCEPTED_TARGET`：用户接受它作为下一阶段设计目标；不表示实现、验证、测量或生产。
- `IMPLEMENTED`：有对应代码、Migration（如需要）和测试证据。
- `VERIFIED`：通过声明范围内的运行验证和反驳测试。
- `MEASURED`：有固定条件、原始结果和可复现 Benchmark/Eval。
- `PRODUCTION_PROVEN`：有生产环境证据；不能由 Target 文档或目录存在推出。

## User Architecture Gate

User Gate 的问题是：

> 用户是否接受当前已经设计清楚的方案，作为下一阶段 Canonical Target Architecture？

通过条件：

```text
A-P0 = 0
核心 Domain / State / Ownership 没有设计级矛盾
关键 Failure / Retry / Recovery / Security Contract 已可描述
所有 I-P0 有 Target Contract 与 Implementation Task Candidate
所有 E-P0 有 Benchmark / Eval Plan
所有 X-P0 有 Qualification Plan
风险、Evidence Gap 和 Scope Boundary 可追踪
```

不要求：

```text
I-P0 = 0
E-P0 = 0
X-P0 = 0
```

User Gate 必须由用户明确决定，不能由模型、verifier 或分数代签。`PENDING_USER_DECISION`
是有效状态，不是失败伪装。

## 后续 Gate

```text
User Architecture Gate
  → Canonical Target Sync
  → Implementation Program
  → V4 Evidence / Red Evidence Review / Counter Retest
  → I-P0 Closure
  → V5 Benchmark
  → E-P0 Closure
  → External Qualification
  → X-P0 Closure
```

原始 P0 的关闭条件仍是相应证据通过 Red Review 并完成 Counter Retest；本 Policy 不修改
`RB-P0-V4-EXECUTION-001` 的 `P0 CLOSED = 0/12` 结果。

## 允许与禁止

允许：

- 在 User Gate 前生成 Lab 中的 Target Contract、Benchmark Plan、Qualification Plan 和
  `Codex Implementation Task Candidate`；
- 在 User Gate 通过后，另行生成有边界的 Implementation Program；
- 用实现、Benchmark 或外部资格结果反向触发 Red/Blue 和 Target Reversal。

禁止：

- 为减少 P0 数字而把 A 改成 I/E/X；
- 把任务 Candidate 写成 active implementation 或 `IMPLEMENTED`；
- 把计划、Mock、emulator、in-process contract 或 xfail 写成 closure-grade evidence；
- 把 `E-P0` 的计划写成 `MEASURED`；
- 把 `X-P0` 的环境阻塞写成安全或生产通过；
- 用本 Policy 代替用户 Gate 或 Canonical Owner。

## V4.1 Review Track 与 Implementation Track 分离

从 Round-006 起，Architecture Review 使用 `ZUNO-RED-BLUE-WORKFLOW-V4.1` 的 Fresh Context / Dual
Thread、Part-A Cold-Start 和 Interview-Calibrated Deep-Dive Chain 协议。它由独立 Red
Challenger/Judge、独立 Blue Canonical Writer 和外部 ChatGPT Auditor
组成；Red Questions、Blue Answers、Canonical Delta、Counter Review 和外部 Verdict 通过
Artifact 交接。没有用户提供的 ChatGPT Verdict，Round 只能保持
`WAITING_FOR_CHATGPT_REVIEW`，不得由 Codex 或 verifier 代签。

Architecture Evolution 与 Implementation Evidence 是并行 Track：实现未完成不能自动阻塞
架构讨论，架构分数也不能升级 `IMPLEMENTED`、`VERIFIED`、`MEASURED` 或 `PRODUCTION_PROVEN`。
实现反例应作为 Architecture Feedback Finding 进入下一轮 Red；架构 Delta 稳定后才生成
Implementation Gap。Fresh-context comprehension 是 Canonical 质量信号，而不是实现证据。

## V4.1 Interview-Calibrated Conceptual Review

V4.1 把 Architecture Review 与连续项目深挖的提问方法结合，但只借用
`QUESTIONING METHOD`，不把面试答案、候选人包装或外部面经推断写入 Zuno 事实。Main Thread
每轮生成会话级 `interview-calibration-packet.md`，按 `REAL_SELF_INTERVIEW`、
`HIGH_SIGNAL_PUBLIC_INTERVIEW`、`GENERAL_PUBLIC_INTERVIEW` 和 `GENERAL_ARCHITECTURE` 标注来源
权重；该 packet 只进入 Red Context，Blue Context 必须禁止读取。

Red 的默认质量单位从随机独立问题改为 12–18 条 `Deep-Dive Attack Chain`，总预算仍恰好 100Q。
每条链应从一个 Claim 连续追到必要性、设计理由、边界、Owner、失败、成本、替代和反转，且至少
注入一个反事实/替代/失败/反转条件与一个成本、时延、权限、版本、Provider、取消、并发或
副作用约束。无法提出足够高质量 Novel Chain 时，报告 `QUESTION_QUALITY_BLOCKED`，不得用同义
问题填数。`INTERVIEW_DEPTH: 0–5` 只衡量提问链质量，不改变 Architecture Defense Score。

Red 必须先把 `DomainVersion`、`EffectReceipt`、`Replan Barrier` 等内部术语还原为普通工程
问题；Blue 若只能依赖项目术语，Red Judge 记录 `CONCEPT_NOT_CLEAR` 或
`INTERVIEW_EXPLAINABILITY: TERM_DEPENDENT`。Part-A first pass 还需判断 Fresh Blue 能否在
30–90 秒内用普通语言解释概念，状态为 `CLEAR | DENSE | TERM_DEPENDENT | MISSING`。这项判断与
Human Writing Verifier 分离：Verifier 只能 warning，不能自动给人工写作或面试可解释性 PASS。
