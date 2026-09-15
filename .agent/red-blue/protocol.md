# Red / Blue Execution Protocol

本协议定义 Zuno Red / Blue 的机器执行规则。长期方法见 `docs/red-blue/README.md`。

## 目标

Red / Blue 的目标不是让 Blue 答赢一次模拟面试，也不是保护当前架构不被推翻。它是一条连续工程闭环：从真实可投递简历出发，用两轮 100 题 Red / Blue 压力暴露候选人表达、工程证据、文档、架构和实现中的断点，再把真正成立的缺陷送回对应 Owner。

```text
当前 Zuno Truth
→ 模拟简历
→ Red Wave 1：100 题
→ Blue Wave 1：100 答 + 封存架构初诊
→ Red Wave 2：先评价 Blue 1，再生成 100 个针对性追问
→ Blue Wave 2：100 答 + 封存架构复诊
→ Red Final Evaluation
→ Blue Final Architecture Reflection
→ Controller Workflow Retrospective
→ Round Report / Improvement Ledger
→ USER_IMPROVEMENT_REVIEW
→ approved Skill / Docs / Architecture / Implementation changes
→ Next Resume Candidate
→ 下一轮重新验证
```

当前架构只是 baseline。Single Agent、Multi-Agent、Supervisor/Specialist、Subgraph、Generic Host、Native Runtime、GraphRAG、Memory 等都可以保留、重构、外置或删除；复杂度必须由问题和测量推导。

Red / Blue 产物不拥有 Project History、Target Architecture、Module Truth、Current Evidence 或 Personal Ownership。正式事实始终回到 canonical owner。

## GitHub 是运行时状态总线

每个 stage 都遵守：

```text
read Round branch HEAD
→ verify stage + allowlist
→ read declared inputs
→ run exactly one stage
→ write artifact + manifest + transcript
→ commit
→ next actor re-read new HEAD
```

GitHub commit 是 commit barrier。聊天摘要、角色临时文本和未提交草稿不能跨阶段成为正式输入。

正式 Round 从固定 `main@zuno_base_sha` 创建独立 branch + Draft PR：

```text
red-blue/<round-id>
docs/red-blue/workspace/<round-id>/
```

每轮固定 `zuno_base_sha` 与 Skill 版本。轮末修改 Skill / Docs / Architecture 只能标记 `NEXT_ROUND_ONLY`；不得回头重新计算本轮 PASS/FAIL。

## 默认生命周期：BATCH_DUEL

```text
ROUND_INIT
→ BUILD_SIMULATED_RESUME
→ USER_RESUME_REVIEW
   ├─ APPROVE → FREEZE_RESUME
   ├─ REQUEST_REVISION → RESUME_REVISION → USER_RESUME_REVIEW
   └─ ABORT → CLOSE / SUPERSEDE
→ RED_WAVE_1
→ BATCH_CHECKPOINT_RED_1
→ BLUE_WAVE_1
→ BATCH_CHECKPOINT_BLUE_1
→ RED_WAVE_2
→ BATCH_CHECKPOINT_RED_2
→ BLUE_WAVE_2
→ BATCH_CHECKPOINT_BLUE_2
→ RED_EVALUATION
→ BLUE_ARCHITECTURE_REFLECTION
→ WORKFLOW_RETROSPECTIVE
→ IMPROVEMENT_SYNTHESIS
→ ROUND_REPORT
→ USER_IMPROVEMENT_REVIEW
   ├─ APPROVE / PARTIAL_APPROVE → APPLY_IMPROVEMENTS
   ├─ REQUEST_REVISION → IMPROVEMENT_REVISION
   └─ DEFER → record reason
→ ARCHITECTURE_REVISION / DOC_REVISION / SKILL_REVISION / IMPLEMENTATION_PLAN as approved
→ BUILD_NEXT_RESUME_CANDIDATE
→ USER_FEEDBACK_CAPTURE
→ CLOSE_AND_ARCHIVE
→ merge Round PR
→ next Round from new main HEAD
```

`BATCH_CHECKPOINT_*` 只要求把当前批次 GitHub 文档链接交给用户，不要求用户逐题回答。用户可以继续、要求重做该批、或中止。自动 Round 不再要求用户扮演候选人。

默认真正需要决策的用户 Gate 是：Resume 与 Improvement。若用户显式要求，也可以在任意 Batch Checkpoint 插入 review/revision。

## Resume Builder

Resume Builder 从固定 base SHA 读取 Project、Architecture、Modules、Evidence、selected provenance 和用户真实简历风格，生成 `01_simulated_resume.md`。

