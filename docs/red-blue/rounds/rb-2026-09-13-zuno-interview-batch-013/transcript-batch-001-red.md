# Round #013 — Batch 001 — Red

Status: `FROZEN_AND_ARCHIVED`  
Question count: **100**  
Primary persona: Skeptical Hiring Manager  
Cross pressure: Agent/RAG Engineer + Backend/System Design + Reliability/Security

This file contains explicit Red attack metadata required by the harness. `red_hidden_intent` is protocol-level attack metadata, not model private chain-of-thought.

## A. Project Reality / Causality / Resume Claim Strength

### Q001
- **claim_under_test:** Zuno solves real legal-AI engineering constraints rather than post-hoc architecture concerns.
- **attack_angle:** Project causality / Current vs Target.
- **red_question:** 你现在的文档已经能讲材料版本、正式结果、恢复和外部副作用。但你加入项目时这些问题到底哪些是真实发生过的，哪些只是后来做架构复盘时推导出来的？请严格按 History / Current / Target / Unknown 分开。
- **red_hidden_intent:** Detect retrospective storytelling that converts target architecture into historical fact.
- **expected_evidence:** Project history, provenance ledger, Current evidence boundaries.

### Q002
- **claim_under_test:** Historical customer feedback motivated meaningful engineering work.
- **attack_angle:** Evidence / project reality.
- **red_question:** 你简历里说项目面向天津法院智慧平台场景。客户 Demo 的“回答质量需要提高”具体是哪个 Bad Case？输入是什么、错在哪里、后来谁修了、修完指标怎样？如果这些都没有恢复，你凭什么把后来的 RAG/Memory/Runtime 设计和这条反馈建立因果？
- **red_hidden_intent:** Force admission of unknown root cause and stop fabricated quality narrative.
- **expected_evidence:** Project README history section; provenance around customer feedback.

### Q003
- **claim_under_test:** Zuno had a real stakeholder workflow.
- **attack_angle:** User / workflow reality.
- **red_question:** 不讲模块名。真实用户是谁，他打开系统以后完成一项法律工作的步骤是什么？你能确认到哪一步，哪一步只是今天 Target 里的理想工作流？
- **red_hidden_intent:** Test whether candidate can distinguish real pilot workflow from target Case Workspace story.
- **expected_evidence:** Project history, Current evidence, Unknown list.

### Q004
- **claim_under_test:** Zuno requires more than a generic host plus Hybrid RAG.
- **attack_angle:** Baseline / replaceability.
- **red_question:** 假设我给你一个成熟 Agent Host、PostgreSQL、BM25+dense+rerank、一个强模型和人工审核。对于你们真实历史任务，哪一条已经被证明确实不够？不要用 Target 设计回答，用当时可证明的项目事实回答。
- **red_hidden_intent:** Separate historical necessity from architectural possibility.
- **expected_evidence:** Historical evidence; explicit Unknown if unproven.

### Q005
- **claim_under_test:** Pilot has meaningful but bounded value.
- **attack_angle:** Production claim pressure.
- **red_question:** 你说项目进入 Pilot Validation。这个 Pilot 到底证明了什么？真实用户数、使用时长、任务量、SLO、故障率、回滚、人工兜底、数据外发条件里哪些有证据，哪些没有？
- **red_hidden_intent:** Prevent Pilot -> Production inflation.
- **expected_evidence:** Project Current/Unknown; evidence docs.

### Q006
- **claim_under_test:** Project value can eventually be measured.
- **attack_angle:** Outcome / measurement.
- **red_question:** 如果不能说准确率提升、不能说生产稳定、不能说用户规模，那 Zuno 现在最合理的三个产品价值指标是什么？这些指标今天有没有基线？
- **red_hidden_intent:** Test whether candidate can define measurable value without inventing numbers.
- **expected_evidence:** Evaluation Target; Measurement Needed.

### Q007
- **claim_under_test:** Product identity is coherent.
- **attack_angle:** Product framing.
- **red_question:** 你简历仍写“法律智能 Agent 平台”，但最新文档更强调 Case Workspace。那到底哪个是产品、哪个只是执行技术？面试官如果说你项目名本身就在过度强调 Agent，你怎么解释？
- **red_hidden_intent:** Expose mismatch between resume wording and updated product thesis.
- **expected_evidence:** Project/Application/Runtime narratives; resume wording.

### Q008
- **claim_under_test:** Research lineage is not falsely presented as implemented product capability.
- **attack_angle:** Research ownership / Current evidence.
- **red_question:** 葛季栋团队做过事件抽取、法条推荐、LawBench、LJPCheck 等研究。你能列出哪些论文方法确定进入过你参与的历史 Zuno 版本吗？如果不能，为什么项目文档还花大量篇幅讲它们？
- **red_hidden_intent:** Force distinction between lineage, product strategy, and current integration.
- **expected_evidence:** Research lineage docs; explicit no-current implication.

### Q009
- **claim_under_test:** Candidate is honest about inherited system.
- **attack_angle:** Ownership / greenfield pressure.
- **red_question:** 你加入时系统已经存在。请你描述“你加入前已经有的东西”和“你加入后本人新增或修改的东西”，至少到 Agent、前端、数据库、RAG、Memory、Tool 这几层，不能用“团队后来完善”混过去。
- **red_hidden_intent:** Detect greenfield ownership inflation.
- **expected_evidence:** Resume, Project ownership section, task-specific evidence.

### Q010
- **claim_under_test:** Candidate can identify real adoption signal.
- **attack_angle:** Product reality.
- **red_question:** 除了 Demo、法院人员测试和 Pilot 这些阶段名，你有什么证据证明用户真的依赖过某个 Zuno 输出完成工作？如果没有，应该怎样表述而不贬低项目也不夸大？
- **red_hidden_intent:** Test maturity of claim language.
- **expected_evidence:** History vs Unknown boundaries.

