# Red Evaluation — rb-2026-09-13-resume-first-014

formal_input_head: 895c355f86002dcb96be86bd952f201f87ecbfaf
formal_inputs:
- 01_simulated_resume.md
- 02_red_questions.md
- 03_blue_answers.md
- .agent/red-blue/attack-model.md@10869d9176d2ef34b46577478bba62d9e254158a

Zuno canonical docs were not used as formal inputs for this evaluation.

## Overall interviewer verdict

**Verdict: PARTIAL — NO_HIRE_YET_FOR_IMPLEMENTATION_ROUND**

这组回答证明候选人有两项明显优势：一是事实边界感强，不会把 Pilot 说成 Production，也不会把团队、Target、测试 artifact 和个人实现混成一件事；二是对 Agent 系统里的 failure semantics、Build/Buy、TCP timeout、幂等、数据库隔离、长期任务恢复等原理理解较完整。

但当前岗位是 Agent 开发 / AI 应用工程技术面，主画像又是 Implementation Interviewer。简历中三条核心技术 bullet 都用了足够具体的实现名词；回答一旦追到这些名词的函数、数据结构、算法、参数、test assertion，就大量退回“文档没有冻结 / 需要现场看代码”。这在事实审计上是诚实，在面试判断上仍然是 implementation ownership 未证明。

最危险的一点是 GraphRAG。简历直接写了四个具体改动名称和精确指标，候选人却无法在不看源码的情况下解释 fusion 公式、seed 选择、alias normalization、path ranking、`limit=5` 语义、`FullChainHit@5` 定义或逐项 ablation。真实面试官会问：如果这些确实是你实现的，为什么最核心算法细节需要依赖文档恢复？

所以这轮不能因为“回答诚实”判 PASS。当前更像一个**架构理解强、工程边界成熟，但个人实现故事还没有被训练到可脱稿复现**的候选人。

## Claim A — Project reality / Pilot / Ownership

verdict: **PASS**
ownership: **PASS**
business_causality: **PASS**
implementation_depth: **PARTIAL**
evidence: **PASS**
communication: **PASS**

**Strongest answers**
- Q003/Q004 能主动说明加入时已有系统，并把“参与 Agent / Memory”与“完整 Runtime / 完整 Memory Owner”分开。
- Q007/Q010 对 Pilot、Production、QPS/P95/SLA 的边界清楚，不制造数字。
- Q005 能按时间给出四条工作的演进，而没有硬编成单一因果链。

**Weakest answers**
- Q002/Q009 对 Pilot / 法院侧测试的环境、参与人、题集和验证方式无法落地。
- Q013 对 reviewer / review 过程无证据。
- Q014 无法说明 Coding Agent 在历史任务中的具体参与方式。

**Interviewer judgment**
项目真实性总体可信，且主动承认已有系统反而提升可信度。问题主要是历史现场证据不够丰富，不足以支撑“真实用户环境里我具体负责什么”的强叙事。

resume_claim_risk: **MEDIUM**
retest_recommendation: 恢复一条真实用户 / Pilot 工作流和一条个人任务的 Issue → code → test → result → review 证据链。

## Claim B — Agent / Tool Calling / MCP

verdict: **PARTIAL**
ownership: **PARTIAL**
business_causality: **PARTIAL**
implementation_depth: **FAIL**
build_buy: **PASS**
failure_recovery: **PASS_AS_KNOWLEDGE / NOT_PROVEN_HISTORICALLY**
evidence: **PARTIAL**
fundamentals: **PASS**

**Strongest answers**
- Q016–Q018 能诚实区分“结构确实被收口”和“当时为什么收口、收益多大并未恢复”。
- Q036–Q039 对 timeout、possible remote success、idempotency、async cancellation 的原理正确。
- Q040 能明确说成熟 SDK 补齐通用 binding 后应该删除 plumbing，只保留业务 Delta。

**Credibility breaks**
- Q019 不知道 concrete tools 的绑定生命周期。
- Q020 不知道 tool→server map 的结构、唯一键与同名 Tool 冲突策略。
- Q021/Q022 无法说明用户级 MCP config 的并发隔离；这对“调用期注入用户配置”是直接 implementation question。
- Q024/Q025 不能解释 direct route matcher 和 ReAct 边界。
- Q027/Q029 无法复现两个简历明确写出的 bug 的最小触发路径。
- Q032–Q034 不知道自己引用的 regression test 到底断言什么、是什么测试层级、config gate 的负例是什么。

