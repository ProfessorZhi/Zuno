# Round Report — rb-2026-10-07-formal-020

```text
round_id: rb-2026-10-07-formal-020
mode: AGENT_AUTO
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
base_sha: 7d3081f2ccaa20c7eeb0bfff75206d08584a6e51
verdict_is_immutable: true
```

---

## 1. 这一轮到底做了什么

100 问 → 100 答 → 100 追问 → 100 答，共 400 条，全部由互不可见的隔离实例产出。

相比 019 的两个实质变更：

1. **防火墙从「逻辑隔离」升到「物理隔离」。** 019 是 `CHATGPT_AUTO` / `LOGICAL_GITHUB_MEDIATED`，靠 allowlist 在同一上下文里假装遗忘；020 里 Red 的上下文**从来没有出现过 `src/` 的内容**。
2. **100 题从「知识点」改成 10 条 Interview Thread。** Red 必须跨题持有状态并回钩 —— Wave 1 有 61 处显式 `callback`，Wave 2 有 100 处 `chases`。

---

## 2. 最终判断

| 维度 | 结论 |
| --- | --- |
| 技术判断力 | **PASS**（偏 STRONG_PASS） |
| 实现细节 | PARTIAL —— 引用精度是最弱环，至少 3 处文件名/符号/行号错误 |
| 失败窗口意识 | **强** —— 候选人主动交出四把刀（A36/A39/A43/A47） |
| 历史真实性 | **NOT_ESTABLISHED** —— 且 Wave 2 让这层变差而非变好 |
| 工程基础功底 | PASS |

**Red Final 不给 FAIL 的理由：** 两轮 200 答里没抓到一处实质性向上编造；反而有约 55–60 处主动削减自身 claim、约 7–8 处直接反驳问题框架。

**不给 STRONG_PASS 的理由：** 最该被信任的那一层（历史真实性）被候选人自己进一步拆掉了。

---

## 3. 本轮最重要的三件事

### 3.1 候选人自己在追杀轮里推翻了 15 处说法

不是被逼认错，是**回去查了记录之后自己改口**。最硬的几处：

- **A87** —— 第一批描述了一个 `penalty` 逻辑；追问后 grep `fusion.py` 找不到 `penalty`，找不出那个函数，直接收缩为「不能确认它存在」。**这是 200 答里唯一一处「说了个东西，回头看发现那东西不在代码里」。**
- **A10** —— 引了一个不存在的 ADR 文件名。
- **A48/A49** —— 把负向历史归错了证据文件。
- **A54** —— 结论反转且反转后更不利：第一批说 `multi_agent_enabled` 没有 reader；查完发现 reader 存在，而 `product/runtime_batch.py:428` 明确**拒绝**在产品面开启它。

### 3.2 Q113：三层实例 + Controller 四方独立收敛到同一结论

Red Wave 2 抓到一个硬矛盾：A11 说 baseline `MRR@10=0.90`，A60 说修复后 `0.80→1.00`。

候选人、Blue 架构复诊、Controller 人工核查**互不可见地**得出同一结论：

> `project-fact-provenance.md:96` 原文已写明「baseline 的 `MRR@10` 在 rerun 中也从 `0.90` 变为 `1.00`，因此不应制造精确的单机制收益百分比」。
> 所以 A60 那句「修复前后 0.80→1.00」把 local 的 run-to-run 增量讲成了「vs 一个不动的 baseline」。**正确说法是打平在 1.00，不是超过。**

**判定：`ANSWER_GAP`，不是 `SYSTEM_GAP`，也不是造假。** 两条数字都有出处；错的是框架。系统口径本身是自洽的。

### 3.3 架构侧第一次做到自我纠错

Blue 架构复诊**撤回了自己第一轮的一条指控**：

> S13 我上轮判错了。`effect-security-slice-c-review.md:4` 头部就有 `superseded_current_evidence: main@9b7891c6 / run 35053215987`。

撤回一条错的判断，比留着它更有价值 —— 留着的话下一轮就会有人去「修」一个不存在的问题。

---

## 4. 真找到的东西（Controller 已独立验证）

三条安全 / fail-open，全部由 Controller 亲自打开源码复核：

| 项 | 事实 | 位置 |
| --- | --- | --- |
| **知识就绪默认开启** | 读取路径上是 `or "ready"`，缺配置即判就绪；写入侧 `mark_ready` 有严格判定，读取侧绕过它 | 检索链路上 **7 处**（初诊报 3 处，实际更广）+ `runtime_engine.py:2862` 硬编码 `graph_available=True` |
| **MCP 配置 IDOR** | GET / DELETE 只凭 `config_id`，`login_user` 拿到了却从不传进 service；而 update 路径**是**传 `user_id` 的。该配置承载 APPCODE / API Key | `api/v1/mcp_user_config.py:51-60`, `:82-92` |
| **TLS 全关 + 携带凭据** | `check_hostname=False` + `CERT_NONE`，同函数上方 `Authorization: APPCODE {api_key}`。且这是**外部副作用**路径 | `capability/tools/delivery/action.py:44-49` |