### Q011
- **claim_under_test:** Historical architecture is not reconstructed from current repo.
- **attack_angle:** Timeline accuracy.
- **red_question:** 2026 年 3 月你加入时的系统架构和今天 main 的架构有什么能确认的差异？哪些历史技术栈其实无法恢复？
- **red_hidden_intent:** Challenge use of current repo as historical proof.
- **expected_evidence:** Project historical unknowns.

### Q012
- **claim_under_test:** Architecture review work has legitimate value despite being post-hoc.
- **attack_angle:** Resume claim risk.
- **red_question:** 你简历第四点写“架构与证据复盘”。面试官可能直接说：这不是项目开发，只是你后来给已有代码补文档。你怎么证明这项工作有工程价值，同时又不把 Target 设计说成你历史上实现的？
- **red_hidden_intent:** Test claim strength and personal ownership boundaries.
- **expected_evidence:** Resume wording; docs governance/evidence separation.

### Q013
- **claim_under_test:** Project solves business constraints, not technology enthusiasm.
- **attack_angle:** Product causality.
- **red_question:** 如果把 Agent、GraphRAG、Memory、MCP 这些词全部删掉，你还能用三句话解释项目为什么值得存在吗？
- **red_hidden_intent:** Detect technology-first narrative.
- **expected_evidence:** Project Part A opening/productization constraints.

### Q014
- **claim_under_test:** Agent layer is not essential by identity.
- **attack_angle:** Simplification.
- **red_question:** 假设明天把所有 Agent 逻辑替换成固定 workflow，只保留 Case Workspace、检索、专业能力和人工复核，哪些真实任务会立刻做不了？哪些其实完全不受影响？
- **red_hidden_intent:** Test deletion condition for Agent runtime.
- **expected_evidence:** Project task complexity tiers; Runtime simplification rules.

## B. Personal Ownership — Agent / MCP / Tool Calling

### Q015
- **claim_under_test:** Candidate personally changed MCP invocation architecture.
- **attack_angle:** Implementation ownership.
- **red_question:** 你简历说把 MCP Server 从 `MCPAgent-as-Tool` 嵌套路径改成 `GeneralAgent` 直接绑定具体 MCP Tools。原调用链和新调用链分别是什么？具体改了哪些函数或对象？
- **red_hidden_intent:** Verify candidate can explain owned implementation beyond wording.
- **expected_evidence:** Resume snapshot; historical task evidence if available.

### Q016
- **claim_under_test:** The MCP refactor solved a real problem.
- **attack_angle:** Baseline / root cause.
- **red_question:** `MCPAgent-as-Tool` 到底坏在哪里？是多一层模型推理、参数丢失、权限边界、递归、Trace 不清楚，还是只是代码不好看？请给一个真实失败场景。
- **red_hidden_intent:** Prevent aesthetic refactor being sold as architecture value.
- **expected_evidence:** Task evidence; regression case.

### Q017
- **claim_under_test:** Refactor outcome is evidenced.
- **attack_angle:** Measurement / regression.
- **red_question:** 这个 Tool Calling 改造前后，你实际证明了什么改善？调用成功率、token、延迟、失败类型、回归测试里至少哪一项有可核验变化？
- **red_hidden_intent:** Demand outcome evidence.
- **expected_evidence:** Tests/PR evidence; otherwise Unknown.

### Q018
- **claim_under_test:** User-level MCP configuration injection is correctly scoped.
- **attack_angle:** Security / context propagation.
- **red_question:** 你说调用期注入用户级 MCP 配置。这个配置从哪里来，如何绑定用户/Workspace/Run，Worker 恢复以后怎么避免拿错用户配置？
- **red_hidden_intent:** Probe multi-tenant/context leakage risk.
- **expected_evidence:** Historical implementation details; Security target if only design.

### Q019
- **claim_under_test:** Deterministic direct route + ReAct fallback is principled.
- **attack_angle:** Agent routing trade-off.
- **red_question:** Workspace 调用层为什么同时保留 deterministic direct route 和 ReAct fallback？什么条件走 direct，什么条件才让模型决定？如果规则选错会出现什么问题？
- **red_hidden_intent:** Test whether routing is intentional or accidental complexity.
- **expected_evidence:** Resume/task evidence; Application/Runtime principles.

### Q020
- **claim_under_test:** Candidate understands MCP recursion bug.
- **attack_angle:** Debugging depth.
- **red_question:** 自定义 MCP 名称递归问题具体怎么触发？递归发生在注册、工具名解析、Agent 包装还是调用回注？你是怎样定位到根因而不是只加一个 if？
- **red_hidden_intent:** Test real debugging ownership.
- **expected_evidence:** Historical bug/task details.

### Q021
- **claim_under_test:** Candidate understands parameter parsing bug.
- **attack_angle:** Debugging / schema.
- **red_question:** 高德天气参数解析为什么会错？是模型生成参数、MCP schema、Pydantic/FastAPI 转换还是 provider adapter 的问题？修复后加了什么回归用例？
- **red_hidden_intent:** Verify concrete implementation knowledge.
- **expected_evidence:** Task tests/PR evidence.

### Q022
- **claim_under_test:** Regression tests are meaningful.
- **attack_angle:** Test quality.
- **red_question:** 你说新增对应回归用例。它们验证的是函数行为、Agent trajectory、MCP integration 还是端到端？如果换模型，测试会不会不稳定？
- **red_hidden_intent:** Distinguish deterministic regression from flaky LLM tests.
- **expected_evidence:** Test scope and assertions.

