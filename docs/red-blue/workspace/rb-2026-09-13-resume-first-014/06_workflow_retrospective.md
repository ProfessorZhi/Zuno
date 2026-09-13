# Workflow Retrospective — rb-2026-09-13-resume-first-014

formal_input_head: 96330be334975a943c9b8d6c572499b914a68dcd
attack_skill: .agent/red-blue/attack-model.md@10869d9176d2ef34b46577478bba62d9e254158a
user_feedback: 07_user_feedback.md@96330be334975a943c9b8d6c572499b914a68dcd

## Verdict

**Red quality: PASS_WITH_REVISIONS**

Round #014 的 Red 已经跨过用户对旧方法最核心的否决点：问题不是从 Zuno 九模块或既知答案反推，而是从冻结简历的四条 Claim 出发；大量问题能落到函数、数据结构、算法、参数、并发、timeout、test assertion 和 baseline/ablation，最终确实暴露了 Blue 之前没有主动暴露的 implementation ownership 断点。

这轮最有价值的结果不是“问得更难”，而是 Red 问出了一个会改变决策的事实：**架构解释力已经明显强于历史个人实现的可复现程度。** 如果仍沿用旧 Reviewer-style 问法，这个断层很容易被完整的 Target Architecture 掩盖。

但这轮仍不能把 Red Skill 判成“完成”。100 问目前更像一套高质量压力题库，不像一场真实 45–60 分钟技术面试的动态问题路径；部分后半段问题在已经发现致命 ownership gap 后仍继续展开二阶设计假设，信息增益开始下降。

## User feedback considered

### UF-001 — GitHub-mediated single-chat workflow

**Resolved for this round.**

Round #014 全程使用独立 branch / Draft PR #226；Resume、Red Questions、Blue Answers、Red Evaluation、Blue Reflection 和本 Retrospective 都必须提交后再从新 HEAD 进入下一阶段。

仍然诚实保留：`CHATGPT_AUTO` 只有 `LOGICAL_GITHUB_MEDIATED`，不等于独立 Agent 的物理上下文隔离。因此本轮可以验证问题质量和流程自洽性，不能作为严格 blind-Red certification。

### UF-002 — Previous Red was unqualified

**Substantially resolved.**

用户要求的四个重点在本轮都实际出现：

- 精品思维：问题围绕高风险 Claim 分预算，不按九模块均摊；
- 全链路：Project reality → implementation → failure → evidence → fundamentals → delete condition；
- 不重复造轮子：Tool、GraphRAG、Memory、Native Runtime 都被问 Adopt / Extend / Delete；
- Implementation / Fundamentals：MCP config isolation、asyncio、TCP/HTTP timeout、idempotency、IR metrics、ranking、PostgreSQL isolation 都从项目自然下钻。

## Red quality score

| Dimension | Score | Judgment |
| --- | ---: | --- |
| Resume Grounding | 9.5/10 | 五条攻击链都能指回冻结简历，没有按 Zuno 内部模块均摊 |
| Technical Depth | 9.5/10 | 多次落到函数、mapping、matcher、算法、参数、test assertion |
| Full-chain Coverage | 9.0/10 | 业务、baseline、实现、故障、证据、基础、删除条件均覆盖 |
| Non-duplication | 8.5/10 | 大部分是深度阶梯；少量 Pilot / route / algorithm 边界存在可压缩重叠 |
| Build/Buy Skepticism | 9.5/10 | Q040/Q064/Q085/Q093/Q100 能真正要求删除自研复杂度 |
| Failure Pressure | 9.5/10 | side effect timeout、fallback duplicate、cancel、stale memory、index drift 都不是 Happy Path |
| Fundamentals Drilldown | 9.0/10 | 基础题由项目派生，不是随机八股 |
| Interview Realism | 8.0/10 | 单题很真实；100 问全部执行不像单场真实面试 |
| Information Gain | 10/10 | 直接定位 PF-031/PF-032/PF-029/030 source-level gap，并推翻“架构完整=面试可讲”的错觉 |
| User Alignment | 9.5/10 | 基本命中用户定义的精品/全链路/不造轮子方向；最终仍需用户本人评价 |

**Overall Red quality: 91.5/100 — PASS_WITH_REVISIONS**

这个分数只评价本轮问题设计，不代表 Blue 面试通过，也不代表严格 blind context 已认证。

## Highest-value questions

### Q042 / Q049 / Q051 / Q055 — GraphRAG implementation ownership

这组问题是本轮最大信息增益来源。Resume 已经写出具体算法名和数字，Red 没有满足于“为什么用 GraphRAG”，而是连续追 runner、metric、fusion、seed、alias、ranking。它直接把一个看似最强的 Resume bullet 打成当前最大风险。

