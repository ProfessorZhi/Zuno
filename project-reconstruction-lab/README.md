# Project Reconstruction & Architecture Lab

## 定位

本目录是 Zuno 的项目重建与架构实验室，不是 Canonical Architecture，也不是简历生成器。它同时承载：

- 历史项目事实恢复；
- 模糊记忆的场景化恢复；
- 当前仓库证据审计；
- 开发过程和交付过程还原；
- Architecture Red Team / Blue Team / Counter Attack；
- 大厂面试官级项目深挖；
- Target Architecture consolidation；
- Architecture-to-Code gap 和 Codex task 规划；
- 可复用 Skill 的设计规范。

它明确不做：

```text
Resume Fabrication Tool
Architecture Decoration Tool
Buzzword Generator
Fake Production Evidence Generator
```

当前 GitHub / 本地仓库不等于完整历史项目，只能作为 `PARTIAL_REPOSITORY_EVIDENCE`。历史现实、当前仓库、重建候选、Target Architecture 和 Future 必须分开。

## Canonical Truth 边界

Lab 可以保留冲突、候选、攻击和未决问题；最终事实与正式架构只能写回：

```text
docs/project/facts/
docs/project/architecture/
docs/project/<topic>/
docs/decisions/
docs/governance/
docs/status/
docs/evidence/
```

Lab 不拥有第二套长期架构事实源。

## 新 Taxonomy

```text
project-reconstruction-lab/
├─ README.md
├─ migration-map.md
├─ 00-charter/
│  ├─ mission.md
│  ├─ evidence-rules.md
│  └─ state-model.md
├─ 01-facts/
│  ├─ fact-baseline.md
│  ├─ open-questions.md
│  ├─ evidence-ledger.md
│  ├─ memory-recovery.md
│  └─ contradictions.md
├─ 02-history/
│  ├─ project-background.md
│  ├─ development-timeline.md
│  ├─ team-and-ownership.md
│  ├─ delivery-history.md
│  └─ technology-history.md
├─ 03-current/
│  ├─ repository-reality.md
│  ├─ current-runtime.md
│  └─ current-gaps.md
├─ 04-product/
│  ├─ product-thesis.md
│  ├─ users-and-workflows.md
│  └─ problem-model.md
├─ 05-red-blue/
│  ├─ README.md
│  ├─ attack-registry.md
│  ├─ blue-responses.md
│  ├─ counter-attacks.md
│  └─ kill-tests.md
├─ 06-architecture/
│  ├─ architecture-candidates.md
│  ├─ consolidation-workflow.md
│  └─ mentor-review-package.md
├─ 07-interview-red-team/
│  ├─ interviewer-charter.md
│  ├─ question-bank.md
│  ├─ challenge-log.md
│  └─ readiness.md
├─ 08-decisions/
│  ├─ decision-candidates.md
│  ├─ adr-backlog.md
│  └─ survive-delete-defer.md
├─ 09-implementation/
│  ├─ architecture-to-code-gap.md
│  ├─ architecture-to-code-workflow.md
│  ├─ migration-strategy.md
│  └─ codex-task-backlog.md
├─ 10-reports/
│  ├─ fact-audit-report.md
│  ├─ architecture-review-report.md
│  ├─ interview-readiness-report.md
│  └─ migration-map.md
├─ skills/
│  ├─ README.md
│  ├─ project-reconstruction-skill-spec.md
│  ├─ architecture-red-blue-skill-spec.md
│  └─ big-tech-interviewer-red-team-skill-spec.md
├─ sessions/       # 已完成的可审计会话
├─ sources/        # 外部资料与仓库侦察快照
├─ workflows/      # 历史可复用执行材料
└─ legacy/         # 旧编号文档和旧 Skill Spec，可追溯但不再是主入口
```

V2 Red/Blue Round 的历史执行契约见 `05-red-blue/round-protocol-v2.md`；Round-001 至 Round-005
继续按各自 V2/V3/V3.1.3 协议保持 immutable。Round-006 以后使用
`05-red-blue/round-protocol-v4.2.md`：Fresh Context、Dual Thread、Conceptual Architecture、
逐题 Adaptive Interrogation、Append-only Question/Answer Ledger、Artifact Handoff、
Interview-Calibrated Red 和外部 ChatGPT Audit。V4.1 作为历史工作流基线保留，不 retroactively
改写历史 Round，也不把 Implementation Evidence 当作 Architecture
Review 的前置 Gate。
Round-001 的完整 100 题记录位于 `sessions/RB-WORKFLOW-V2-001/`，保持 immutable history；
Round-002 位于 `sessions/RB-WORKFLOW-V3-ROUND-002/`，按 V3 完成 Question → Answer → Score
→ Decision → Delta → Canonical Sync。Round-003 使用 V3.1，额外审查 Canonical Part A / Part B
质量和每题 `document_impact`；V3.1.1 归一化会话 `sessions/RB-DOCUMENT-NORMALIZATION-V3.1.1/`
负责移除旧正文混排，并要求 SECTION_REWRITE/FULL_PART_REWRITE。