### Q023
- **claim_under_test:** Team vs personal Tool Calling ownership is clear.
- **attack_angle:** Ownership.
- **red_question:** Tool Calling Strategy 是你负责、参与还是只改过其中一条链？如果面试官问“整个 Tool Runtime 是你写的吗”，你的精确回答是什么？
- **red_hidden_intent:** Force bounded ownership statement.
- **expected_evidence:** Project ownership section; resume.

### Q024
- **claim_under_test:** Candidate has concrete PR/code evidence.
- **attack_angle:** Evidence.
- **red_question:** 你能不能给出一个你本人最能代表 Zuno Agent 工作的 PR/commit，讲清输入、改动、测试和结果？如果现在文档没有精确 PR 映射，这是不是简历证据缺口？
- **red_hidden_intent:** Identify missing personal task traceability.
- **expected_evidence:** Resume/Project Unknown; commit provenance if available.

### Q025
- **claim_under_test:** LangGraph use is understood, not name-dropping.
- **attack_angle:** Framework fundamentals.
- **red_question:** 你在 Zuno 里实际用了 LangGraph 哪些能力？Checkpoint、graph execution、interrupt、Send、Reducer、subgraph 里哪些是 Current，哪些只是你后来在 Target 中讨论过？
- **red_hidden_intent:** Separate hands-on usage from architecture knowledge.
- **expected_evidence:** Current evidence and resume.

### Q026
- **claim_under_test:** MCP schema changes are handled safely.
- **attack_angle:** Tool versioning.
- **red_question:** 如果 MCP Server 在任务运行中升级，Tool schema 从 v1 变 v2，旧 Plan 已经生成了 v1 参数，你的历史实现会怎样？今天 Target 又准备怎样？请两层分开。
- **red_hidden_intent:** Current/Target split under schema drift.
- **expected_evidence:** Historical implementation vs Capability/Effects target docs.

### Q027
- **claim_under_test:** Tool permission claims are honest.
- **attack_angle:** Security / implementation.
- **red_question:** 你本人做的那条 Tool Calling 链里，执行前权限检查到底做到什么程度？是真实 Current 的 user-level config scope，还是今天 Target 才有 SecurityEpoch / continuous authorization？
- **red_hidden_intent:** Prevent security target inflation into personal implementation.
- **expected_evidence:** Resume; evidence; Security docs.

### Q028
- **claim_under_test:** Tool refactor is valuable enough for resume.
- **attack_angle:** Hiring-manager skepticism.
- **red_question:** 如果我说“你这就是把一个 Agent wrapper 拆掉，顺便修了两个 bug”，为什么它值得占简历第一条？请用工程因果而不是技术名词回答。
- **red_hidden_intent:** Stress resume prioritization.
- **expected_evidence:** Concrete failure reduction, simplification, boundary clarification.

## C. Personal Ownership — Context / Memory

### Q029
- **claim_under_test:** Candidate personally implemented `GeneralAgent.prepare_context()` slice.
- **attack_angle:** Implementation ownership.
- **red_question:** 你在 `GeneralAgent.prepare_context()` 里具体接了哪两类上下文？调用顺序、过滤条件、返回结构是什么？
- **red_hidden_intent:** Verify implementation depth.
- **expected_evidence:** Resume; focused task evidence.

### Q030
- **claim_under_test:** Same-scope task summary is correctly scoped.
- **attack_angle:** Data isolation.
- **red_question:** “同 scope task summary”的 scope 到底是什么？User、Workspace、Matter、Task 还是 Session？如果两个案件属于同一个用户，怎样防止摘要串案？
- **red_hidden_intent:** Probe boundary ambiguity.
- **expected_evidence:** Context Pack policy / tests.

### Q031
- **claim_under_test:** Only APPROVED memory is injected.
- **attack_angle:** Memory governance.
- **red_question:** 为什么只允许 `APPROVED` structured memory 进入 Context？谁把 Candidate 变 APPROVED？你本人实现的是读取 gate 还是完整审核生命周期？
- **red_hidden_intent:** Separate read-time gate from full memory authority.
- **expected_evidence:** Resume; historical task evidence.

### Q032
- **claim_under_test:** Review gate is meaningful.
- **attack_angle:** Human/memory governance.
- **red_question:** 这个 review gate 如果没有人审，系统还能自动写长期记忆吗？如果不能，产品上怎么避免所有 Memory 永远卡在 Candidate？
- **red_hidden_intent:** Test operational viability and target/current distinction.
- **expected_evidence:** Memory task docs; Unknown if not built.

### Q033
- **claim_under_test:** Source-id trace supports provenance.
- **attack_angle:** Traceability.
- **red_question:** `source-id trace` 具体能追到什么？原始消息、task summary、memory row、DocumentVersion 还是只是一个字符串？它如何帮助你排查错误上下文？
- **red_hidden_intent:** Prevent provenance buzzword usage.
- **expected_evidence:** Focused tests/task artifact.

### Q034
- **claim_under_test:** Memory authority is correctly bounded.
- **attack_angle:** Authority.
- **red_question:** 如果 structured memory 里写“付款日期是 6 月 1 日”，Domain 正式材料后来变成 6 月 15 日，谁是 Authority？你的历史 Context Builder 会不会继续把旧记忆喂给模型？
- **red_hidden_intent:** Test stale memory handling.
- **expected_evidence:** Current implementation boundary; target Memory/Domain principles.