### Q019–Q025 / Q032–Q035 — Tool implementation and tests

这组问题把“我做了 Tool Calling strategy”从框架名压到 binding lifecycle、mapping、concurrency、matcher 和 regression assertion。Blue 在这些位置大量 Unknown，说明问题确实改变了 interviewer verdict。

### Q067–Q084 — Context / Memory contract

这组没有停在“Memory 分几层”，而是追 scope、read gate、orchestrator、crash、idempotency、DB isolation 和 tests。与用户要求的“项目自然下钻基础”高度一致。

### Q040 / Q064 / Q085 / Q093 / Q100 — Build / Buy / Delete

这些问题成功防止候选人把已经做过的复杂度合理化成“必须存在”。特别是“成熟平台补齐 Delta 以后删不删”和“Hybrid RAG 达标以后删不删”属于高价值判断题。

## Questions with lower marginal value

这些题本身并非无效，但在一场真实面试里可进入 reserve，而不是 primary path。

### Q009

和 Q002/Q007/Q010 都在压 Pilot / environment / Production boundary。Q009 仍有环境配置价值，但可以合并到 Q002 后的 follow-up。

### Q028

在候选人连 Q027 的真实递归机制都无法复现时，继续问如何推广成通用 cycle detection 已进入二阶设计。真实面试更可能先停在 ownership failure。

### Q031

复杂自然语言 parser edge cases 有价值，但若 Q029 已无法讲清真实 bug，Q031 的信息增益下降，可以进入 reserve。

### Q054 / Q056

alias false merge、path-length bias 都是合理算法问题；但候选人 Q053/Q055 连真实实现都说不清时，继续展开假设风险更像 research review，而不是最短面试路径。

### Q096–Q098

逻辑模块拆服务、跨模块 DB 边界、全链路 Trace 与 Resume 第四条架构复盘有关，因此并非脱题；但对 `Implementation Interviewer` 主画像而言，它们应排在个人代码 ownership 之后。如果前面已经 NO_HIRE，这三题在真实面试中的优先级较低。

## Duplicate analysis

本轮没有出现旧方法那种“大量换词重复问模块边界”的问题。

存在的局部近邻主要是：

```text
Q024 matcher → Q025 route boundary
Q029 real parser bug → Q030 design rationale → Q031 generalization
Q049 fusion → Q050 failure mode
Q053 alias implementation → Q054 false merge
Q055 ranking implementation → Q056 path bias
```

这些多数形成合理的 implementation → counterexample 深度阶梯，而不是同义重复。

可优化之处是**动态停止**：如果前一个问题已经暴露“不知道真实实现”，后续 speculative follow-up 应降级为 reserve，把时间转给另一个高风险 Claim。

## Full-chain audit

### Tool/MCP

```text
why change nested Agent-as-Tool
→ before/after call chain
→ binding lifecycle / mapping
→ request isolation / schema
→ direct route / bugs / tests
→ timeout / idempotency / cancellation
→ Build/Buy/Delete
```

Result: **complete and high-value**.

### GraphRAG

```text
why GraphRAG / baseline
→ dataset/runner/metrics
→ failure candidate displacement
→ fusion/seed/alias/ranking implementation
→ ablation/overfit/cost/index drift
→ kill condition / formal benchmark
```

Result: **complete and highest information gain**.

### Context/Memory

```text
baseline failure
→ contracts / scope
→ prepare_context / orchestrator
→ approval / stale / injection
→ post-turn crash / idempotency / DB isolation
→ tests
→ Build/Buy/Delete
```

Result: **complete and high-value**.

### Architecture

```text
simple RAG baseline
→ business failure conditions
→ Domain / Runtime / Effect / Security boundary
→ Generic Host reuse
→ measurement gate
→ service split / trace
→ rebuild/delete
```

Result: **complete but slightly over-budget for an Implementation-primary round**.

## Skill defects discovered

### 1. 100 questions need execution priority, not only generation quality

Current Skill says 100 is not KPI, but output format still makes 100 questions look like one literal interview sequence.

**Proposed independent Skill change:** keep the 100-question pressure suite, but require labels:

```text
PRIMARY_PATH      25–40 questions
RESERVE_FOLLOWUP  remaining questions
KILL_SWITCH       conditions that stop one chain and move to another
```

The archive still gets 100 high-quality questions; the simulated interviewer behaves more like a real interviewer.

### 2. Named implementation claims need an early ownership probe

When Resume contains exact names like `baseline-preserving fusion` or `ContextOrchestrator`, the first 2–3 questions in that chain should require:

