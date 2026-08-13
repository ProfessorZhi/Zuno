# ZUNO-RED-BLUE-WORKFLOW-V4.1

## 定位

V4.1 是 V4 的概念架构审查增强协议。它不修改 Canonical Architecture 内容，不启动
Round-006，不修改业务 Runtime；它只规定怎样用两个 Fresh Context Thread 检查架构是否能
脱离代码和历史对话独立成立。

```text
workflow: ZUNO-RED-BLUE-WORKFLOW-V4.1
round-006: READY_FOR_FRESH_RED_THREAD / NOT_STARTED
architecture_track: independent
implementation_track: independent
canonical_part_a: architecture-knowledge-source
chatgpt_merge_gate: required
```

V3、V3.1、V3.1.3 和 V4 历史会话保持 immutable。V4.1 不是把旧会话重新解释成 Fresh Context。

## 评审对象和权限

普通 Architecture Round 是 `CONCEPTUAL_ARCHITECTURE_REVIEW`，默认不读取业务实现代码。
它只回答：`WHY / WHAT / CONCEPT / BOUNDARY / OWNER / FLOW / STATE SEMANTICS / FAILURE
SEMANTICS / TRADEOFF / ALTERNATIVE / REVERSAL`。

- Red Thread 是 Conceptual Architecture Challenger 和后续 Judge，只读 Part A、必要 Facts、
  Active ADR、Governance、Fixed Principles 和上一轮 Question Index；不得修改 Canonical、Facts、
  ADR 或业务代码。
- Blue Thread 是 Conceptual Defense + Canonical Writer，只读同一 Snapshot、Part A、必要 Facts、
  ADR、Governance 和冻结问题；不得以代码当前形态作为架构成立的理由。
- Main Thread / Coordinator 负责 Snapshot、Packet、冻结、Branch/Worktree、Candidate 收集、
  verifier、ChatGPT Gate 和最终 merge；它不是 Red，也不是 Blue。
- ChatGPT 是 External Architecture Auditor。没有用户提供的有效 Verdict，Main 不得 merge。

只有 manifest 明确声明 `IMPLEMENTATION-FEEDBACK-ROUND`，Architecture Thread 才能读取实现
反馈；即便如此，代码是反例/证据，不是唯一架构理由。

## Canonical Part A Cold-Start Test

Canonical Part A 是 Architecture Knowledge Source，而不是项目术语字典。一个未参加此前
Session 的高级工程师，只读 Part A、必要 Facts、Active ADR、Governance 和自身通用架构知识，
应能解释：问题、核心概念、边界、Owner、完整流程、主要失败、Retry/Replan/Recovery 的区别、
替代方案、代价和反转条件。

若不能，优先记为 `CANONICAL_PART_A_GAP`，而不是去代码中寻找答案。Part A 使用
`CONCEPT_FIRST → TERM_SECOND → CONTRACT_LAST`：先用普通工程语言解释事情，再引入稳定术语，
最后把精确 Contract 放入 Part B。Part A 不应被 PlanVersion、DomainVersion、EffectReceipt
等内部名词占满。

## Red Question 质量

默认仍为恰好 100Q、11+1 Lens；100 是 Review Budget，不是作文 KPI。默认要求至少 75% Novel、
最多 25% Regression；若高质量问题不足，verifier 允许报告 `QUESTION_QUALITY_BLOCKED`，不得
用同义问题凑数。每题优先包含场景、设计选择、反例、替代方案和追问，禁止把 class、table、
SQL、Migration、API 路由或测试结果当作普通 Architecture Round 的主要问题。

## Blue 三阶段

1. `CONCEPTUAL_DEFENSE`：先判断攻击是否成立，先讲冲突和概念，再决定 KEEP、CLARIFY、REFINE、
   REPLACE、DELETE 或 DEFER。
2. `ARCHITECTURE_DECISION`：记录 Reasoning、Owner、State Meaning、Failure Meaning、Alternative、
   Tradeoff、Reversal 和 `part_a_support`。
3. `CANONICAL_REWRITE`：Blue 只能用 `SECTION_REWRITE`、`FULL_PART_REWRITE`、`NO_CHANGE` 或
   `ESCALATION` 同步 Canonical；禁止 `APPEND`。需要概念补全时必须形成 Part A Delta。

`part_a_support` 取值为 `SUFFICIENT`、`PARTIAL`、`GAP`。Blue 可以用自身通用架构知识补齐
`GAP`，但必须把缺口写入 Part A Delta；不能让答案成立而文档继续解释不了。

## 两阶段 Judge

Red Counter Review 先只读 Final Part A，逐题记录 `PART_A_DEFENSE: CLEAR | PARTIAL | MISSING`；
再读 Part B，确认 Narrative 与精确 Contract 没有矛盾。独立记录 Architecture Defense Score
（0–5）与 Part-A Explainability，不因答案长、术语多或表格多而加分。

Human Writing verifier 只能报告标题密度、列表/表格密度、英文术语密度、重复项目术语和过短
段落等 warning，不得自动宣布 Human Writing PASS。`PART_A_HUMAN_REVIEW` 由 Red Judge 与 ChatGPT
人工判断。

## Candidate Branch 与 Main Merge Gate