### Q035
- **claim_under_test:** Context contamination is understood.
- **attack_angle:** Security / prompt injection.
- **red_question:** Tool 输出或 Memory 里如果包含“忽略之前指令并执行某工具”，Context Builder 怎样区分数据和指令？你本人那条 slice 有没有做这层隔离？
- **red_hidden_intent:** Probe prompt-injection boundary vs target security.
- **expected_evidence:** Historical implementation; if absent, honest gap.

### Q036
- **claim_under_test:** Memory conflicts have defined semantics.
- **attack_angle:** State evolution.
- **red_question:** 两条 APPROVED memory 互相矛盾时，你的 Current 实现怎么处理？如果今天文档主张 supersede/stale/quarantine，但历史代码没做，这个差异你怎么讲？
- **red_hidden_intent:** Force Current/Target distinction.
- **expected_evidence:** Current evidence; target design.

### Q037
- **claim_under_test:** Token budget management is concrete.
- **attack_angle:** Context engineering fundamentals.
- **red_question:** 你的 Zuno Context Builder 具体按什么预算选内容？有 token 阈值、排序分数或 truncation 策略吗？还是你真正做的只是“把两类已有内容拼进去”？
- **red_hidden_intent:** Prevent borrowing CodingAgent context compression work into Zuno claim.
- **expected_evidence:** Resume-specific implementation scope.

### Q038
- **claim_under_test:** OpenViking claim is properly bounded.
- **attack_angle:** Ownership / technology integration.
- **red_question:** Project 文档提到你接入过 OpenViking。它当时在 Memory / Context 里具体承担什么？你改了它、封装了它还是只完成配置接入？
- **red_hidden_intent:** Clarify integration depth.
- **expected_evidence:** Project ownership/history.

### Q039
- **claim_under_test:** Context slice has evidence of benefit.
- **attack_angle:** Measurement.
- **red_question:** 你有 `32 passed`，这证明的是行为正确还是证明回答质量提高？如果没有在线质量指标，简历应该怎样讲这条工作的结果？
- **red_hidden_intent:** Separate test evidence from product outcome.
- **expected_evidence:** Resume wording; test scope.

### Q040
- **claim_under_test:** Conversation history is not the product database.
- **attack_angle:** Architecture/product framing.
- **red_question:** 最新文档说 Conversation History 不是案件数据库。那你早期的 Session Memory / Long-term Memory 思路里，哪些内容现在应该删掉或降级成外部结构引用？
- **red_hidden_intent:** Test learning/evolution rather than defending old design.
- **expected_evidence:** Runtime/Application/Knowledge narratives.

## D. Research-to-Product / Capability Strategy

### Q041
- **claim_under_test:** Candidate does not appropriate team research.
- **attack_angle:** Research ownership.
- **red_question:** 事件抽取、JIA、LawBench、LJPCheck 等是导师/课题组成果。你面试时能说“我们做了这些研究”吗？哪种说法会越界？
- **red_hidden_intent:** Detect research ownership inflation.
- **expected_evidence:** Research lineage rules; Project ownership.

### Q042
- **claim_under_test:** JIA lineage maps to stable product semantics.
- **attack_angle:** Research-to-engineering.
- **red_question:** 为什么 JIA 最适合产品化成事件时间线/争议结构，而不是直接包装成一个“离婚案件 Agent”？这个判断是 Current 产品事实还是 Target 产品策略？
- **red_hidden_intent:** Test capability abstraction and claim status.
- **expected_evidence:** Research strategy + Current boundary.

### Q043
- **claim_under_test:** LawBench is used appropriately.
- **attack_angle:** Evaluation strategy.
- **red_question:** LawBench 为什么可以帮助 Provider Capability Profile，却不能直接决定“哪个模型最好”？如果一个模型 LawBench 总分高但某 Task Class 很差，你怎么路由？
- **red_hidden_intent:** Test task-scoped qualification concept.
- **expected_evidence:** Capability/Evaluation docs.

### Q044
- **claim_under_test:** LJPCheck is understood as functional testing lineage.
- **attack_angle:** Evaluation.
- **red_question:** LJPCheck 给 Zuno 的工程启示是什么？你如何避免把它写成“Zuno 已经拥有完整法律功能测试平台”？
- **red_hidden_intent:** Separate lineage from current implementation.
- **expected_evidence:** Research strategy; Current evidence.

### Q045
- **claim_under_test:** CMDL is not misused as autonomous judgment product evidence.
- **attack_angle:** Product ethics / task class.
- **red_question:** 为什么 CMDL 更适合作为复杂 Task Class / Eval 数据，而不是拿来宣传自动判决能力？
- **red_hidden_intent:** Test product boundary and responsible framing.
- **expected_evidence:** Research strategy.

### Q046
- **claim_under_test:** Capability boundary is semantics-first.
- **attack_angle:** Architecture abstraction.
- **red_question:** 一篇论文模型和一个 Capability 的边界怎么划？什么时候两个论文实现应该属于同一个 Capability，什么时候必须升 CapabilityVersion？
- **red_hidden_intent:** Test semantic stability reasoning.
- **expected_evidence:** Capability Part A/reference.

### Q047
- **claim_under_test:** Research artifact qualification has a real gate.
- **attack_angle:** Productization.
- **red_question:** 一个研究模型论文指标很好，接口也能跑。它进入真实案件路径前还差哪几步？哪一步是 Zuno 真正 Own、不能直接交给 Agent Host 的？
- **red_hidden_intent:** Test research-to-engineering chain.
- **expected_evidence:** Research-to-engineering traceability; Capability/Eval.

### Q048
- **claim_under_test:** Research assets remain valuable when foundation models improve.
- **attack_angle:** Strategic differentiation.
- **red_question:** 如果 GPT/Claude 明年在事件抽取、法条推荐上全面超过你们论文模型，葛季栋团队这些研究资产还剩什么产品价值？
- **red_hidden_intent:** Test whether value is in structures/eval rather than model weights.
- **expected_evidence:** Product strategy.

