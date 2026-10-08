# Round 021 Artifact Links

Round: `rb-2026-10-08-formal-021`
State: `ACTIVE` — 本轮进行中
Base: `cdd2063b341e6919fafaa1395d1f3bdc837329f6`
Branch: `red-blue/rb-2026-10-08-formal-021` · PR [#282](https://github.com/ProfessorZhi/Zuno/pull/282)

> **本轮 base 的由来**：round 020 只批准了 A 组三条 P0（`IMP-020-01/02/03`）。这三条已在 `PR #281`
> 落地（merge commit `cdd2063b`），`main` 因此前进到本轮的 `zuno_base_sha`。也就是说本轮跑在
> **已经修掉那三条缺陷的树**上 —— 这是 round 020 刻意避免「base 落后 main ⇒ Red 重新发现已落地改动」
> 那个失败模式的做法。

| 项 | 值 |
| --- | --- |
| `mode` | `AGENT_AUTO` |
| `firewall_strength` | `PHYSICAL_CONTEXT_ISOLATION` |
| `strict_blind_red_certification` | `true` |
| Interview Threads | 10（与 020 相同，taxonomy 未改） |
| Wave 规模 | 100 问 / 100 答 × 2 波（共 400 条） |
| `resume_review_gate` | `DELEGATED`（用户 2026-10-08 委托 Controller 代行） |
| `improvement_review_gate` | `REQUIRED`（未过） |

## Resume

- [01_simulated_resume.md](01_simulated_resume.md) — `FROZEN`（against `cdd2063b`，Resume Gate 委托下批准）
- [10_next_resume_candidate.md](10_next_resume_candidate.md) — `NOT_STARTED`

## Red

- [02_red_questions.md](02_red_questions.md) — `COMPLETE`（100 题，两个互不可见实例拼接）
- [04_red_wave2_review_and_questions.md](04_red_wave2_review_and_questions.md) — `COMPLETE`（Part A 盲评 7 节 + Q101–Q200）
- [04_red_evaluation.md](04_red_evaluation.md) — `COMPLETE`（盲评总判 PARTIAL；15 findings）

## Blue — Candidate Answers

- [03_blue_answers.md](03_blue_answers.md) — `COMPLETE`（A1–A100）
- [04_blue_wave2_answers.md](04_blue_wave2_answers.md) — `ANSWERS_COMPLETE`（A101–A200，两实例拼接；18 处撤回 / 修正）

## Blue — Sealed Architecture Review

- [03_blue_architecture_notes.md](03_blue_architecture_notes.md) — `COMPLETE / SEALED_FROM_RED`（15 findings）
- [04_blue_wave2_architecture_notes.md](04_blue_wave2_architecture_notes.md) — `COMPLETE / SEALED_FROM_RED`（复诊差分：维持 12 / 降级 2 / 升级 1 / 新增 5）
- [05_blue_architecture_reflection.md](05_blue_architecture_reflection.md) — `COMPLETE`（ARCHITECTURE_GAP = 1，仅 F-01）

## Controller

- [06_workflow_retrospective.md](06_workflow_retrospective.md) — `COMPLETE`（5 项审查，10 提案）
- [07_user_feedback.md](07_user_feedback.md) — `NOT_STARTED`
- [08_session_transcript.md](08_session_transcript.md) — `NOT_STARTED`
- [09_improvement_ledger.md](09_improvement_ledger.md) — `DRAFT_REVIEW`（20 条提案，未应用）
- [09_round_report.md](09_round_report.md) — `COMPLETE`
- [00_manifest.yaml](00_manifest.yaml) — `ACTIVE`

---

## Controller notes（Red 不可读）

### Resume boundary declaration

约束继承自 round 020 的 improvement ledger 与 `docs/governance/interview-acceptance-standard.md §3`。
**Red Wave 1 只读 `01_simulated_resume.md`，不得读本页。**

**明确不写：**

- **不写 GraphRAG「效果提升 / 多跳检索更准」。** 独立 holdout 与 leave-one-out ablation 尚未执行，
  冻结协议见 `docs/governance/rb019-graphrag-ablation-protocol.md`（状态 `BLOCKED_PENDING_DATA`）。
  注意：`docs/evidence/current-eval-baseline.md` 的 `MEASUREMENT_BLOCKED` 是**整个 eval 层**的状态（成因是缺外部
  benchmark 数据），不是 GraphRAG 专属；不要把全局状态收窄成 GraphRAG 结论。已记录的只是 regression 修复与 baseline 保持。
- **不写任何 run-to-run 百分比。** `docs/governance/project-fact-provenance.md:96` 明确写着 baseline 的 `MRR@10` 在同日 rerun 中也从
  `0.90` 变为 `1.00`，因此「修复前后」框架在本样本上不成立。正确说法是 local 与 baseline **打平**。
- **不写 Production、规模、QPS、Latency、Cost、法院数量、用户量、准确率或任何收益数字。** 全部为 Unknown / Measurement Needed。
- **不写「我设计了整个 Agent Runtime / 整个 GraphRAG / 全部后端」。** 加入项目时系统已存在（约 2026.03，非 Greenfield）。
- **不写任何无法取证的 Personal Ownership。** 见 `docs/project/README.md`「团队与个人参与的边界」（由 `IMP-020-10` 写入）。

**可以写，且经得起追问：** Tool/MCP binding、config injection、route boundary、GraphRAG baseline-preserving fusion、
seed expansion / alias / path ranking、Context/Memory V2 与 readback 收紧，都有公开提交链支撑。

### IMP-020-09 处置记录（Resume Gate 委托下的代行决定）

本轮 frozen resume 直接采用 round 020 的 `10_next_resume_candidate.md` 正文，逐字未改。五条处置：
**保留 1 条**（第 2 条，附两条硬上限：不得声称「效果提升」、不得制造 run-to-run 百分比）、
**降级改写 4 条**（第 1/3/4/5 条，漂的是动词强度不是事实）、**删除 0 条**。

`IMP-020-09` 因此在本轮 Resume Gate 处**已消费**，不再计入 `still_open`。

**本段不进入 `01_simulated_resume.md`**：告诉 Red「这些 bullet 是刻意弱化过的」等于给 Red 发路标，
会污染 Wave 1 的 blind baseline。Resume 文件必须是一份干净的简历。

### Resume Gate 前的独立取证核验（Controller 记录）

Resume 冻结前，由**一个隔离 subagent** 在 base `cdd2063b` 上对候选简历的 5 条 bullet 与 3 条边界主张
逐条回溯到 canonical 源（`docs/governance/project-fact-provenance.md`、`src/backend/**`、`tests/**`），
并对每条给出 `SUPPORTED / PARTIALLY_SUPPORTED / NOT_SUPPORTED`。结论：**5 条 bullet 全部有 commit / 测试 / 台账支撑，
但 3 处措辞证不到**，已当场改掉：

| # | 原措辞 | 核验结果 | 改后 |
| --- | --- | --- | --- |
| B1 | 「复杂或**参数不完整**任务回落 ReAct」 | `NOT_SUPPORTED` —— 参数不全的工具体走产品侧 `_plan_tool_creation_flow` 的 `mode="ask"` 补参流程，不是回落 ReAct；能证的只有 `_plan_kind_for` 返回 `simple`/`complex` | 删掉「参数不完整」，改为「复杂请求进入 ReAct 路径」 |
| B1 | 「ReAct **回落**侧暂无回归断言」 | `SUPPORTED`（全量 grep 无任何断言 workspace 请求回落 ReAct 的测试） | 「回落」→「一侧」，与上一条解耦 |
| B3 | 「上述改动**在 5-query smoke 上验证**」 | `PARTIALLY_SUPPORTED` —— 每个机制另有单元测试（`tests/graphrag/*`），原句反向地过窄 | 补「每个机制有单元测试，但质量收益目前只在 5-query smoke 上观察到」 |
| B4 | 「接入……和**一个轻量 ContextOrchestrator**」 | `SUPPORTED`，但 `ContextOrchestrator.prepare` 在 `src/` 内**无生产调用点**（只有 re-export）；真实生产路径是 `build_context` 节点 → `build_context_pack(scope=…)` | 把 ContextOrchestrator 降为 **typed contract 层**，不再暗示它是运行时装配器 |

**核验确认但仍留在简历里的既有缺口（不是错误陈述，是已知不足）：**

- `ContextOrchestrator.prepare` 无生产调用点（同上）。
- Memory 的「同 scope」保护**没有跨 scope 泄漏的负向测试**；focused tests 覆盖的是过滤逻辑，不是泄漏隔离（与 round 020
  `04_red_evaluation.md` 的 A130 一致）。
- GraphRAG 的具体点名与 rerun 数字全部来自 `project-fact-provenance.md` 台账转述，**仓库内没有可复核的 raw runtime
  report**（该路径 gitignored）。
- `docs/project/README.md:150`「团队与个人参与的边界」确认存在，`IMP-020-10` 的取证缺口（commit 作者字段区分不出「我」与「团队」）依然成立。

**核验 subagent 的一处自身错误（留给 `06_workflow_retrospective.md`）：** 它报告「base `cdd2063b` 在本仓库不存在、
`git rev-parse` 返回 unknown revision」。Controller 复核：`git cat-file -t cdd2063b341e…` → `commit`，
且它同时等于 `origin/main` 与本 round 分支的 merge-base。**该 base 有效，manifest 无需修改。**
subagent 的 git 命令是在非仓库 cwd 下执行的 —— 这是 Harness 侧的 cwd 传递缺陷，不是仓库状态问题。

### ⚠️ Resume Gate 自身引入的一处错误（本轮发现，NEXT_ROUND_ONLY，不回写 frozen resume）

**这条要记在 Resume Builder 头上 —— 是 Controller 自己在 Resume Gate 改出来的。**

Blue Wave 1 的 **A56** 指出：`complex` 分支需要一个注入的 DAG planner。Controller 独立复核确认：

- `src/backend/zuno/main.py:113` —— 产品装配处 `dynamic_dag_planner=None`。
- `src/backend/zuno/platform/services/workspace/single_controller_runtime.py:818` —— `elif complex_unbound:`
  → `admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND`，紧邻注释明确写着 unbound 组合
  **「must never fake a fixed three-step DAG or fall back to a direct answer」**。

⇒ 在该产品组合下，**复杂请求是在规划准入处 fail closed 被拦下，而不是「进入 ReAct 路径」**。

而 `01_simulated_resume.md` 第 1 条现在写的正是「复杂请求进入 ReAct 路径」——
这是本 Controller 在 Resume Gate 把 round 020 的「复杂或参数不完整任务回落 ReAct」改写后的结果。
**改错了方向**：我依据的核验只证到 `_plan_kind_for` 会返回 `simple`/`complex` 这个**分类**存在，
没有继续查这个分类在**产品装配下**被谁消费。核验停在了「机制存在」而不是「机制被这样使用」。

**处置：不回写 frozen resume。** 本轮 frozen resume 与已完成的 Red/Blue 产物保持不动（verdict immutable）。
该条进入 `09_improvement_ledger.md`，并必须在 `10_next_resume_candidate.md` 里改成可复核措辞，例如
「复杂请求需要绑定动态规划器，未绑定时在准入处 fail closed」——具体措辞由下一轮 Resume Gate 连同核验一起定。

**这是一次「自我发现」而非外部发现**：A56 是 Blue 自己答出来的，Controller 只是把它追到了代码。因此它同时是
**Resume Builder 缺陷**与**取证深度缺陷**（Resume Gate 的核验清单缺一项：「这个机制在产品装配下真的被这样用了吗」）。

**Arch 初诊把它判成 `F-01`，并给出了更硬的一条证据 —— Controller 已独立复核，逐条成立：**

- `src/backend/zuno/platform/services/workspace/simple_agent.py:2150-2156` —— `_plan_kind_for()` 命中 token 表
  `("compare", "across", "conflict", "multi-hop", "multihop", "analyze", "synthesize", "报告")`
  中**任意一个**就返回 `"complex"`。**中文「报告」就在表里。**
- `single_controller_runtime.py:737-739` —— `complex_unbound = (plan_kind == "complex" and self._dynamic_dag_planner is None)`。
- `main.py:113` —— 产品装配 `dynamic_dag_planner=None`。
- `single_controller_runtime.py:814-818` —— `elif complex_unbound:` → `admission_reason = DYNAMIC_PLAN_RUNTIME_NOT_BOUND`。

⇒ 在 shipped composition 下，**任何含「报告」（或 compare / analyze / multi-hop…）的普通 workspace 请求都会被准入拦下**，
且注释明确禁止回落。这不只是「简历措辞错」，而是**简历 / 架构描述 / 代码三方互斥**的架构缺口（Arch 判为 F-01，
本轮唯一确认的 `ARCHITECTURE_GAP`）。

**Blue 自身两处引用问题（Controller 复核后的精确版，与 Arch §14 的转述有出入）：**

- **动作错（成立）**：`A8` / `A56` 把 `single_controller_runtime.py:497-501` 说成「抛」`DYNAMIC_PLAN_RUNTIME_NOT_BOUND`。
  实际该处是 `build_workspace_plan_steps` 的 **`return None`**；全文件**不存在** `raise DYNAMIC_PLAN_RUNTIME_NOT_BOUND`，
  真正的 fail-closed 是 `:737-739` 判 `complex_unbound` → `:814-818` 置常量 → `:825` `_blocked_request`。
- **目录错（不成立，是 Blue-2 记错自己的错）**：Arch §14 说 A8/A56 把该文件「写成在 `agent/runtime/execution/` 下」。
  Controller 逐行核对：`03_blue_answers.md` 的 A8（`:121`/`:125`）与 A56（`:798`）**根本没写目录**，只写了
  `single_controller_runtime.py:497-501` —— 属**欠指定**，不是写错目录。`agent/runtime/execution/` 在该文件里
  只出现在 `:122`，指的是另一个文件 `react_runner.py`。「写成在 agent/runtime/execution/ 下」这个说法
  出处是 **Blue-2a 自述**（`04_blue_wave2_answers.md:21`），即它**误述了自己 Wave 1 的错误**。

⇒ 结论对（complex 在 shipped composition 下不可达），但「位置与动作都错」这句只有一半成立：**动作错，目录只是欠指定**。
这条「关于错误的错误」进 `06_workflow_retrospective.md`。

**本轮复现的泄漏向量：** Arch 实例自报对 `docs/` 做过一次跨目录 grep，输出顺带带回了
`docs/red-blue/rounds/**` 与本轮 workspace 其他文件的片段（声明未用作证据）。这是 `IMP-020-14` 记录的
泄漏向量在本轮的**再次复现** —— 记为观测事实，不当作已解决。

### Gate 说明

- `resume_review_gate: DELEGATED` —— 用户 2026-10-08 在「再来一轮」后选择「照 020 一样委托给我」，
  Resume Gate 由 Controller 在委托下代行；用户仍可要求 `RESUME_REVISION` 并重跑本波。
- `improvement_review_gate: REQUIRED（未过）` —— 本轮 improvement ledger **不自动应用**。

### 已知结构性冲突

active round 分支的 Draft PR **无法**通过 `tests/repo/test_docs_entrypoints.py`：该测试要求
`.agent/red-blue/current.md` 为 `state: no-active`，而 active round 必然是 `state: active-red-blue`。
这是刻意设计的结构性冲突，不是本轮回归。019 / 020 都用「归档分支收口」处理，本轮沿用同一方式：
workspace 移入 `docs/red-blue/rounds/`、`current.md` 复位为非激活后，CI 才应转绿。

### 隔离的诚实边界

subagent 的**上下文隔离是物理的**（独立 context、无共享记忆）；**文件系统是共享的**，
允许读哪些文件靠指令约束 + 事后审计，不是沙箱。round 020 已实测出三个泄漏向量
（见其 `06_workflow_retrospective.md §4.2`）并在 ledger 的 `IMP-020-14` 里给出修法；
该条尚未生效（Skill / Harness blob 与 020 相同），因此**本轮仍带同样的泄漏向量**。