模拟简历必须像真实投递材料，不像 Evidence memo。默认 1 行项目简介、1 行技术栈、约 4–6 条高价值贡献。

```text
真实问题 → 本人动作 / 技术决策 → 机制 → 可验证结果
```

事实边界强制：Pilot ≠ Production；团队工作 ≠ Personal Ownership；Target ≠ Current；small smoke ≠ formal benchmark。

冻结 Resume 后，本轮所有 Red Evaluation 都针对同一版本。Resume 改动必须新建 Round 或显式 invalidate 后续产物。

## RED_WAVE_1：固定 100 题

Red Wave 1 正式输入只有：

```text
frozen 01_simulated_resume.md
target role / JD / interview stage
pinned .agent/red-blue/attack-model.md
model general technical knowledge
```

Red 不读取 Zuno docs / source / Evidence / Blue hidden answer key。

`02_red_questions.md` 必须包含 **恰好 100 个可回答问题**。100 是正式批次规模，不再只是离线 Pressure Suite。

问题按真实面试深挖逻辑覆盖：

- Ownership / before-after；
- 问题与最简单方案；
- 调用链、状态、数据结构、参数、算法；
- failure / retry / concurrency / timeout / stale result；
- test / metric / bad case / evidence；
- Build / Buy / Delete；
- Python / DB / network / IR / Agent fundamentals；
- 架构替代方案与退出条件。

每题仍坚持“一问一个主要意图”。100 题可以覆盖多条 Thread，但不能用 100 个同义句灌水。

完成后只向用户发布该文件链接，进入 `BATCH_CHECKPOINT_RED_1`。

## BLUE_WAVE_1：100 答 + 封存架构初诊

Blue Wave 1 读取：

```text
frozen Resume
02_red_questions.md
pinned defense-model.md
AGENTS.md
allowed canonical Project / Architecture / Modules / Decisions / Evidence / provenance @ zuno_base_sha
```

Blue 必须对 Red Wave 1 的 100 题逐题回答，顺序和题号一一对应。候选人口头回答写入 `03_blue_answers.md`。

同一 stage 还要生成 `03_blue_architecture_notes.md`。它不是候选人口头回答，而是 Blue 以架构 Reviewer 身份对这 100 个问题暴露出的系统断点做**初诊**：

```text
signal
source_check
Current / Target / Evidence / Unknown
is_answer_gap_or_system_gap
candidate_architecture_change
simpler_alternative
cost_and_exit_condition
classification
```

### 关键 Firewall

`03_blue_architecture_notes.md` 对后续 Red **封存**。

Red Wave 2 和 Red Final Evaluation 只能读取 `03_blue_answers.md`，不能读取 Blue 架构初诊、canonical docs 或 Evidence。否则 Red 会拿到隐藏答案，盲测失效。

Blue Wave 1 完成后只向用户发布 `03_blue_answers.md` 链接；架构初诊保存在 Round 中，留给最终 Blue Reflection。

## RED_WAVE_2：先评价 Blue 1，再给 100 个追问

Red Wave 2 输入：

```text
frozen Resume
02_red_questions.md
03_blue_answers.md
pinned attack-model.md
target / JD / stage
```

明确禁止：

```text
03_blue_architecture_notes.md
Zuno canonical docs / source / Evidence
Blue hidden source traces
```

Red Wave 2 输出 `04_red_wave2_review_and_questions.md`，必须分两部分。

### Part A — Blue Wave 1 Blind Evaluation

Red 以真实面试官视角评价第一批回答：

- 哪些 Claim 已可信；
- 哪些只有术语、缺实现；
- 哪些 Ownership 不清；
- 哪些数字 / Pilot / benchmark 可疑；
- 哪些 failure / fundamentals 暴露薄弱；
- 哪些回答自己产生了新的攻击 handle。

Red 可以说“作为面试官我不信”，不能宣布 Zuno Architecture Truth。

### Part B — Exactly 100 Targeted Follow-ups

紧接 Part A 生成 **恰好 100 个新问题**。这些题必须由 Blue Wave 1 的实际回答驱动，不得把第一批原题机械换词。

典型追杀关系：

```text
Blue 说 call-time config
→ 追并发隔离 / config version / retry consistency

Blue 说 baseline-preserving fusion
→ 追 threshold / tie-break / ablation / latency / query-class kill gate

Blue 说 APPROVED memory
→ 追 authority / bypass / revocation / TOCTOU / durable concurrency

Blue 说 Multi-Agent 可选
→ 追 Tool vs Subgraph vs Specialist / shared state / late result / failure owner / benchmark
```