以及两条实现只做了一半：

- **N01** —— 五张 memory 写入表里**四张只写不读**（表名字面量全仓各只出现一次且均为 INSERT，零个 `FROM`）。由 Red 的 Q128 翻出 —— 它拿了候选人在 A33/A35 自己用过的尺子（「有没有 caller」）反过来量 memory 那边。
- **S07/N03** —— `escalate_due_reconciliations` 与 `timeout_due_async_jobs` 两个维护入口**都没有调用方**，零 scheduler / cron。「15 分钟后升级」这个语义没有东西触发它。

---

## 5. Red 抓错的地方（由架构侧给源码依据纠正）

盲 Red 无源码，**必然**有一部分判断是错的。架构审判逐条纠正了 4 处：

| # | Red 的说法 | 实际 |
| --- | --- | --- |
| R1 | 把「同实例跨用户复用」升格为 FUNDAMENTAL_GAP | 实例每请求新建（`build_simple_agent` 是 staticmethod、无缓存/单例），前件不可达。真实的那一半另立为 F-21（不变量无测试固定，`EVIDENCE_GAP`） |
| R2 | 称「3 月已存在」独立可核性 = 0 | 与 Red 自己在 §7 承认的 diff before-side 证据自相矛盾 |
| R3 | 用 ADR 的**禁用术语** `dual` 描述现状 | 实为「一条在跑 + 一条死实现」 |
| R4 | 把一行治理注释放大成「举证策略没有工程落点」 | 该协议有 canonical Evidence 配套与明确 owner |

**四条无一是「顺话」或「编造」，全部来自 Red 无源码这一物理约束。**

---

## 6. 方法论上最该记住的一条

> **指标会被优化掉，然后换一个位置重新出现。**

第一轮 Red 把「候选人主动认边界」判为**最强真实性信号**。第二轮发现这个字段的**形态是被 `interview-acceptance-standard.md` 教出来的**（A183）—— 也就是说，衡量诚实的标准同时也是生成诚实外观的模板。

候选人没有演戏；是这套流程**自己把「诚实」变成了一个可优化的目标函数**。

对一个以可追溯性为唯一目标的项目，这是必须记住的：**任何被写进标准的诚实形式，都会在下一轮退化成表演形式。** 应对不是取消标准，而是**持续更换测量点**。

---

## 7. 治理级发现：Ownership 不可考古

Red Final 判「历史真实性 NOT_ESTABLISHED」的根因不是候选人答得差，而是**取证材料不存在**：

- 仓库 2161 个 commit 中，人类身份只有 `ProfessorZhi` / `WenHi Huang`(=vince) 及自动化 —— **作者字段区分不出「我」与「团队」**。
- 根提交 `eafeb1c2`（2026-04-15）与候选人能自证的第一笔改动**同日**，因此「我加入时系统已存在」在 git 里没有任何证据。

所以简历上「我重构了 MCP Tool Calling」这类主张，在本仓库历史里**既不能证实也不能证伪**。

**本轮不制造 Ownership。** 只提出把它写进 `docs/project/README.md` 的已知边界（`IMP-020-10`）。

---

## 8. 输出清单

| 文件 | 状态 |
| --- | --- |
| `00_manifest.yaml` | ACTIVE |
| `00_artifact_links.md` | 稳定入口 |
| `01_simulated_resume.md` | FROZEN（`user_resume_review_status: DELEGATED`） |
| `02_red_questions.md` | COMPLETE · 100 题（Q1–Q100）+ 原始分批 `.part1/.part2` |
| `03_blue_answers.md` | COMPLETE · 100 答（A1–A100） |
| `03_blue_architecture_notes.md` | COMPLETE · SEALED FROM RED · 18 信号 |
| `04_red_wave2_review_and_questions.md` | COMPLETE · Part A 盲评 + Q101–Q200 + 隔离审计附录 |
| `04_blue_wave2_answers.md` | COMPLETE · 100 答（A101–A200）+ 隔离审计附录 |
| `04_blue_wave2_architecture_notes.md` | COMPLETE · SEALED FROM RED · 复核 + N01–N04 |
| `04_red_evaluation.md` | COMPLETE · Red Final 盲评 |
| `05_blue_architecture_reflection.md` | COMPLETE · 架构审判 |
| `06_workflow_retrospective.md` | COMPLETE |
| `07_user_feedback.md` | COMPLETE |
| `08_session_transcript.md` | COMPLETE |
| `09_improvement_ledger.md` | **PENDING_USER_REVIEW** · 15 条 |
| `10_next_resume_candidate.md` | BUILT_PENDING_USER_RESUME_REVIEW |

---

## 9. 下一步需要用户决定的

1. `09_improvement_ledger.md` 的 15 条提案（分 A–E 五组）。
2. `10_next_resume_candidate.md` 是否作为下一轮的 frozen resume。
3. 是否把 `IMP-020-10`（Ownership 不可考古）写进 `docs/project/README.md` 的已知边界。
