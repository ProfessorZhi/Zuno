# Round 020 Artifact Links

Round: `rb-2026-10-07-formal-020`
State: `ACTIVE`
Base: `7d3081f2ccaa20c7eeb0bfff75206d08584a6e51`（= 当前 `main` HEAD）
Branch: `red-blue/rb-2026-10-07-formal-020`

本页是本轮稳定入口。所有正式 artifact 使用固定路径，完成后原地更新。

| 项 | 值 |
| --- | --- |
| `mode` | `AGENT_AUTO` |
| `firewall_strength` | `PHYSICAL_CONTEXT_ISOLATION` |
| `strict_blind_red_certification` | `true` |
| Interview Threads | 10（见 `00_manifest.yaml` → `thread_taxonomy`） |
| Wave 规模 | 100 问 / 100 答 × 2 波 |

## Resume

- [01_simulated_resume.md](01_simulated_resume.md) — `FROZEN`（`user_resume_review_status: DELEGATED`）
- [10_next_resume_candidate.md](10_next_resume_candidate.md) — `NOT_STARTED`

## Red

- [02_red_questions.md](02_red_questions.md) — `NOT_STARTED`
- [04_red_wave2_review_and_questions.md](04_red_wave2_review_and_questions.md) — `NOT_STARTED`
- [04_red_evaluation.md](04_red_evaluation.md) — `NOT_STARTED`

## Blue — Candidate Answers

- [03_blue_answers.md](03_blue_answers.md) — `NOT_STARTED`
- [04_blue_wave2_answers.md](04_blue_wave2_answers.md) — `NOT_STARTED`

## Blue — Sealed Architecture Review

- [03_blue_architecture_notes.md](03_blue_architecture_notes.md) — `NOT_STARTED / SEALED_FROM_RED`
- [04_blue_wave2_architecture_notes.md](04_blue_wave2_architecture_notes.md) — `NOT_STARTED / SEALED_FROM_RED`
- [05_blue_architecture_reflection.md](05_blue_architecture_reflection.md) — `NOT_STARTED`

## Controller / Improvement

- [06_workflow_retrospective.md](06_workflow_retrospective.md) — `NOT_STARTED`
- [07_user_feedback.md](07_user_feedback.md) — `NOT_STARTED`
- [08_session_transcript.md](08_session_transcript.md) — `NOT_STARTED`
- [09_improvement_ledger.md](09_improvement_ledger.md) — `NOT_STARTED`
- [09_round_report.md](09_round_report.md) — `NOT_STARTED`
- [00_manifest.yaml](00_manifest.yaml) — `ACTIVE`

---

## Controller notes（Red 不可读）

### Resume boundary declaration

本节的约束来自 019 的 improvement ledger 与 `docs/governance/interview-acceptance-standard.md`，用于防止简历、面试回答与架构互相漂移。**它不进入简历正文**，Red Wave 1 只读 `01_simulated_resume.md`，不得读本页。

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行（`docs/evidence/current-eval-baseline.md` 为 `MEASUREMENT_BLOCKED`）；已记录的只是 regression 修复与 baseline 保持。冻结协议见 `docs/governance/rb019-graphrag-ablation-protocol.md`。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 这些当前全部是 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）；总体架构与九模块文档是后续系统化整理的产物，不能倒推为加入时的历史 Ownership。

**可以写，且经得起追问：** Tool/MCP binding、config injection、route boundary、GraphRAG baseline-preserving fusion、seed expansion / alias / path ranking、Context/Memory V2 与 readback 收紧，都有公开提交链支撑。追问到「有没有 holdout」时，正确回答是：没有，测量当前 blocked，因此只是 regression 修复。

### Gate 说明

- `resume_review_gate: DELEGATED` —— 用户 2026-10-07 指示「你来进行一轮红蓝队对攻迭代」，Resume Gate 由 Controller 在委托下代行；用户仍可要求 `RESUME_REVISION` 并重跑本波。
- `improvement_review_gate: REQUIRED` —— 本轮 improvement ledger 不自动应用，必须回到用户面前。

### 已知结构性冲突

active round 分支的 Draft PR **无法**通过 `tests/repo/test_docs_entrypoints.py`：该测试要求 `.agent/red-blue/current.md` 为 `state: no-active`，而 active round 必然是 `state: active-red-blue`。这是刻意设计的结构性冲突，不是本轮回归。019 已用「归档分支收口」处理，020 沿用同一收口方式。