### Q049
- **claim_under_test:** Research-product feedback loop is not merely narrative.
- **attack_angle:** Measurement / governance.
- **red_question:** “真实工作 → 专家修改 → Regression → Research Question → Provider qualification”这条闭环，今天哪一段已经 Current？哪几段只是 Target？
- **red_hidden_intent:** Prevent future loop being presented as current data flywheel.
- **expected_evidence:** Module Current/Target/Gap.

### Q050
- **claim_under_test:** Case Workspace is justified as product view.
- **attack_angle:** Product design.
- **red_question:** 为什么 Case Workspace 比“聊天 + 引用 + 最终报告”更适合法律工作？这是不是你们自己想象的 UI，还是有真实用户行为证据？
- **red_hidden_intent:** Test product hypothesis vs proven need.
- **expected_evidence:** Application target + project history boundaries.

## E. Knowledge / RAG / GraphRAG

### Q051
- **claim_under_test:** Task-specific readiness is necessary.
- **attack_angle:** Knowledge readiness.
- **red_question:** 100 份材料里 98 份处理完、2 份 OCR 未完成。为什么不能让模型先回答再打一个“可能不完整”的提示？什么情况下必须阻断？
- **red_hidden_intent:** Challenge complexity of task-specific readiness.
- **expected_evidence:** Knowledge Part A; risk-based task scope.

### Q052
- **claim_under_test:** Retrieval miss is not negative fact.
- **attack_angle:** RAG semantics.
- **red_question:** “没有检索到违约通知”为什么不能直接回答“没有违约通知”？你需要什么覆盖证据才敢做否定性判断？
- **red_hidden_intent:** Test epistemic boundary.
- **expected_evidence:** Knowledge negative-claim discussion.

### Q053
- **claim_under_test:** DocumentVersion and KnowledgeGeneration separation is justified.
- **attack_angle:** Versioning.
- **red_question:** 为什么同一个合同 v3 换了 OCR/chunk/embedding 后要有新的 KnowledgeGeneration，而不是给索引加一个 `updated_at` 就够？
- **red_hidden_intent:** Test whether version abstraction pays for itself.
- **expected_evidence:** Knowledge generation rationale.

### Q054
- **claim_under_test:** Readiness is task-class scoped.
- **attack_angle:** Product efficiency.
- **red_question:** 条款定位和全案争议分析需要不同 readiness。这个规则由谁定义？如果每种 task class 都写一套依赖，不会变成配置地狱吗？
- **red_hidden_intent:** Stress governance/complexity cost.
- **expected_evidence:** Knowledge/Capability boundary; simplification.

### Q055
- **claim_under_test:** Citation remains stable across reindexing.
- **attack_angle:** Provenance.
- **red_question:** 今天 Retriever 找到 chunk 42，明天重新切分后 chunk 42 不存在了。历史 WorkProduct 的引用怎么还能回到当时材料？
- **red_hidden_intent:** Test CitationLineage vs WorkProduct binding.
- **expected_evidence:** Knowledge/Domain docs.

### Q056
- **claim_under_test:** GraphRAG claims are evidence-bounded.
- **attack_angle:** Measurement.
- **red_question:** 你们真正能证明的 GraphRAG 效果是什么？PF-031 那个 HotpotQA 小样本能支持哪些结论，不能支持哪些结论？
- **red_hidden_intent:** Prevent generalization from tiny smoke test.
- **expected_evidence:** Project provenance/eval evidence.

### Q057
- **claim_under_test:** Hybrid Retrieval remains respected baseline.
- **attack_angle:** Simplification / ablation.
- **red_question:** 如果 BM25+dense+rerank 在真实法律 task class 上已经达到要求，GraphRAG 还要不要留？你们的 kill condition 是什么？
- **red_hidden_intent:** Test deletion discipline.
- **expected_evidence:** Knowledge/Evaluation docs.

### Q058
- **claim_under_test:** Graph projections are rebuildable and versioned.
- **attack_angle:** Multi-store consistency.
- **red_question:** 新 DocumentVersion 到来时，向量索引更新了但图索引只更新一半，查询应该读哪一代？你怎么避免“混合世代”检索？
- **red_hidden_intent:** Test serving-generation atomicity.
- **expected_evidence:** Knowledge Target; current gap.

### Q059
- **claim_under_test:** Agentic Retrieval has a stop condition.
- **attack_angle:** Agent/RAG cost control.
- **red_question:** Agent 可以不断改 query、补检索。什么时候必须停？“模型觉得够了”为什么不够？
- **red_hidden_intent:** Test evidence-gap-based stopping.
- **expected_evidence:** Knowledge Agentic Retrieval section.

### Q060
- **claim_under_test:** Multiple stores do not imply global 2PC.
- **attack_angle:** Distributed systems.
- **red_question:** PostgreSQL、Object Store、Vector、Graph 都参与 Knowledge build，为什么不做全局事务？不用 2PC 时，你靠什么知道 generation 可以切 serving？
- **red_hidden_intent:** Test owner-local consistency model.
- **expected_evidence:** Knowledge generation/ServingPointer; architecture consistency.

### Q061
- **claim_under_test:** Failed generation cannot replace last-good serving.
- **attack_angle:** Failure recovery.
- **red_question:** v1 正在服务，v2 build 到一半失败。系统如何确保用户继续看到 v1？这个 Target 在 Current 代码里真的成立吗？
- **red_hidden_intent:** Surface known Slice D defect/current gap.
- **expected_evidence:** Evidence from #212/current Knowledge gap.