**Interviewer judgment**
这条故事目前可以证明“候选人参与并修改过这一带代码”，还不能证明“候选人掌握这段实现到可以独立维护”。尤其简历已经写到 middleware、route、regression artifact，面试官有充分理由要求数据结构和函数级回答。

resume_claim_risk: **HIGH**
retest_recommendation: 不先弱化简历；先恢复 4/15、4/28 commit diff 和 tests，形成一条可脱稿讲清的 before → decision → data flow → bug → assertion 链。如果源码恢复后仍无法解释，再缩简历。

## Claim C — GraphRAG retrieval quality

verdict: **FAIL**
ownership: **PARTIAL**
business_causality: **PASS**
implementation_depth: **FAIL**
evaluation_depth: **FAIL**
build_buy: **PASS**
evidence_honesty: **STRONG_PASS**

**Strongest answers**
- Q041/Q064 明确 GraphRAG 是 measurement-gated option，而不是默认优于 Hybrid RAG。
- Q057/Q058 不把最终 rerun 反写成每个改动的独立因果贡献，也承认 overfit 风险。
- Q065 能设计一个合理的正式 benchmark / ablation 方向。

**Critical credibility breaks**
- Q042 无法解释简历中 `limit=5` 的语义。
- Q044–Q046 无法给出 `Recall@5`、`MRR@10`、`FullChainHit@5` 在本项目 evaluator 中的精确定义。
- Q049 不知道 `baseline-preserving fusion` 的实际算法。
- Q051/Q052 不知道 `candidate-aware seed expansion` 的 seed 规则和参数。
- Q053/Q054 不知道 alias normalization 的实现和冲突处理。
- Q055/Q056 不知道 path-aware ranking 的 feature / 公式。
- Q059 不知道 `fallback_count=1` 在这次 runner 中到底代表什么。

**Interviewer judgment**
这是本轮最严重的断点。简历用了“随后实现 baseline-preserving fusion、candidate-aware seed expansion、entity alias normalization 与 path-aware ranking”这样的个人实现语气，还列了具体评测数字。真实面试里，这些对象就是最自然的算法深挖入口。候选人若不能解释其真实算法和 evaluator，面试官会怀疑这些名称来自复盘文档，而不是本人可复现的实现记忆。

诚实强调“小样本 smoke、不是 benchmark”值得加分，但它不能抵消 implementation ownership 缺失。

resume_claim_risk: **CRITICAL**
retest_recommendation: 下一步优先级最高。恢复 PF-031 对应代码、runner、raw/frozen config、指标实现和 commit 顺序；至少能讲清一个失败 query 的 candidate list，以及四项改动中每项真实做了什么。没有这些内容时，不应把四个算法名同时写进最终求职简历。

## Claim D — Context / Memory

verdict: **PARTIAL**
ownership: **PARTIAL**
business_causality: **PASS**
implementation_depth: **FAIL**
security_reasoning: **PASS_AS_DESIGN**
evidence: **PARTIAL**

**Strongest answers**
- Q074 主动把 PR #8 限定在 readback hardening / contract / tests，没有冒充完整审核生命周期。
- Q075/Q077 能说清 Memory 不应成为权威事实，stale / prompt-injection 是独立风险。
- Q083/Q085 不把 foundation 说成熟长期记忆系统，也愿意复用 Memory provider。

**Credibility breaks**
- Q067/Q068 无法列出 typed contract 的核心字段和 scope 维度。
- Q069 不知道 scope isolation 真正在什么层 enforce。
- Q070/Q071 无法把 `prepare_context()` / `ContextOrchestrator` 讲到接口和调用链。
- Q072/Q073 不知道 summary / structured memory 的 arbitration、token budget 和 read-after-revoke race。
- Q076 不知道 source-id trace 的粒度。
- Q079–Q081 对 post-turn crash、idempotency、并发更新只能给设计答案，无法证明历史实现。
- Q084 知道“32 passed”，却不能给出最关键的正负 test assertion。

**Interviewer judgment**
“参与”这一措辞降低了 claim 风险，但 bullet 仍列出多个具体工程对象。候选人必须至少能复现 Contract shape、scope model、pre-call readback data flow 和 2–3 个关键 tests，才配得上现在的具体度。

resume_claim_risk: **HIGH**
retest_recommendation: 恢复 PF-029/PF-030 的 schema、`prepare_context()`、`ContextOrchestrator` 和 focused tests，形成一个 bounded implementation story。

## Claim E — Architecture / reuse-first / failure semantics

verdict: **STRONG_PASS**
business_causality: **STRONG_PASS**
build_buy: **STRONG_PASS**
failure_recovery: **STRONG_PASS**
simplification: **STRONG_PASS**
communication: **PASS**

