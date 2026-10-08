# Round Report — rb-2026-10-08-formal-021

```text
round_id: rb-2026-10-08-formal-021
mode: AGENT_AUTO / BATCH_DUEL
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
base_sha: cdd2063b341e6919fafaa1395d1f3bdc837329f6
branch: red-blue/rb-2026-10-08-formal-021
pr: 282
scale: 100 问 × 2 波 + 100 答 × 2 波 = 400 条
red_blind: true
improvement_review_gate: REQUIRED（未过）
```

---

## 1. 这一轮到底做了什么

在 base `cdd2063b`（= `main`，round 020 的三条 P0 安全修复已在 `PR #281` 落地）上，跑完一次完整的盲红蓝对局：

```text
Frozen Resume（Resume Gate 委托下批准）
→ Red Wave 1：100 题（两个互不可见实例，blind）
→ Blue Wave 1：100 答 + 封存初诊（15 findings）
→ Red Wave 2：盲评 7 节 + Q101–Q200
→ Blue Wave 2：100 答（A101–A200，18 处撤回/修正）+ 封存复诊（差分：维持 12 / 降级 2 / 升级 1 / 新增 5）
→ Red Final Evaluation（盲，总判 PARTIAL，15 findings）
→ Blue Architecture Reflection（判决：ARCHITECTURE_GAP 仅 1 条）
→ Workflow Retrospective（5 项审查，10 条提案）
```

Red 全程未读两份封存架构笔记与 canonical 源；Blue Wave 2 的 Candidate 未把封存笔记当 coaching。

---

## 2. 最终判断

**整轮：PARTIAL**（Red Final 盲判），**架构侧：1 条 `ARCHITECTURE_GAP`**（Blue Reflection 判决）。

本轮的验收标尺仍然是那条核心指令：**任何强 Claim 能否被追到 History / Ownership / 代码 / 失败窗口 /
Evidence / 和 Unknown**。按这条尺子：

- **没有任何一条强 Claim 是「只有形容词、落不到任何一档」的**（这是不给 FAIL 的理由）。
- **没有任何一条收益性 Claim 被建立**，而且「最可复核的一段」（06/08 控制面）**不归候选人**；
  他 ownership 内的三段（Tool/MCP、GraphRAG、Context/Memory）**收益全未证明**（这是不给 PASS 的理由）。
- **复杂度正当性一层：未建立。** 四层自研（GraphRAG、Memory V2 / ContextOrchestrator、Native Runtime、
  MCP 准入）的保留理由统一退化为「有单测、有设计、协议未跑」。

---

## 3. 本轮最重要的三件事

### 3.1 Q113：攻方最锋利的一击，被候选人用 commit 图驳回前提，然后**拒绝**接住胜利

Red Wave 2 的 Q113 攻的是整轮唯一一句「修复有效」：audit 若是 `qwen-plus`、rerun 若是 `deepseek-v4-flash`，
则 local 从 `Recall@5` 0.80 回到 1.00 就可能是**换模型**而非修复。

Blue 的回应分两步，**两步都对自己不利**：

1. **驳回前提**：`a25c95a2`（2026-06-20 15:12 "Align multihop eval profile with DeepSeek default"）
   把受版本管理 profile 的 `conversation_model` 由 `qwen-plus` 改为 `deepseek-v4-flash`，
   而它是 audit `7928df50`、rerun `3da5d742` 与输入 `c3d06da3` 的**共同祖先** ⇒ audit 与 rerun **同模型**。
   （Controller 已独立复核这条血缘链与那段 diff。）
2. **拒绝归因**：排除「换模型」之后，它**没有**顺势宣称「所以是 fusion 修复起作用」——
   因为 baseline 自身数字在同日 rerun 里也漂了（`MRR@10` 0.90→1.00、`Recall@2` 0.70→0.90、
   avg latency 12148.21→16064.76 ms），**不可分离**。

⇒ 一个只想赢的候选人会在第 1 步之后收工。**这一步是本轮最强的真实性信号**，
并且与本轮边界声明「local 与 baseline 打平」完全一致。

### 3.2 Resume Gate 抓出了**自己**的一处方向错误

`01_simulated_resume.md` 第 1 条现写「复杂请求进入 ReAct 路径」——**这句是错的**，
是本 Controller 在 Resume Gate 上把 round 020 的「复杂或参数不完整任务回落 ReAct」改写出来的。

- **错在哪**：核验只证到 `_plan_kind_for` 的 `simple`/`complex` 分类**存在**，
  没继续查它在**产品装配下**被谁消费。核验停在「机制存在」，没走到「机制被这样使用」。
- **实际是什么**：`main.py:113` `dynamic_dag_planner=None` ⇒ 复杂请求在**准入处 fail closed**，不进入 ReAct。
- **谁发现的**：不是外部。Blue Wave 1 的 **A56** 自己答出来的，Controller 追到代码才确认。