### Q062
- **claim_under_test:** Current Knowledge implementation has known isolation defect.
- **attack_angle:** Evidence honesty.
- **red_question:** 你们之前 diagnostic 已经发现 failed v2 会替换 last-good manifest。面试官问“那你们 Knowledge 架构现在就是错的吧”，你怎么回答？
- **red_hidden_intent:** Test ability to own implementation gap without collapsing target design.
- **expected_evidence:** Current evidence review; Target distinction.

## F. Runtime / Long-running Agent / Recovery

### Q063
- **claim_under_test:** Runtime target is not falsely current.
- **attack_angle:** Current/Target.
- **red_question:** PlanVersion、Single Controller、Replan Barrier 这些概念里，哪些你能证明 Current 已实现，哪些只是目标设计？
- **red_hidden_intent:** Stop target inflation.
- **expected_evidence:** Runtime Current/Target/Gap and evidence.

### Q064
- **claim_under_test:** Single Controller has a concrete failure case.
- **attack_angle:** Concurrency.
- **red_question:** 为什么需要 Single Controller？请给两个自治 Controller 同时处理新证据时会产生的具体冲突，而不是说“为了避免并发问题”。
- **red_hidden_intent:** Demand causal justification.
- **expected_evidence:** Runtime Part A.

### Q065
- **claim_under_test:** Immutable PlanVersion is worth complexity.
- **attack_angle:** Version semantics.
- **red_question:** 为什么不直接在当前 plan 上改后续 steps？PlanVersion 带来了哪些恢复或晚到结果判断能力？
- **red_hidden_intent:** Test minimality of immutable plan versions.
- **expected_evidence:** Runtime design rationale.

### Q066
- **claim_under_test:** Late results are not blindly discarded.
- **attack_angle:** Causation.
- **red_question:** 新 Plan 已经激活，旧 Plan 的一个昂贵分析分支晚到而且结果仍然正确。你是复用、丢弃还是重新验证？判断条件是什么？
- **red_hidden_intent:** Test freshness/causation semantics.
- **expected_evidence:** Runtime late-result rules.

### Q067
- **claim_under_test:** Domain commit vs stale checkpoint recovery is correct.
- **attack_angle:** Crash window.
- **red_question:** Domain transaction 已经提交，Runtime 还没写新 Checkpoint 就崩溃。重启第一步查什么？为什么不能直接 replay 当前 Step？
- **red_hidden_intent:** Test core cross-owner recovery invariant.
- **expected_evidence:** Domain/Runtime/Architecture recovery docs.

### Q068
- **claim_under_test:** Cancellation does not erase irreversible facts.
- **attack_angle:** Irreversibility.
- **red_question:** 用户在刚才那个 crash 之后又点了 Cancel。正式 WorkProduct 已经提交但 Runtime 不知道。Cancel 到底能取消什么？
- **red_hidden_intent:** Test forward-only correction.
- **expected_evidence:** Architecture irreversibility; Runtime cancellation.

### Q069
- **claim_under_test:** Retry/Replan/Reconcile are semantically distinct.
- **attack_angle:** Failure taxonomy.
- **red_question:** 给我各举一个必须 Retry、必须 Replan、必须 Reconcile 的例子，并解释如果用错会造成什么后果。
- **red_hidden_intent:** Test operational semantics.
- **expected_evidence:** Runtime/Effects docs.

### Q070
- **claim_under_test:** Long wait resumes with revalidation.
- **attack_angle:** TOCTOU / long-running.
- **red_question:** Agent 等专业人员两天后恢复。期间材料更新、模型资格变化、权限撤销。Resume 为什么不能从暂停代码下一行继续？
- **red_hidden_intent:** Test current-world revalidation.
- **expected_evidence:** Runtime/Security/Knowledge docs.

### Q071
- **claim_under_test:** Native Runtime is not defended by identity.
- **attack_angle:** Build/Buy.
- **red_question:** LangGraph/成熟 Agent Host 已经能 checkpoint、interrupt、并发。Zuno Native Runtime 真正需要 Own 的是什么？如果 Host 明天补齐 durable execution，你删什么？
- **red_hidden_intent:** Test semantic vs infrastructure ownership.
- **expected_evidence:** Runtime simplification; architecture Build/Buy.

### Q072
- **claim_under_test:** Retry budget is coordinated.
- **attack_angle:** Cost/reliability.
- **red_question:** SDK retry、Gateway fallback、Runtime reflection 都可能“再试一次”。谁拥有总预算？如果三层各重试 3 次，怎样避免 27 次调用爆炸？
- **red_hidden_intent:** Test layered retry amplification.
- **expected_evidence:** Runtime Budget + Gateway Usage.

### Q073
- **claim_under_test:** Persistent multi-agent is measurement-gated.
- **attack_angle:** Multi-Agent skepticism.
- **red_question:** 一个 Controller + parallel steps 已经能并行研究。永久 Specialist Agent topology 额外提供了什么？什么测量结果出现时你会删除它？
- **red_hidden_intent:** Test anti-overengineering stance.
- **expected_evidence:** Project/Runtime/Eval deletion rules.

### Q074
- **claim_under_test:** Recovery claims have actual evidence.
- **attack_angle:** Current evidence.
- **red_question:** 你们现在有哪些 crash / late result / failover 场景是真正通过测试证明的？哪些关键恢复路径仍然只有文档？
- **red_hidden_intent:** Identify implementation/evidence gap.
- **expected_evidence:** Evidence docs; Slice C/D findings.

## G. External Effects / Security / Tool Safety