```text
define the actual algorithm / contract
show input/output
show one failure example
show one test assertion
```

Round #014 eventually did this very well, but the Skill should make it an explicit invariant rather than relying on model judgment.

### 3. Implementation-primary persona needs an architecture budget ceiling

For an Implementation Interviewer, architecture/counterfactual questions should not consume more time than code/data/test ownership once a fatal implementation gap exists.

**Proposed default:** architecture + manager pressure remains in the 100-question suite, but only 10–15 questions enter PRIMARY_PATH unless the implementation chains pass.

## Protocol defects discovered

### 1. `stage_head_sha` name is semantically awkward

A file cannot contain the SHA of the commit that contains itself. Round #014 therefore uses `stage_head_sha` as “last consumed input HEAD”, while live branch ref is authoritative.

This works but the name is ambiguous.

**Proposed independent protocol change:** rename to one of:

```text
last_input_head_sha
stage_input_head_sha
```

and record `output_commit_sha` only in the next transcript event / Git history.

### 2. Round Init did not capture all initial user feedback

Initial `07_user_feedback.md` recorded the GitHub-mediated workflow requirement but omitted the equally important user judgment that the prior Red was unqualified and must use boutique/full-chain/build-buy/implementation attack skill. The Controller caught and committed UF-002 before this retrospective, but this should not require repair.

**Proposed protocol change:** Round Init must normalize all user requirements that affect the current Round into `07_user_feedback.md` before Resume Builder begins.

### 3. CHATGPT_AUTO remains logically, not physically, blind

This is now represented honestly and is no longer a protocol inconsistency. It remains a **certification limitation**.

Use `AGENT_AUTO` when the question is “can an actually isolated interviewer produce the same attack?” Do not spend an AGENT_AUTO retest before P0/P1 implementation documentation changes, because current content gap would dominate the result again.

## Was Red still too reviewer-like?

**Mostly no.**

The implementation chains are recognizably interview questions because they ask what a candidate claiming those resume bullets should know. Q019/Q020/Q024/Q032/Q042/Q049/Q067/Q084 are especially clear examples.

The tail of the architecture chain Q096–Q098 is the closest to Reviewer territory. They remain defensible because the Resume explicitly includes “架构与工程复盘”, but an actual Implementation interview would usually reach them only if earlier implementation chains survived.

## Did Red attack unnecessary wheel reinvention?

**Yes.**

It did not accept “法律业务特殊” as an answer. Tool binding, GraphRAG, Memory and Runtime all faced a delete/adopt question. This is a substantive improvement over a feature-list review.

## Did Red naturally test fundamentals?

**Yes.**

Fundamentals came from the project:

```text
MCP user config → concurrent request isolation / ContextVar
Tool timeout → TCP/HTTP uncertainty / idempotency
async tool → cancellation semantics
Memory concurrent update → PostgreSQL isolation / lost update
GraphRAG metrics → Recall / MRR / ranking / ablation
```

No standalone “讲讲 Redis / 什么是 RAG” question was needed.

## Information gained from the workflow itself

The new GitHub state bus worked: every major stage was frozen before the next stage re-read it, and user-feedback normalization itself became a visible commit rather than an implicit memory correction.

The biggest workflow lesson is that **resume-first alone is insufficient unless the resume contains claims with enough implementation surface**. Round #014 improved the resume by adding PF-031 GraphRAG; that single claim produced far more useful implementation pressure than broad Target Architecture questions.

## Proposed next-round changes

Do not run Round #015 yet.

First complete at least P0 GraphRAG source-level recovery. Ideally also recover Tool/MCP and Context/Memory. Then in the next independent Red Skill / protocol task:

1. add PRIMARY_PATH / RESERVE_FOLLOWUP / KILL_SWITCH;
2. add named-implementation early ownership probes;
3. cap architecture questions in Implementation-primary path;
4. rename `stage_head_sha` semantics;
5. make complete user-feedback normalization a Round-init invariant.

After canonical Project docs change, open a fresh resume-first Round. For strict context-firewall validation, use `AGENT_AUTO` on that retest.

## Final workflow judgment

```text
Previous user complaint: materially addressed
Red technical depth: PASS
Red full-chain quality: PASS
Red non-duplication: PASS_WITH_MINOR_COMPRESSION
Red Build/Buy skepticism: PASS
Red fundamentals drilldown: PASS
Interview realism: PASS_WITH_EXECUTION_PATH_GAP
GitHub process self-consistency: PASS_WITH_PROTOCOL_CLEANUP
Strict blind-Red certification: NOT_APPLICABLE_IN_CHATGPT_AUTO

Round #014 Red/Harness verdict: PASS_WITH_REVISIONS
```