**处置：不回写 frozen resume（verdict immutable）。** 该条进入 ledger（`IMP-021-08` / `G-08`），
并必须由下一轮 Resume Gate 改成可复核措辞。同时记为 **Resume Builder 缺陷** + **取证深度缺陷**，
产出提案 `IMP-021-11`（核验清单新增「装配侧确认」）。

### 3.3 架构侧这一轮做的是**减法**，而且交叉验证成立

- 唯一 `ARCHITECTURE_GAP` 仍是 `F-01`，但 Current 更精确：拦截**不抛异常**，而是产出一个
  `plan_steps=()` 的**正常请求** ⇒ 形成「有 entrant、无 Plan」的 run，**字面违反**
  `docs/modules/reference.md:237`「Native Runtime entrant 一定有 Plan」。（Controller 独立复核成立。）
- Wave 2 复诊把 Wave 1 自己的 `F-06`（conditional `ARCHITECTURE_GAP`）**主动降级**；
  条件性集合清零；`F-11/F-13/F-14/F-15` 明确**不升级**。
- `Multi-Agent` 的结论是**不值得（今天）**：当前失败是「准入无 owner」，不是「单 Agent 做不动」，零 measured constraint。
- **交叉验证**：Red Final 是**盲**的，Blue Reflection **有源码**。两者独立收敛到同一批缺陷
  （guardrail 覆盖 baseline 下限、命名组件无生产调用方、仓内 RRF 未用、准入无 ADR）；
  而 Reflection 独立回源码核出 Red Final **2 处过强表述**（`RF-01`/`RF-02`），并闭合它 2 个保留的未知（均指向 Blue 正确）。

---

## 4. 真找到的东西（Controller 已独立验证，`file:line` 可复核）

| # | 事实 | 证据 |
| --- | --- | --- |
| 1 | 复杂请求在 shipped composition 下准入 fail closed，**不进入 ReAct** | `simple_agent.py:2150-2156`；`main.py:113`；`single_controller_runtime.py:737-739/814-818/825` |
| 2 | 拦截产出**空 plan 的 run**（不是异常） | `single_controller_runtime.py:870-911`（`plan_steps=()` / `capability_ids=()` / `decision:"block"`）；`:497-499` `return None`（全文件无 `raise DYNAMIC_PLAN_RUNTIME_NOT_BOUND`） |
| 3 | 该 run 违反已接受的架构不变量 | `docs/modules/reference.md:237` |
| 4 | `DeleteRestoreRuntime` 无生产调用点 | `PersistentDeleteRestoreCoordinator` 在 `src/` 零构造点；调用者仅测试 |
| 5 | `mcp_user_config` 没有 cache，每次调用直查库 | `api/services/mcp_user_config.py:141` → `dao/mcp_user_config.py:63`；全文件无 cache 关键字 |
| 6 | `resolve_alias` 的 `allow_fuzzy` 分支是**死代码** | `platform/services/graphrag/entity_alias.py:35-61`（该循环的相等判定已在上面返回） |
| 7 | fusion 是图层护栏；`baseline-preserving` **不是**全局不变量 | `platform/services/retrieval/fusion.py:922`（`selected[weakest_index] = candidate`）、`:943`（`floor_preserved = promoted_candidate is None`） |
| 8 | 幂等 key 是 `{run_id}:{step_run_id}:{tool_name}:{salt}`，`salt` **确定** | `capability/mcp/mcp_tool_executor_adapter.py:70-73`；`simple_agent.py:216-218` |
| 9 | audit 与 rerun **同模型**（换模型发生在更早的 smoke） | `a25c95a2` 为 `7928df50` / `3da5d742` / `c3d06da3` 的共同祖先 |
| 10 | `fusion_score` 只写 metadata、不进 `_rank_key` 返回元组（trace-only） | `fusion.py:968-977` |

---

## 5. Red 抓错的地方（由架构侧给源码依据纠正）

Red Final 是**盲**的，且它**自己声明**（`04_red_evaluation.md:262`）所有 `file:line` 判断都是**结构判断**、未核源码。
因此它的偏差**几乎全是「过度精确」，不是凭空错误**：

| ID | Red Final 说 | 实际 | 依据 |
| --- | --- | --- | --- |
| `RF-01` | 简历第 4 条靠「一个**不存在的对象**」支撑 | 过强。`prepare_context` **作为符号存在** | `agent/harness.py:9`/`:269`；`agent/durable_runtime.py:416`；`agent/post_turn.py:43`。真错的是**归属**（不是 live 方法），不是存在性 |
| `RF-02` | A8/A56 有「**两处**硬错」 | 只有**一处**（动作错：`:497-501` 的 `return None` 被说成「抛」）。「目录」只是**欠指定** —— Wave 1 根本没写目录 | `03_blue_answers.md:121`/`:125`/`:798`。且「写成在 `agent/runtime/execution/` 下」出自 **Blue-2 自己**对自己 Wave 1 错误的**误述**（`04_blue_wave2_answers.md:21`） |