### Q075
- **claim_under_test:** HTTP timeout is treated as unknown external reality.
- **attack_angle:** Distributed effects.
- **red_question:** POST 发出后本地 timeout。为什么状态不是 FAILED？请从 TCP/HTTP 能证明什么、不能证明什么开始回答。
- **red_hidden_intent:** Drill from architecture into network fundamentals.
- **expected_evidence:** Effects Part A + distributed systems reasoning.

### Q076
- **claim_under_test:** Idempotency key alone is insufficient.
- **attack_angle:** Exactly-once pressure.
- **red_question:** 如果远端支持 idempotency key，是不是就不需要 Reconcile 了？哪些情况下仍然必须确认远端事实？
- **red_hidden_intent:** Test overreliance on idempotency.
- **expected_evidence:** Effects semantics.

### Q077
- **claim_under_test:** Provider success + local receipt failure is handled conservatively.
- **attack_angle:** Failure injection.
- **red_question:** 远端已经成功，但本地保存 EffectReceipt 时数据库失败。Current diagnostic 证明系统会怎样？重启后会不会重复调用 executor？
- **red_hidden_intent:** Test knowledge of #210 evidence.
- **expected_evidence:** Slice C current evidence.

### Q078
- **claim_under_test:** Reconciliation convergence is not overstated.
- **attack_angle:** Implementation gap.
- **red_question:** 你们能创建 OPEN reconcile、能 escalation，但最终 RESOLVED / conclusive ReconciliationReceipt 的实现证据不足。那“Reconcile 能闭环”今天能不能写成 Current？
- **red_hidden_intent:** Force precise implementation status.
- **expected_evidence:** Slice C #209 gap.

### Q079
- **claim_under_test:** Mandatory audit is not falsely claimed current.
- **attack_angle:** Security/audit gap.
- **red_question:** diagnostic 证明 mandatory audit helper 有，但 Gateway 可以在 audit 缺失时继续 dispatch 并记录 EffectReceipt。面试官说“你的安全设计根本没接上”，你怎么回应？
- **red_hidden_intent:** Test handling of confirmed Target violation.
- **expected_evidence:** Slice C #205.

### Q080
- **claim_under_test:** SecurityEpoch revoke-before-send has positive evidence.
- **attack_angle:** Continuous authorization.
- **red_question:** 哪个测试能证明 SecurityEpoch 在发送前被撤销时系统 fail-closed？这个证据证明到哪一层，不能外推什么？
- **red_hidden_intent:** Test bounded positive evidence.
- **expected_evidence:** Slice C #203.

### Q081
- **claim_under_test:** Secret lease revocation is separately enforced.
- **attack_angle:** Secret/security.
- **red_question:** Secret 在 lease validation 前被撤销时发生什么？为什么这和普通 RBAC revoke 不是完全同一层问题？
- **red_hidden_intent:** Test secret lifecycle understanding.
- **expected_evidence:** Slice C #207/#208.

### Q082
- **claim_under_test:** Authorization is re-evaluated at protected boundaries.
- **attack_angle:** TOCTOU.
- **red_question:** 10:00 用户有权限，10:20 Worker 准备把正文发到模型时权限被撤销。入口鉴权为什么不够？你会在哪些动作前重做判断？
- **red_hidden_intent:** Test continuous authorization semantics.
- **expected_evidence:** Security/Application/Model/Effects docs.

### Q083
- **claim_under_test:** Approval is scoped and expiring.
- **attack_angle:** Governance.
- **red_question:** 专业人员批准过一次外发，之后材料版本、目标系统或 ToolVersion 变化。旧 Approval 还能不能继续用？为什么？
- **red_hidden_intent:** Test approval causation/freshness.
- **expected_evidence:** Security/reference contracts.

### Q084
- **claim_under_test:** Compensation is a new action, not rollback.
- **attack_angle:** Irreversibility.
- **red_question:** 已经确认外围系统收到错误结果，业务要求撤回。为什么不能把旧 EffectReceipt 改成 failed？补偿动作需要重新经过哪些边界？
- **red_hidden_intent:** Test historical truth and forward correction.
- **expected_evidence:** Architecture/Effects docs.

## H. Evaluation / Measurement / Evidence

### Q085
- **claim_under_test:** GraphRAG evaluation claims are disciplined.
- **attack_angle:** Measurement.
- **red_question:** 你们那次 HotpotQA `limit=5` GraphRAG rerun 最终只是对齐 baseline。为什么这仍然值得写进项目，而不是删掉？
- **red_hidden_intent:** Test ability to value negative/regression evidence.
- **expected_evidence:** Evaluation PF-031 narrative.

### Q086
- **claim_under_test:** Research benchmarks do not imply current product qualification.
- **attack_angle:** Evidence boundary.
- **red_question:** LawBench/LJPCheck/CMDL 都出现在新战略里。今天有没有任何一个已经成为 Zuno release gate？如果没有，怎么避免面试官觉得你只是拿论文给项目贴金？
- **red_hidden_intent:** Test honest use of research lineage.
- **expected_evidence:** Research strategy status and Current gaps.

### Q087
- **claim_under_test:** HumanDecision is not automatic ground truth.
- **attack_angle:** Data flywheel validity.
- **red_question:** 专业人员改了模型输出，为什么不能直接把修改版当训练真值？哪些偏好、策略性写法或人类错误会污染数据？
- **red_hidden_intent:** Test governance of expert feedback.
- **expected_evidence:** Domain/Evaluation product loop docs.

### Q088
- **claim_under_test:** Regression data does not remain a clean holdout.
- **attack_angle:** Eval methodology.
- **red_question:** 线上 Bad Case 被加入 Regression Suite 后，下一版 Prompt 专门修了它。这条 case 还能算独立 holdout 吗？你如何维持评测可信度？
- **red_hidden_intent:** Test contamination awareness.
- **expected_evidence:** Evaluation methodology; generic testing knowledge consistent with docs.