Round-001 后的 Blue Repair 记录位于 `sessions/RB-BLUE-REPAIR-001/`。它负责根因聚类、Part-A
修复、Severity Reclassification、P0 Burn-down 和 Counter Retest；它不是第二轮 100Q，也不
改变 Round-001 的原始记录。Round-002 通过 V3 重新检验了这些变化。

Final P0 的证据战役记录位于 `sessions/RB-EVIDENCE-CLOSURE-001/`。它不重开 100Q，而是逐项
记录 Evidence ID、Closure Condition、实际 Artifact、Red Evidence Review 和 Counter Retest。
当前 12 个 Final P0 均未闭合，已有 10 项 V3 窄证据，Closure-grade evidence 为 `0/12`。

随后执行的 `sessions/RB-P0-V4-EXECUTION-001/` 只验证可安全执行的 V4 候选：6 项 V4
verification/emulator records、5 项 V3 current/narrow records；Red accepted 为 0，Counter
Retest 未运行，12 个原始 P0 仍保持 OPEN。Q039 被追踪为 Q039-C Critical Invariant 与
Q039-B V5 Benchmark Gap，原始 Q039 不删除。

每个专题只回答自己的问题。`02-history/` 与 `03-current/` 是工作视图，不替代 `docs/project/facts/`；`06-architecture/` 不替代 `docs/project/architecture/`。

## Continuous Reconstruction Loop

```text
Workspace Bootstrap
  → Evidence Intake
  → Fact Recovery
  → Memory Recovery
  → Historical Timeline
  → Current Repository Audit
  → Product Reconstruction
  → Architecture Red Attack
  → Blue Reconstruction
  → Counter Attack
  → Big Tech Interview Attack
  → Gap Repair
  → Architecture Consolidation
  → Closure Class / User Architecture Gate
  → ADR Preparation
  → Canonical Docs Sync
  → Architecture-to-Code Gap
  → Codex Task Candidate
  → User-approved Implementation Program
  → Implementation Review
  ↺ 新证据回到 Fact Recovery / Architecture Red Team
```

V3.1.2 Round-004 以 Human Writing、Architecture Consistency、Failure Semantics 和 Component Survival 为主题，保持 immutable。
V3.1.3 Round-005 进一步审查 Deep Failure、Recovery、Concurrency 和 Closure Classification Integrity；它新增 A/I/E/X 分布审计与 Part A 连续阅读规则，但不重写 Round-004，也不把分类结果当作 Runtime 或生产证据。
V3.1.3.1 作为 Round-005 关闭后的 Derived Semantic Audit，重新判断 attack-time/post-round Closure Class 和 finding state；它不修改 Round-005 原件，也不改变 Facts、Runtime 或 Production 状态。

## 当前 Program：ZUNO-RED-BLUE-WORKFLOW-V4.2 / RB-WORKFLOW-V4.2-BOOTSTRAP

Canonical Facts Framework V1 已形成。本 Program 不再扩张事实目录，而是把事实深度恢复
与架构重构并行推进：

| Track | 目标 | 当前输出边界 |
|---|---|---|
| Track A — Fact Depth Recovery | 恢复真实法院工作流、个人代码 Ownership、Court QA、Incident、协作和复用/研究转化 | 只进入 Facts、Evidence Ledger、Open Questions 或候选，不创造未知细节 |
| Track B — Architecture Reconstruction | 从真实问题推导 Product、Domain、Runtime、Knowledge、Service、Data、Security 和 Eval | V3 允许受 Gate 规则约束的 refinement AUTO_APPLY；重大原则变化仍只进入 Escalation |

## Fact Readiness Gate

事实层不追求 `UNKNOWN = 0`。当下面主链能够逐段回答，且每段都标注事实状态与 Evidence
ID 时，即可在事实未完全闭合的情况下开始架构重构：