**它主动保留、本轮被闭合的 2 个未知**（方向皆指向 Blue 正确，不计为判错）：
① `{salt}` 是否确定 —— 确定；② `final_top5_floor_preserved` 是否存在 —— 存在（`fusion.py:888/948/943/1037`）。

**注：`RF-02` 与 Controller 在 `00_artifact_links.md` 的独立结论一致** —— 两个互不可见的执行者从同一源码得出同一判定。

---

## 6. 方法论上最该记住的一条

> **元层（对缺陷的描述、自我修正、状态总线产物）和对象层一样会错，而且没有任何东西会替你发现它。**

本轮三个实例，各自属于一层，全部由**回源码/回文件**才抓到：

1. **状态总线坏了没人知道**：`00_manifest.yaml` 从 `red_wave_1` 起就是**非法 YAML**
   （未加引号的 `git log --grep "^rb-021: ..."` 含 `: `），跨多个 stage commit 无校验。
   已核实 `718c8524`、`957e8114` 两个提交上**都解析失败**。提案 `IMP-021-14`。
2. **对缺陷的描述本身是错的**：Arch §14 把 A8/A56 的错转述成「写成在 `agent/runtime/execution/` 下」，
   Controller 一度把它当事实写进记录，直到逐行核对才发现 Wave 1 **根本没写目录**。（见 §5 `RF-02`）
3. **自我修正也不可信**：Blue-2 对自己 Wave 1 错误的复述**又是错的**（同上）。提案 `IMP-021-13`。

⇒ **「一条关于错误的陈述」和「一条自我修正」都必须回源码核**，不能因为它是元层就采信。
这条比本轮任何单条技术发现都更可迁移。

---

## 7. 治理级发现

**本轮的 Resume Gate 错误是第一次由 Controller 自己的产物变成 round finding。**
它没有造成任何「结论漂移」（frozen resume 未回写、verdict 未重算），但它证明：
**Resume Builder 的核验清单有结构性缺口**（缺「装配侧确认」），而这个缺口**不会由外部攻方发现**——
Blue 是在正常答题时顺手答出来的。⇒ Resume Builder 必须自带装配侧核验（`IMP-021-11`）。

第二条：**隔离的诚实边界仍然只是自我申报**。本轮观测到 **3 次**泄漏向量
（Wave 1 Arch 跨目录 grep、Wave 2 Arch 跨目录 grep、**新形态**——允许文件正文里字面列出封存件文件名），
全部自报、无一由沙箱发现。`IMP-020-14` 尚未生效，本轮按原样带病运行，**不当作已解决**。

---

## 8. 输出清单

| 产物 | 状态 | 提交 |
| --- | --- | --- |
| `01_simulated_resume.md` | FROZEN | `bcd00a61` |
| `02_red_questions.md` | COMPLETE（100） | `97bdd0db` |
| `03_blue_answers.md` | COMPLETE（100） | `28e4661e` |
| `03_blue_architecture_notes.md` | COMPLETE / SEALED（15 findings） | `28e4661e` |
| `04_red_wave2_review_and_questions.md` | COMPLETE（盲评 + Q101–Q200） | `718c8524` |
| `04_blue_wave2_answers.md` | COMPLETE（A101–A200） | `957e8114` |
| `04_blue_wave2_architecture_notes.md` | COMPLETE / SEALED（差分） | `b95e00fc` |
| `04_red_evaluation.md` | COMPLETE（PARTIAL） | `144ba412` |
| `05_blue_architecture_reflection.md` | COMPLETE（ARCHITECTURE_GAP = 1） | `52eac169` |
| `06_workflow_retrospective.md` | COMPLETE（5 项审查，10 提案） | `52eac169` |
| `09_improvement_ledger.md` | DRAFT_REVIEW（20 条提案） | 本次提交 |
| `09_round_report.md` | 本文件 | 本次提交 |
| `00_manifest.yaml` / `00_artifact_links.md` / `.agent/red-blue/current.md` | 全阶段登记 | 见分支 log |

---

## 9. 下一步需要用户决定的

1. **`IMP-021-01`（唯一架构缺口）** 是否批准进 `docs/architecture/` + ADR ——
   即给 Workspace 准入边界一个 owner，并把「planner 未绑定时的复杂请求」定义为受控拒绝。
2. **`IMP-021-08` 的简历措辞处置**是否按 ledger 的表落地，尤其 `G-01` / `G-08`
   （第 1 条那句方向错的措辞，下一轮由 Resume Gate 连同核验一起改）。
3. **`IMP-021-11`..`IMP-021-19` 这 9 条 Skill / Harness 提案**是否授权修改 `.agent/red-blue/`
   （含 manifest validator、subagent `git -C`、产物形态校验、封存文件名不外泄等）。

> 以上均为提案；`improvement_review_gate: REQUIRED` 未过，本轮**不自动应用**任何一条。
> 本轮 verdict **不因** ledger 而重算（`current_round_verdict_recomputed: false`）。