完成后只向用户发布该文件链接。

## BLUE_WAVE_2：100 答 + 第二次架构复诊

Blue Wave 2 读取：

```text
frozen Resume
02_red_questions.md
03_blue_answers.md
04_red_wave2_review_and_questions.md
pinned defense-model.md
allowed canonical sources @ zuno_base_sha
```

为保持公平，Blue Wave 2 **不能读取 `03_blue_architecture_notes.md` 作为答题 coaching**。它只根据 Red 的公开评价/追问和 canonical truth 回答。

Blue 对 Red Wave 2 的 100 个问题逐题回答，写入 `04_blue_wave2_answers.md`。

同一 stage 另外写 `04_blue_wave2_architecture_notes.md`，继续记录架构复诊，但仍对 Red Final Evaluation 封存。

完成后只向用户发布 `04_blue_wave2_answers.md` 链接。

## RED_EVALUATION：最终盲评

Red Final Evaluation 读取：

```text
Frozen Resume
Red Wave 1 100 questions
Blue Wave 1 100 answers
Red Wave 2 blind review + 100 questions
Blue Wave 2 100 answers
pinned attack-model.md
```

不读取任何 Blue architecture notes、Zuno docs、source 或 Evidence。

`04_red_evaluation.md` 最终判断：

- 两轮后候选人是否可信；
- Blue 1 的缺口是否在 Blue 2 被真正解释，而不是话术补洞；
- Ownership / implementation / failure / evidence / fundamentals；
- Resume Claim 保留 / 降级 / 删除建议；
- Red 自己仍无法确认的部分。

Red Evaluation 不拥有 Architecture Truth。

## BLUE_ARCHITECTURE_REFLECTION：最终架构审判

Red Final Evaluation 提交以后，Blue Final Architecture Reflection 才读取：

```text
全部 Red / Blue 可观察产物
03_blue_architecture_notes.md
04_blue_wave2_architecture_notes.md
canonical Project / Architecture / Modules / Decisions / Evidence @ zuno_base_sha
```

`05_blue_architecture_reflection.md` 必须回答的不只是“文档够不够”，还包括：

1. 当前架构到底哪里真的有问题；
2. 简单方案是否已经够用；
3. 当前设计在哪个真实 failure / constraint 下失效；
4. Multi-Agent / Specialist / Subgraph / Generic Host / Native Runtime / 单体等替代方案哪一个更合理；
5. Architecture Owner / Authority / State / Contract / Recovery / Security 是否需要调整；
6. 哪些复杂度应该删除而不是继续扩展；
7. Current、Target、Evidence、Unknown 如何分开；
8. 要修改架构还缺什么 measurement / benchmark / experiment。

分类：

```text
SIMULATED_RESUME_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_ZUNO_CHANGE
```

只有 Owner、Authority、State、Contract、Recovery、Security 或 Build/Buy 因果本身不成立时，才进入 `ARCHITECTURE_GAP`。

## WORKFLOW_RETROSPECTIVE：Controller 审整个过程

`06_workflow_retrospective.md` 由 Controller 完成。它不是 Blue Architecture Reflection 的附录，而是对**模拟系统本身**做元审查。

### Resume Builder Reflection

- 简历是否给出了真正有技术含量、可连续追问的工程故事；
- 是否遗漏更强的个人贡献；
- 是否有可疑数字、模块清单或过度边界免责声明。

### Red Thinking Framework Reflection

不仅评价题目好不好，还评价 Red 的思考框架：

- 100 题是否围绕少数高价值 Claim 建立深度，而不是平均扫点；
- Red 2 是否真的听懂 Blue 1，还是只把 Pressure Suite 换词；
- Blind Evaluation 是否公平；
- 是否把 general technical knowledge 当成隐藏 Zuno 答案；
- Ownership、Failure、Build/Buy、Fundamentals、Evidence 的攻击顺序是否自然；
- 哪些 Red Skill 规则应该删除、加强或重新组织。

### Blue Thinking Framework Reflection

必须分别审 Blue 的“候选人回答框架”和“架构诊断框架”：

- 是否先识别问题属于 Historical Ownership / Current System / Target Design / Open Design / Fundamental；
- 是否有材料时讲不清、没材料时乱补；
- 是否过度防御，只会说 Unknown；
- 是否能从 failure 推导架构，而不是看到问题就新增对象；
- 是否尊重简单方案和删除条件；
- Blue 架构初诊是否污染了第二波候选人答案；
- 哪些 Defense / Architecture reasoning rules 应修改。