```text
为什么做
  → 谁在用
  → 团队怎么做
  → 我做了什么
  → 一个请求怎么跑
  → 真实遇到什么问题
  → 怎么改
  → 怎么测试
  → 客户怎么反馈
  → 为什么后来要改架构
```

正式产品名、合同甲方、精确法院名单、历史中间件、用户规模、SLA 和指标如果没有证据，
继续保持 `UNKNOWN`，不成为架构启动阻塞项。

## Architecture Review Gate

本 Program 的目标不是把已有 Target 文档重新排版，而是对每项复杂度执行：

```text
Historical Problem
→ Candidate Design
→ Red Attack
→ Blue Response
→ Counter Attack
→ Benchmark / Spike / Evidence
→ KEEP / SIMPLIFY / EXTERNALIZE / DEFER / DELETE
```

Python-only 和 Microservice 是 Owner 给定的 Target Constraint；Red Team 仍必须攻击第二
语言、服务数量、服务边界、Worker/Library 替代、通信与数据成本。Multi-Agent、LangGraph、
GraphRAG、Memory、OpenViking、Legal Domain Kernel 和 Native Domain-aware Runtime 都不是
因为当前文档出现就自动保留。

本 Program 是 active design program，不是 implementation program。业务 Runtime、UI、
Schema/Migration、依赖和生产 Infra 不在本轮修改范围内；Implementation Task Candidate 可以
在 Lab 中记录，但必须等用户通过 Architecture Gate 后才能激活 implementation Program。

V4.2 Bootstrap 只改工作流和治理。Architecture Evolution Track 当前为
`ROUND-006 BLOCKED_BY_USER_GATE / ARCHITECTURE_BLOCKER`；已完成 3 个真实 Live Turn，但因 Session
Handoff API 返回旧 completed response 而停止，Architecture Score 无效；Implementation Evidence Track 保留
`IMPLEMENTATION-EVIDENCE-CYCLE-001` 的真实状态，当前为 `WAITING_FOR_RED_COUNTER_RETEST`。
两条 Track 通过 Canonical Architecture 和 Architecture Delta 反馈，但互不作为对方的自动 Gate。

V4.2 规定：Main Thread 每次只冻结一个 Question、一个 Answer 和一个 Chain Decision；
`question-answer-ledger.jsonl` 是 append-only 记录，禁止 `questions_frozen_sha`、`red-questions.md`
和 Q001–Q100 预生成题单。Interview calibration 只进入 Red Context，Blue Context 必须禁止读取。
Chain 的后续问题必须由上一 Answer 的 follow-up reason 触发；只有 `LIVE_ATTACK_COMPLETE` 后，Blue
才能进行 Candidate Canonical Rewrite。80–100 题是实际预算，不是预设题单。

## Reader Paths

| Reader | 路径 |
|---|---|
| 用户：我到底做过什么？ | `01-facts/` → `02-history/` → `07-interview-red-team/personal-contribution` |
| 导师 / 架构师：设计是否成立？ | `01-facts/` → `04-product/` → `05-red-blue/` → `06-architecture/` |
| 面试官：是否真的做过？ | `01-facts/` → `03-current/` → `07-interview-red-team/` |
| 工程实现者：下一步改什么？ | `06-architecture/` → `09-implementation/` → `docs/project/` / ADR |

## 统一原则

1. 先证据，后叙事；先最小事实，后候选解释。
2. 用户确认、仓库证据、Artifact、公开背景和模型推断不能混标签。
3. Red 不负责守住旧架构；Blue 必须证明复杂度；Counter Attack 必须真实发生。
4. Interview Ready 不等于 Production Ready。
5. 任何复杂度都必须能回答：为什么存在、为什么不是 Library/Worker/已有 OSS、如何失败、如何删除。

## 验证入口

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python tools/scripts/verify_red_blue_session.py
python tools/scripts/verify_red_blue_round_v2.py
python tools/scripts/verify_red_blue_round_v3.py
python tools/scripts/verify_red_blue_score_v3.py
python tools/scripts/verify_canonical_diff_v3.py
python tools/scripts/verify_red_blue_round_v31.py
python tools/scripts/verify_document_quality_v31.py
python tools/scripts/verify_document_normalization_v311.py
python tools/scripts/verify_human_writing_v312.py
python tools/scripts/verify_red_blue_round_v312.py
python tools/scripts/verify_red_blue_workflow_v4.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP
```

完整 CI 未运行时，不得写 `CI PASS`。