### Q089
- **claim_under_test:** LLM Judge is used only where appropriate.
- **attack_angle:** Eval reliability.
- **red_question:** 哪些指标必须 deterministic checker，哪些可以交给 LLM Judge？Judge 本身漂移时怎么办？
- **red_hidden_intent:** Test evaluator hierarchy.
- **expected_evidence:** Evaluation Part A.

### Q090
- **claim_under_test:** Product value metrics are decision-relevant.
- **attack_angle:** Business measurement.
- **red_question:** 对“争议焦点识别 + 证据—事实—法律依据审查”这个第一产品切片，你会选哪 5 个指标证明它真的提高专业生产力，而不是只让模型分数更高？
- **red_hidden_intent:** Test product measurement design.
- **expected_evidence:** Research strategy + Evaluation target; no invented numbers.

### Q091
- **claim_under_test:** Release PASS is not Production Ready.
- **attack_angle:** Qualification boundary.
- **red_question:** 某 Provider 在 DatasetVersion X 上全部 PASS，为什么仍然不能说 Production Ready？还缺哪些系统层证据？
- **red_hidden_intent:** Test layered qualification.
- **expected_evidence:** Evaluation/Project evidence boundaries.

### Q092
- **claim_under_test:** Complexity is removed through ablation/kill tests.
- **attack_angle:** Simplification.
- **red_question:** GraphRAG、Memory、Reflection、Multi-Agent、Native Runtime 里，你会先给哪一个做 kill test？baseline 怎么选，什么结果会真的触发删除？
- **red_hidden_intent:** Test engineering courage and measurable deletion conditions.
- **expected_evidence:** Evaluation complexity deletion section.

## I. Build / Buy / Scale / Fundamentals

### Q093
- **claim_under_test:** Zuno is not duplicating generic platforms.
- **attack_angle:** Build/Buy.
- **red_question:** Dify、Coze、WorkBuddy、LangGraph、OpenAI/Anthropic managed agent infrastructure 越来越强。Zuno 今天真正不能外包的 3 个东西是什么？
- **red_hidden_intent:** Force semantic differentiation.
- **expected_evidence:** Project/architecture/research strategy.

### Q094
- **claim_under_test:** Framework capability and business authority are separated.
- **attack_angle:** Framework boundary.
- **red_question:** LangGraph 能 checkpoint、interrupt、Send、Reducer。为什么 Zuno 还需要 Runtime/Domain/Effects 这些概念？哪些可以直接交给 LangGraph，哪些不能？
- **red_hidden_intent:** Test framework reuse without authority leakage.
- **expected_evidence:** Architecture/Runtime/Domain/Effects.

### Q095
- **claim_under_test:** Generic agent harness commoditization changes architecture priorities.
- **attack_angle:** Strategic simplification.
- **red_question:** 如果 Managed Agent Harness 已经提供长会话、sandbox、subagent、context compaction、durable session，Zuno 自研层应该缩到什么程度？
- **red_hidden_intent:** Test response to platform evolution.
- **expected_evidence:** Research strategy / Build-Buy.

### Q096
- **claim_under_test:** Architecture scales down as well as up.
- **attack_angle:** Simplification.
- **red_question:** 用户量少 10 倍、只有一个法院、每天几十个任务时，九个责任域里哪些逻辑边界仍必须保留，哪些实现机制应该直接 defer？
- **red_hidden_intent:** Test logical vs deployment complexity.
- **expected_evidence:** Architecture deployment/simplification; module boundaries.

### Q097
- **claim_under_test:** Model Gateway can shrink.
- **attack_angle:** YAGNI.
- **red_question:** 如果长期只用一个私有模型，没有多 Provider、没有地域路由，Model Gateway 还剩什么？什么时候它应该缩成一个 adapter？
- **red_hidden_intent:** Test abstraction deletion condition.
- **expected_evidence:** Model Gateway simplification.

### Q098
- **claim_under_test:** Nine logical modules do not imply microservices.
- **attack_angle:** Deployment/system design.
- **red_question:** 你会怎么把九个责任域部署成进程/Worker？为什么不是九个微服务？第一个真正值得独立拆出去的部分会是哪一个，取决于什么证据？
- **red_hidden_intent:** Test logical vs physical architecture.
- **expected_evidence:** Architecture deployment section.

### Q099
- **claim_under_test:** Scale claims remain honest without measurements.
- **attack_angle:** Performance fundamentals.
- **red_question:** 现在没有真实 QPS、P95、Token、Cost、HA/DR 数据。如果面试官问“10 倍流量先炸哪里”，你能回答设计推断到什么程度，又必须在哪一步停下来承认没测过？
- **red_hidden_intent:** Test calibrated system-design reasoning.
- **expected_evidence:** Architecture scale/backpressure + Unknowns.

### Q100
- **claim_under_test:** Candidate can summarize strongest defensible project value and delete excess complexity.
- **attack_angle:** Hiring-manager close.
- **red_question:** 如果只允许你保留 Zuno 简历里的两条贡献、删除今天 Target 里一半复杂机制，并用 90 秒说服我这个项目值得招你，你保留什么、删什么、为什么？
- **red_hidden_intent:** Force prioritization, ownership honesty, and simplification into one close question.
- **expected_evidence:** Resume personal contributions + Project/Architecture deletion conditions.

## Red Batch Freeze

- Question count: 100
- Questions frozen after this commit.
- Blue must not use Red calibration corpus or hidden attack metadata as answer sources.
- Any follow-up generated from Blue answers belongs to Batch 002.