### Harness Reflection

- 两轮是否都严格 100 题 / 100 答；
- Red 2 是否只能看到 Blue 1 observable answers；
- Red Final 是否未看到 Blue architecture notes；
- commit barrier / pinned base / Skill 是否正确；
- Batch link checkpoint 是否按批次向用户暴露；
- artifact 是否足够复现整个过程；
- 是否有无意义 stage / gate / 重复工作。

Retrospective 不能修改本轮回答或 verdict。

## ROUND_REPORT 与 Improvement Ledger

`09_improvement_ledger.md` 汇总 Red Evaluation、Blue Final Reflection、Workflow Retrospective 和用户反馈。每条 finding 只有一个 primary owner：

```text
RESUME_GAP
RED_SKILL_GAP
BLUE_SKILL_GAP
HARNESS_GAP
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
IMPLEMENTATION_GAP
EVIDENCE_GAP
OWNERSHIP_GAP
FUNDAMENTAL_GAP
NO_CHANGE
```

每条至少记录：

```text
signal
source_artifacts
root_cause
primary_class
owner
proposed_change
evidence_needed
risk_if_changed
status: APPLY | DEFER | REJECT | NEEDS_OWNER_DECISION
change_effective_scope: NEXT_ROUND_ONLY
next_round_retest
```

同时生成 `09_round_report.md` 给用户阅读，回答：

```text
这一轮 Red 打出了什么
Blue 哪些回答经住了
候选人哪些地方仍薄弱
当前架构有哪些真实缺陷
哪些只是文档 / Evidence / Skill 缺口
建议怎么改架构
哪些复杂度反而应该删除
下一轮要复测什么
```

然后进入 `USER_IMPROVEMENT_REVIEW`。

## Apply：真的允许修改架构

用户批准后，Finding 按 Owner 落地：

- Resume → 下一轮 Resume Candidate；
- Red / Blue Skill → `.agent/red-blue/`；
- Harness → Protocol / Templates / Validators；
- Narrative / Docs → canonical documentation owner；
- Architecture → `docs/architecture/` / `docs/modules/` / ADR；
- Implementation → 进入明确 implementation plan / program；
- Evidence → 增加 test / trace / eval / benchmark；
- Ownership → 恢复 provenance，而不是改措辞伪装。

Architecture Revision 必须解释：问题、最简单方案、当前方案哪里失败、新方案、增加成本、退出条件和 Measurement Needed。Multi-Agent 不是默认升级路线。

架构 / 文档 / Skill 改完必须先验证，再生成 `10_next_resume_candidate.md`。下一轮从新的 exact main HEAD 重建 / 校验 Resume。

## Context Firewall

### CHATGPT_AUTO

```text
firewall_strength: LOGICAL_GITHUB_MEDIATED
strict_blind_red_certification: false
```

同一 ChatGPT 对话不能证明物理遗忘，但必须通过 GitHub allowlist 模拟 Red blind。

### AGENT_AUTO

```text
firewall_strength: PHYSICAL_CONTEXT_ISOLATION
strict_blind_red_certification: true
```

## LIVE_INTERVIEW：可选模式，不是自动 Round 默认

若用户明确要求真人逐题模拟，可启用 `LIVE_INTERVIEW`。其规则继续是：

```text
RED_TURN question commit
→ BLUE_TURN answer commit
→ RED_TURN follow-up commit
→ BLUE_TURN answer commit
```

Red question commit 必须先于对应 Blue answer commit；Blue answer commit 必须先于下一 Red follow-up commit。`LIVE_INTERVIEW` 下仍要求一个问题一个主要意图。

自动架构校准 Round 默认使用 `BATCH_DUEL`，不能再要求用户逐题扮演候选人。

## Round Core Artifacts

旧的 11 个 core artifact 保持兼容：

```text
00_manifest.yaml
01_simulated_resume.md
02_red_questions.md
03_blue_answers.md
04_red_evaluation.md
05_blue_architecture_reflection.md
06_workflow_retrospective.md
07_user_feedback.md
08_session_transcript.md
09_improvement_ledger.md
10_next_resume_candidate.md
```

BATCH_DUEL 额外要求：

```text
03_blue_architecture_notes.md
04_red_wave2_review_and_questions.md
04_blue_wave2_answers.md
04_blue_wave2_architecture_notes.md
09_round_report.md
```

所有 artifact 只保存 observable role I/O、GitHub refs、classification、decision 和用户 intervention；不保存或伪造模型私有 chain-of-thought。