**Strongest answers**
- Q086/Q087 能从最简单 RAG baseline 推导材料版本、正式成果、长任务、权限变化和外部副作用，而不是先背模块名。
- Q090/Q091 能区分 Runtime checkpoint、业务提交和现实 Effect，并解释 crash / timeout recovery。
- Q093/Q094/Q096 能主动复用成熟平台、避免微服务化和 Multi-Agent 崇拜。
- Q095/Q100 能给复杂机制明确 measurement / delete condition。

**Risk**
回答中大量 Authority / Receipt / Effect / measurement-gated 等架构词汇非常完整，而前面实现故事又明显不够细，形成一定“背架构文档感”。如果真实面试把 3 分钟继续压到函数 / SQL / test，当前表现会出现明显落差。

resume_claim_risk: **LOW_AS_DESIGN / HIGH_IF_PRESENTED_AS_IMPLEMENTED**
retest_recommendation: 保留为后半段架构成熟度加分项，不要让它替代个人实现主故事。

## Fundamentals derived from project

verdict: **PASS**

- TCP / HTTP timeout 与 remote side effect：PASS。
- idempotency / unknown outcome：PASS。
- asyncio cancellation 与远端执行：PASS。
- PostgreSQL isolation / lost update：PASS。
- Build/Buy / complexity deletion：PASS。

这些回答说明基础不是当前主要风险。当前主要风险是**把基础原理和 Target 设计讲得比本人历史实现更熟**。

## Most dangerous interview breakpoints

1. **GraphRAG algorithm ownership**：简历最具体，回答最不能下钻。
2. **GraphRAG evaluator ownership**：有数字却不知道 runner 参数和 metric definition。
3. **Tool config isolation**：写了用户级配置注入，却无法解释 concurrency / lifecycle / keying。
4. **Direct route implementation**：写了 deterministic route / fallback，却无法说明 matcher 和 failure path。
5. **Regression tests**：写了 test artifact / 32 passed，却无法列最关键 assertion。
6. **Context/Memory contract**：写了 typed contracts/scoped memory，却无法复现字段和 scope model。
7. **Context data flow**：`prepare_context()` / `ContextOrchestrator` 只能讲摘要级 before/after。
8. **Historical rationale**：多处知道“改了什么”，不知道“当时为什么改”。
9. **Review / collaboration provenance**：reviewer、真实 ownership handoff 未恢复。
10. **Pilot reality**：真实用户流程、环境、样本和结果缺失。

## Communication readiness

### 30 秒
**PASS.** 项目边界、简单 RAG 与复杂法律任务的差别可以讲清。

### 90 秒
**PASS.** 能选 GraphRAG / Tool / Memory 中一条讲“做过什么 + 边界是什么”，且事实不膨胀。

### 3 分钟 implementation deep dive
**FAIL in current form.** 一旦进入算法、字段、调用栈、参数或 test assertion，频繁依赖“需要回源码 / 文档未冻结”。

## Does this sound like someone who actually did it?

**Partly.**

项目经历、失败边界、个人不认领的部分很可信；这不像纯粹编造项目。问题在于核心技术 bullet 的词汇具体度高于候选人的脱稿 implementation recall。真实面试官会形成一种判断：**“你大概率参与过，但我还没确认这些具体算法和机制是不是你真正拥有的。”**

## Interview decision

```text
Project reality: PASS
Ownership honesty: PASS
Architecture maturity: STRONG_PASS
Fundamentals: PASS
Tool/MCP implementation ownership: PARTIAL
GraphRAG implementation ownership: FAIL
Context/Memory implementation ownership: PARTIAL
Production/evidence honesty: STRONG_PASS

Overall: PARTIAL
Hiring signal for implementation-heavy Agent role: NO_HIRE_YET
```

## Retest recommendation

不要先继续增加架构名词，也不要马上把所有简历技术内容删弱。先恢复三条 source-level implementation story：

1. PF-031 GraphRAG：runner + metric + candidate list + four real algorithm changes + tests/ablation boundary；
2. PF-032 Tool/MCP：before/after call graph + binding lifecycle + config map/isolation + direct route matcher + two bug reproductions + tests；
3. PF-029/PF-030 Context/Memory：contract fields + scope model + `prepare_context()` / orchestrator data flow + key tests。

如果这些事实能从历史源码恢复并与个人 commit 对齐，下一轮简历无需弱化，Blue 只需要把实现故事真正学透；如果恢复不到，就应该缩小对应 Resume Claim。
