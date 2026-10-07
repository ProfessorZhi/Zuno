# Round 020 Artifact Links

Round: `rb-2026-10-07-formal-020`
State: `ACTIVE` — 全部角色阶段已完成，停在 `USER_IMPROVEMENT_REVIEW`
Base: `7d3081f2ccaa20c7eeb0bfff75206d08584a6e51`
Branch: `red-blue/rb-2026-10-07-formal-020` · PR [#280](https://github.com/ProfessorZhi/Zuno/pull/280)

| 项 | 值 |
| --- | --- |
| `mode` | `AGENT_AUTO` |
| `firewall_strength` | `PHYSICAL_CONTEXT_ISOLATION` |
| `strict_blind_red_certification` | `true` |
| Interview Threads | 10 |
| Wave 规模 | 100 问 / 100 答 × 2 波（共 400 条） |

## 先看这两个

- [09_improvement_ledger.md](09_improvement_ledger.md) — **`PENDING_USER_REVIEW`** —— 15 条提案，需批准
- [09_round_report.md](09_round_report.md) — 本轮报告

## Resume

- [01_simulated_resume.md](01_simulated_resume.md) — `FROZEN`（`user_resume_review_status: DELEGATED`）
- [10_next_resume_candidate.md](10_next_resume_candidate.md) — `BUILT_PENDING_USER_RESUME_REVIEW`

## Red

- [02_red_questions.md](02_red_questions.md) — `COMPLETE` · 100 题（Q1–Q100），61 处回钩
- ↳ 原始分批：`02_red_questions.part1.md`（Q1–Q50）/ `.part2.md`（Q51–Q100）—— 两个互不可见的隔离实例的原始输出，主文件为逐字拼接
- [04_red_wave2_review_and_questions.md](04_red_wave2_review_and_questions.md) — `COMPLETE` · Part A 盲评 + Q101–Q200 + 隔离审计附录
- [04_red_evaluation.md](04_red_evaluation.md) — `COMPLETE` · Red Final 盲评

## Blue — Candidate Answers

- [03_blue_answers.md](03_blue_answers.md) — `COMPLETE` · 100 答（A1–A100）
- [04_blue_wave2_answers.md](04_blue_wave2_answers.md) — `COMPLETE` · 100 答（A101–A200）

## Blue — Sealed Architecture Review

- [03_blue_architecture_notes.md](03_blue_architecture_notes.md) — `COMPLETE / SEALED_FROM_RED` · S01–S18
- [04_blue_wave2_architecture_notes.md](04_blue_wave2_architecture_notes.md) — `COMPLETE / SEALED_FROM_RED` · 复核 + N01–N04
- [05_blue_architecture_reflection.md](05_blue_architecture_reflection.md) — `COMPLETE` · 架构审判

## Controller

- [06_workflow_retrospective.md](06_workflow_retrospective.md) — `COMPLETE`
- [07_user_feedback.md](07_user_feedback.md) — `COMPLETE`
- [08_session_transcript.md](08_session_transcript.md) — `COMPLETE`
- [00_manifest.yaml](00_manifest.yaml) — `ACTIVE`

---

## Controller notes（Red 不可读）

### Resume boundary declaration

约束来自本轮 improvement ledger 与 `docs/governance/interview-acceptance-standard.md`。**Red Wave 1 只读 `01_simulated_resume.md`，不得读本页。**

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行（`docs/evidence/current-eval-baseline.md` 为 `MEASUREMENT_BLOCKED`）；已记录的只是 regression 修复与 baseline 保持。冻结协议见 `docs/governance/rb019-graphrag-ablation-protocol.md`。
- **不写任何 run-to-run 百分比。** `project-fact-provenance.md:96` 明确写着 baseline 的 `MRR@10` 在同日 rerun 中也从 `0.90` 变为 `1.00`，因此「修复前后」框架在本样本上不成立。正确说法是 local 与 baseline **打平**。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 全部为 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）。

**可以写，且经得起追问：** Tool/MCP binding、config injection、route boundary、GraphRAG baseline-preserving fusion、seed expansion / alias / path ranking、Context/Memory V2 与 readback 收紧，都有公开提交链支撑。

### Gate 说明

- `resume_review_gate: DELEGATED` —— 用户 2026-10-07 指示「你来进行一轮红蓝队对攻迭代」，Resume Gate 由 Controller 在委托下代行；用户仍可要求 `RESUME_REVISION` 并重跑本波。
- `improvement_review_gate: REQUIRED（未过）` —— 本轮 improvement ledger **不自动应用**。

### 已知结构性冲突

active round 分支的 Draft PR **无法**通过 `tests/repo/test_docs_entrypoints.py`：该测试要求 `.agent/red-blue/current.md` 为 `state: no-active`，而 active round 必然是 `state: active-red-blue`。这是刻意设计的结构性冲突，不是本轮回归。019 已用「归档分支收口」处理，020 沿用同一收口方式。

### 隔离的诚实边界

subagent 的**上下文隔离是物理的**（独立进程、无共享记忆）；**文件系统是共享的**，允许读哪些文件靠指令约束 + 事后审计，不是沙箱。本轮实测出三个泄漏向量，见 `06_workflow_retrospective.md` §4.2。