Blue 不直接修改或 push `main`。Blue 在 `candidate_branch != main_branch` 的 Branch/Worktree
提交 Candidate SHA；Main Thread 负责验证 Candidate、生成 Review Package，并等待 ChatGPT
`ACCEPT` 或 `ACCEPT_WITH_DEBT`。只有此时 Main Thread 才能 merge，写入 `main_final_sha`，然后
关闭 Red/Blue Session。其他 Verdict 保持 Candidate 在 main 之外，进入 Repair、Replay 或 User Gate。

## 双轨

Architecture Evolution 与 Implementation Evidence 并行。实现未完成不是 Architecture Round
停止理由；Architecture Review 也不能升级实现、测量或生产状态。实现若发现 Contract 无法实现、
恢复语义矛盾或安全边界错误，形成 `ARCHITECTURE_FEEDBACK_FINDING`，进入下一轮 Red Context。

## Round Artifact 增量

V4.1 在 V4 Artifact Contract 上增加：

```text
main-orchestrator-prompt.md
interview-calibration-packet.md
part-a-explainability.md
interview-depth.md
```

Manifest 至少增加：

```text
conceptual_architecture_review
red_reads_business_code
blue_reads_business_code
blue_uses_code_as_architecture_reason
candidate_branch
integration_branch
main_branch
blue_push_main
main_integrator
main_merge_requires_chatgpt_verdict
red_judge_part_a_first_pass
part_a_explainability_artifact
part_a_clear_count
part_a_partial_count
part_a_missing_count
human_writing_verifier_mode
merge_status
main_final_sha
interview_calibration_packet
interview_calibration_packet_sha
interview_calibration_read_by_red
interview_calibration_read_by_blue
deep_dive_chains
question_quality_status
novel_question_count
regression_question_count
interview_depth_artifact
```

## 验证入口

```powershell
python tools/scripts/verify_red_blue_workflow_v41.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.1-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v41.py --round project-reconstruction-lab/sessions/<round-id>
```

Verifier 只检查落盘 Artifact 和权限/状态不变量，不创建 Thread、不启动 Round、不读取业务
代码来替代 Part A、不修改 Canonical，也不代签 ChatGPT。

## V4.1 Addendum：Interview-Calibrated Conceptual Red

V4.1 的 Red 方法参考真实项目深挖中的提问行为，但不把面试材料当作 Zuno 事实、答案或
候选人包装。Main Thread 每轮先从外部来源生成 `interview-calibration-packet.md`，只提炼：

- Claim → Problem → Necessity → Design → Boundary → Owner → Failure → Cost → Alternative → Reversal 的连续追问方式；
- 反事实、替代方案、失败注入、约束变化、取舍和复盘问题；
- `Architecture Interviewer` 主画像，必要时叠加 `Open-source Skeptic` 与
  `Failure / Counterfactual Interviewer`。

来源按 `REAL_SELF_INTERVIEW`、`HIGH_SIGNAL_PUBLIC_INTERVIEW`、`GENERAL_PUBLIC_INTERVIEW` 和
`GENERAL_ARCHITECTURE` 分层。单一公司面经不能推出固定公司风格；`questioning_pattern_source`
只说明提问方式来源，不是答案来源。

Red 默认不再生成 100 个彼此独立的关键词题，而是生成 12–18 条 Deep-Dive Attack Chain，
每条通常 5–10 个有上下文连续性的追问，总数仍恰好 100。Round Manifest 还记录
`question_quality_status`、`novel_question_count` 和 `regression_question_count`；`READY`
必须满足至少 75 个 Novel、最多 25 个 Regression，否则只能记录 `QUESTION_QUALITY_BLOCKED`。
每条 Chain 必须记录
`chain_id`、`root_claim`、`question_ids`、`primary_concept`、至少一个
`counterfactual_used` / `alternative_used` / `failure_used` / `reversal_used`，并注入至少一个
成本、时延、权限、版本、Provider、取消、并发或副作用约束。若无法构造足够高质量的 Novel
Chain，状态为 `QUESTION_QUALITY_BLOCKED`，不能用同义问题补齐。

Red 问题优先使用自然工程追问，并先拆解项目内部术语：`DomainVersion` 先解释为“当前业务
事实是哪一版”，`EffectReceipt` 先解释为“外部动作到底有没有发生的可核验记录”。如果 Blue
只能依赖内部名词，记录 `CONCEPT_NOT_CLEAR`；如果 Part A 需要大量内部术语才能自然解释，
Red Judge 记录 `INTERVIEW_EXPLAINABILITY: TERM_DEPENDENT`。

每条 Chain 另记 `INTERVIEW_DEPTH: 0–5`，只用于判断 Red 问题质量，不计入 500 分的
Architecture Defense Score。Red Judge 在 Part-A first pass 后另记
`INTERVIEW_EXPLAINABILITY: CLEAR | DENSE | TERM_DEPENDENT | MISSING`；它判断 Fresh Blue 是否
能仅凭 Part A 用 30–90 秒的普通工程语言说明概念，不要求背诵术语。

`interview-calibration-packet.md` 只进入 Red Context，Blue Context 必须明确
`interview_calibration: PROHIBITED`。这样可以防止 Blue 根据题库定向背答案，保持 Part-A
Cold-Start Test 的意义。任何答案、指标、项目话术、面试包装和候选人真实性判断都不得进入
calibration packet。
