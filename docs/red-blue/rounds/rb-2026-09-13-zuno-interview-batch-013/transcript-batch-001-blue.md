# Round #013 — Batch 001 — Blue

Status: `CLOSED_BOOK_ANSWERED_AND_ARCHIVED`  
Answer count: **100**

Blue sources are restricted to the exact resume snapshot plus the manifest allowlist. No interview-calibration corpus or Red hidden attack metadata is used as answer evidence.

## A. Project Reality / Causality / Resume Claim Strength

### Q001
**answer:** 历史上能确认的是已有系统、Internal Demo、客户/智慧法院项目组 Demo、法院侧人员测试、Pilot Validation，以及“回答质量还需要提高”的反馈。今天 Current 只能按代码、测试、Migration 和 Evidence 说有限实现；材料版本、Formal Admission、完整跨 Owner recovery 等很多内容属于 Target。历史客户当时是否已经暴露这些具体架构问题，文档明确保持 Unknown，不能用今天设计反推。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md`; `docs/evidence/README.md`.

### Q002
**answer:** 当前没有恢复那条客户质量反馈对应的具体 Bad Case、根因和前后指标，因此我不能说后来某个 RAG、Memory 或 Runtime 改造就是这条反馈的直接修复。能说的是领域上这些风险存在、项目历史上确有质量反馈；两者之间的具体因果仍然 Unknown。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-017.

### Q003
**answer:** 历史证据只能确认项目进入过法院侧人员测试和 Pilot，无法恢复完整用户角色、逐步操作流程或验收脚本。今天文档描述的 Case Workspace、材料就绪、候选分析、专业复核、Formal WorkProduct、交付是一套 Target 产品流程，不应冒充历史 Pilot 的逐步实录。

**source_trace:** `docs/project/README.md`; `docs/modules/application/README.md`; `docs/governance/project-fact-provenance.md`.

### Q004
**answer:** 对“历史真实任务是否已经证明 Generic Host + Hybrid RAG + 人审不够”，目前没有直接对照实验，所以我不会声称已经证明。Target 的判断是：简单问答继续用受控 RAG；只有材料版本、长期运行、正式结果和现实副作用进入以后，领域状态与恢复语义才有额外价值。这是架构假设，优势仍需 A/B/C 对照测量。

**source_trace:** `docs/project/README.md`; `docs/architecture/architecture.md`; `docs/evidence/README.md`.

### Q005
**answer:** Pilot 只能证明项目到过试点验证阶段。真实用户数、持续时长、QPS、SLO、HA/DR、正式验收、故障率和完整运维证据都没有建立，因此不能写成 Production 或 Production Ready。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-019/PF-020/PF-022; `docs/evidence/README.md`.

### Q006
**answer:** 比较合理的价值指标包括：Evidence/Citation 正确与充分、专业人员接受/修改/拒绝模式、形成 review-ready WorkProduct 的时间，以及复杂任务的 recovery correctness / duplicate-effect 等。今天这些正式业务指标没有完整 baseline；Current Eval 明确是 `MEASUREMENT_BLOCKED`，所以只能定义测量框架，不能报收益数字。

**source_trace:** `docs/modules/evaluation/README.md`; `docs/evidence/current-eval-baseline.md`; `docs/evidence/README.md`.

### Q007
**answer:** “法律智能 Agent 平台”是历史/简历中的项目定位；最新 Target 更明确地把复杂工作的长期产品视图放在 Matter / Case Workspace，Agent 是组织检索、工具和长任务执行的机制。面试时我会说明 Agent 是执行技术，不是业务 Authority；如果最终固定 workflow 足够，Agent Runtime 可以缩薄。

**source_trace:** exact resume snapshot; `docs/project/README.md`; `docs/modules/application/README.md`; `docs/modules/runtime/README.md`.

### Q008
**answer:** 当前允许来源不能证明某篇葛季栋/LIPLAB 论文的方法已经进入我参与的具体历史版本。项目文档讲这些研究，是作为团队研究谱系和未来 Capability 产品化来源；它明确禁止从“论文存在”推出“Current 已集成”。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-003.

### Q009
**answer:** 我加入时项目已经有代码和简单自研前端，不是我从零立项。能够确认的个人范围包括部分 Agent 开发、Memory 第一批重要工作、OpenViking 在 Memory/Context 区域的接入参与、Tool Calling Strategy 相关开发，以及数据库查看/调试；不能扩大成整个 Runtime、全部 RAG/GraphRAG、数据库总体设计或完整产品由我独立完成。

**source_trace:** exact resume snapshot; `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-007–PF-014.

### Q010
**answer:** 现有材料不能证明用户已经长期依赖某个 Zuno 输出完成正式工作。我会表述为“经历过 Demo、法院侧人员测试和 Pilot Validation”，并明确缺少正式生产、稳定用户规模和验收数据，而不是说“已被法院生产使用”。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-018–PF-020.

### Q011
**answer:** 能确认的是我加入时已有系统和前端，以及后来公开历史里恢复出的部分 Agent/Tool/Context 任务。历史完整依赖、部署拓扑和 Pilot 技术栈没有恢复，今天 main 的依赖不能直接当作 3 月架构。因此无法给出完整“当时 vs 今天”的组件级对照，只能逐项说有证据的变化。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-008/PF-021/PF-027.

### Q012
**answer:** 这项工作的价值不在于声称我历史上实现了九模块，而在于把“历史事实、当前代码证据、Target 设计、Unknown”拆开，避免错误的实现/生产 Claim，并为后续验证明确故障窗口和复杂度删除条件。简历已经把它写成“架构与证据复盘”，不是“主导总体架构落地”。

**source_trace:** exact resume snapshot; `docs/project/README.md`; `docs/evidence/README.md`.

### Q013
**answer:** 去掉技术名词后，Zuno 的目标是把不断变化的案件材料和研究能力转成可追溯的专业候选，让专业人员形成长期可解释的工作成果，并在任务等待、权限变化和外部动作失败时仍能知道什么真实发生过。简单问题仍然允许只用普通检索和一次生成。

**source_trace:** `docs/project/README.md`; `docs/architecture/architecture.md`.

### Q014
**answer:** 材料固定、步骤明确、没有长期等待/动态输入/现实副作用时，固定 workflow 完全可以替掉 Agent 控制而不影响 Domain、Knowledge、Security 等业务边界。真正需要动态控制的主要是运行过程中前提变化后要 Replan、等待恢复、并行晚到结果重验收等任务；如果这些场景没有收益证据，Native Runtime 应继续缩薄。

**source_trace:** `docs/project/README.md`; `docs/modules/runtime/README.md`; `docs/architecture/architecture.md`.

## B. Personal Ownership — Agent / MCP / Tool Calling

### Q015
**answer:** 简历和 PF-032 支持两段历史工作：2026-04-15 `GeneralAgent` 的 Tool/MCP binding 从 MCPAgent-as-Tool 收口到具体 MCP Tools，并在调用期注入用户配置；2026-04-28 的 Workspace 层保留 deterministic direct route / ReAct fallback，并做 MCP hardening。允许来源不足以把这两段扩大成完整 Tool Runtime 或今天的 Effects 体系。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-012/PF-032.

### Q016
**answer:** 允许来源能确认“嵌套 MCPAgent-as-Tool 被收口”和后续 recursion/参数解析 hardening，但没有保存足够的原始需求、Trace 或业务失败来证明唯一根因是 token、权限或延迟中的哪一个。最稳的说法是：这是调用层次收口并伴随具体 bug 修复，业务收益和原始故障因果仍缺真实运行证据。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032.

### Q017
**answer:** 目前能证明的是历史代码改动与回归测试 artifact，不是调用成功率、token、P95 或用户质量提升。项目事实台账明确不允许把这两段历史实现扩写成生产稳定性或客户收益。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-012/PF-032; exact resume snapshot.

### Q018
**answer:** 历史 Claim 只到“调用期注入用户级 MCP 配置”；允许文档没有完整恢复它怎样在用户/Workspace/Run 间绑定，以及 Worker 重启后的传播协议。因此我不能把今天 Security/Runtime Target 的稳定身份和持续授权反写成当时已实现，只能把多租户/恢复作为现有证据缺口。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032; `docs/modules/security/README.md` as Target only.

### Q019
**answer:** 文档能确认 Workspace 层保留 deterministic direct route 与 ReAct fallback，但没有在允许来源里冻结当时完整的路由判定表。设计原则上，确定且可验证的调用优先 deterministic，真正需要模型解释/选择时才用 ReAct；但我不能把这个原则冒充成当时所有分支的精确 Current 条件。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032; `docs/modules/runtime/README.md` for current design principle.

### Q020
**answer:** Canonical 允许来源只记录“custom MCP name recursion 被修复”，没有恢复递归具体发生在注册、解析还是包装哪一层。我不能凭印象补根因；要把这个问题回答到代码级，需要回到 PF-032 指向的历史 commit/test artifact。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032; `unknown_or_unsupported: exact root-cause location not preserved in Blue allowlist`.

### Q021
**answer:** 允许来源同样只确认“高德天气参数解析问题被修复并有对应 test artifact”，没有足够信息区分是模型参数生成、MCP schema 还是 adapter 转换的精确根因。我会明确停在这里，不把后来 Target 的 schema/version 机制当历史解释。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032; `unknown_or_unsupported`.

### Q022
**answer:** PF-032 支持存在 historical test artifact，但 Canonical 事实层没有把每个断言、测试粒度和是否依赖模型固定下来。能说“新增了对应回归用例”，不能自动说“当时完整 CI 通过”或“真实 MCP E2E 已验证”。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032.

### Q023
**answer:** 精确表述是“参与过 Tool Calling Strategy，并能由公开历史恢复两段具体改动”。不能回答“整个 Tool Runtime 是我写的”；今天 PreparedAction/Approval/EffectReceipt/Reconcile 等体系属于后续 Current/Target 边界，不应反向算作 4 月个人实现。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-012/PF-032; `docs/project/README.md`; exact resume snapshot.

### Q024
**answer:** 对 Memory，PF-029 已经明确恢复到单提交 PR #8 和 focused tests；对 Tool Calling，PF-032 恢复了 4 月两段 historical commits/test artifact，但当前简历没有直接列 commit/PR。若面试需要一条最可核验的个人闭环，我会优先讲已有明确 provenance 的任务，并承认 Tool Calling 的业务结果仍未恢复。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-029/PF-032; exact resume snapshot.

### Q025
**answer:** 项目事实层只确认开发期间学习和接触过 LangGraph，不能推出完整 Target Runtime 由我实现。Current Runtime Evidence 能证明今天代码路径存在 AgentRunStore/checkpoint/Agent Core graph 等基础，但那是仓库 Current，不等于个人历史 Ownership；PlanVersion/Single Controller 等仍主要是 Target 语义。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-014; `docs/evidence/current-runtime-baseline.md`; `docs/modules/runtime/README.md`.

### Q026
**answer:** 4 月历史实现遇到 MCP schema 在任务中途变化时的完整行为没有在允许来源中恢复。今天 Target 的原则是：Tool/Capability 版本变化需要重新做兼容/资格检查，旧计划结果不能因为格式还能解析就默认继续执行；但这个回答必须标成 Target，而非当时 Current。

**source_trace:** `docs/modules/capability/README.md`; `docs/modules/effects/README.md`; `docs/governance/project-fact-provenance.md` PF-032.

### Q027
**answer:** 我本人历史切片能确认用户级 MCP 配置注入，但不能证明 SecurityEpoch、持续授权、PreparedAction 等后续机制当时已存在。持续授权目前有部分 Current fault evidence，但不是这条个人 4 月实现的组成部分。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032; `docs/evidence/README.md`; `docs/governance/effect-security-slice-c-review.md`.

### Q028
**answer:** 它值得写的原因主要是把 Tool 调用从额外 Agent 嵌套收回更直接的调用层，并修复 Workspace MCP routing 的具体兼容问题；这是可解释的工程简化和 hardening。当前证据不支持把它包装成“显著提升用户质量/性能”，因此简历也没有写提升百分比。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-032.

## C. Personal Ownership — Context / Memory

### Q029
**answer:** PF-029 与简历支持：在 `GeneralAgent.prepare_context()` 接入同 scope task summary 和仅 `APPROVED` 的 structured memory，同时补 Context Pack policy、source-id trace 与 review/provenance gate。它是一个 bounded readback hardening slice，不是整个 Memory 系统从零实现。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-029/PF-030.

### Q030
**answer:** Canonical 事实层只记录“same scope”，没有在允许来源里冻结 scope 到底是 User/Workspace/Matter/Task 中哪一个字段组合。我不能现场发明；如果要回答实现级定义，需要回到 PF-029 对应代码和 tests。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-029; `unknown_or_unsupported: exact scope key not preserved in canonical prose`.

### Q031
**answer:** 我能证明的是 read path 只消费 `APPROVED` structured memory，并有 review gate；不能证明我实现了完整 Candidate→Approved 审核生命周期。更完整 Memory authority 不能从这个 slice 自动推导。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-029/PF-030.

### Q032
**answer:** 允许来源没有证明真实产品里 review queue 的吞吐、谁审批以及没有人审时如何自动推进。因此这属于历史/产品化 Unknown；不能因为 Target 需要 review gate，就声称已有成熟人工运营闭环。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-029/PF-030; `docs/project/README.md` Unknown boundaries.

### Q033
**answer:** 能确认的是 Context Pack 增加了 source-id trace，用来保留被装入上下文的信息来源。Canonical 文档没有列出它可追到的所有物理表/消息层级，所以我只会说“支持来源追踪和 focused provenance tests”，不扩写成完整全链路 provenance。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-029.

### Q034
**answer:** 正式 DocumentVersion/Domain facts 是更强的业务 Authority，Memory 只应作为工作上下文；旧 Memory 不能覆盖新材料事实。至于 PF-029 历史实现是否已经做了跨 Domain 版本的自动 stale 处理，允许来源没有证明，所以 Current 不能承诺。

**source_trace:** `docs/project/README.md`; `docs/modules/domain/README.md`; `docs/modules/runtime/README.md`; PF-029 for historical scope.

### Q035
**answer:** 今天 Target 明确要求工具/外部内容不能因为被放入 Context 就取得 Security Authority；但 PF-029 只证明 scope/approval/provenance 的 focused slice，没有 Current evidence 证明我那条历史实现已经完成 prompt-injection instruction/data 隔离。我会把这点列为未证明，而不是借用安全设计补历史。

**source_trace:** PF-029; `docs/modules/security/README.md`; `docs/modules/runtime/README.md`.

### Q036
**answer:** Current historical slice对两个 APPROVED memory 冲突的完整处理没有在 canonical sources 中证明。Target 原则是 Memory 不应成为正式案件事实源，冲突和最新业务事实应回到对应 Owner；如果需要长期 Memory 生命周期，应显式 stale/supersede，而不是原地覆盖，但不能说 PF-029 已完成这些。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/domain/README.md`; `docs/governance/project-fact-provenance.md` PF-029/PF-030.

### Q037
**answer:** Zuno 简历这条没有声称实现 token 阈值、裁剪打分或压缩策略；这些更完整的上下文治理是另一个 Coding Agent 项目里的个人实现，不能借来填 Zuno。Zuno 这里能证明的是 bounded Context Builder/readback slice。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-029/PF-030.

### Q038
**answer:** PF-011 只支持“我参与过 OpenViking 在 Memory/Context 区域的接入”。公开 Git 尚未恢复具体 SDK/Adapter/数据结构和生产使用方式，所以我不能说改过 OpenViking 核心、也不能给出实现细节。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-011.

### Q039
**answer:** `32 passed` 证明的是那组 focused tests 覆盖的 scope/approval/provenance 行为，没有证明最终回答质量提高。简历合理的结果表述是“用 focused tests 验证边界”，而不是“提升法律答案准确率”。

**source_trace:** exact resume snapshot; PF-029.

### Q040
**answer:** 最新 Target 把原始材料、案件专业结构、正式判断放回 Knowledge/Domain 等外部持久 Owner；Runtime Memory/summary 只保存执行需要的工作上下文。也就是说，任何试图把“案件真相”长期塞进 Conversation/Session Memory 的设计都应该降级或删除，Context 应能从外部事实重建。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/application/README.md`; `docs/modules/knowledge/README.md`; `docs/modules/domain/README.md`.

## D. Research-to-Product / Capability Strategy

### Q041
**answer:** 不能把导师/课题组论文说成“我做的研究”。合理说法是“项目处在 LIPLAB 智慧司法研究工程化背景下，我参与其中的 Agent/Memory/Tool 等工程任务；论文成果属于导师/课题组研究资产”。

**source_trace:** `docs/project/README.md`; `docs/governance/project-fact-provenance.md` PF-003/PF-009–PF-014.

### Q042
**answer:** 把 JIA 一类研究抽象成事件时间线/冲突/争议结构，是今天 Target 产品化策略：稳定专业结构比绑定一个“离婚 Agent”更容易更换 Provider、复用和审计。它不是 Current UI 已经上线这些结构的证明。

**source_trace:** `docs/project/README.md`; `docs/modules/knowledge/README.md`; `docs/modules/capability/README.md`.

### Q043
**answer:** LawBench 类结果适合提供按任务拆分的能力画像，而不是一个全局排行榜。05 的资格模型要求 Provider 对具体 Task Class、材料/风险条件有证据；07 的 Model Role 路由也不能越权扩大法律 Capability Eligibility。

**source_trace:** `docs/project/README.md`; `docs/modules/capability/README.md`; `docs/modules/model-gateway/README.md`; `docs/modules/evaluation/README.md`.

### Q044
**answer:** 文档把 LJPCheck 的价值定位为“headline accuracy 不足，需功能测试/失败模式回归”的方法论来源。Current Eval 仍是 `MEASUREMENT_BLOCKED`，所以不能说 Zuno 已建成完整法律 functional-testing release gate。

**source_trace:** `docs/project/README.md`; `docs/modules/evaluation/README.md`; `docs/evidence/current-eval-baseline.md`.

### Q045
**answer:** CMDL 更适合提醒系统复杂多主体任务不能由简单单主体分数代表，因此可用于扩展 Task Class/Eval 边界。Zuno 的产品定位明确不是 Autonomous Judge，机器结果保持候选并需要专业判断，因此不应拿数据集存在去宣传自动判决。

**source_trace:** `docs/project/README.md`; `docs/modules/domain/README.md`; `docs/modules/evaluation/README.md`.

### Q046
**answer:** 如果两个实现对输入、输出、unsupported/failure 语义和适用范围承担同一个专业承诺，可以是同一 Capability 的不同 Provider。若“事件”的业务定义、支持范围或失败语义本身变化，就应形成新的 CapabilityVersion，而不是藏在相同 JSON 下。

**source_trace:** `docs/modules/capability/README.md`.

### Q047
**answer:** 研究模型进入真实任务至少要经过稳定语义定义、接口/Conformance、按 Task Class 的质量 Qualification、当前 Eligibility/安全条件，再由 Runtime 调用；输出仍只是 Candidate。Zuno 真正需要 Own 的是法律 Capability 语义、资格和 Formal business boundary，而 Generic Host 可以承载调用和通用执行。

**source_trace:** `docs/modules/capability/README.md`; `docs/modules/domain/README.md`; `docs/project/README.md`.

### Q048
**answer:** 即使基础模型全面超过旧论文模型，团队仍有价值的资产是法律任务定义、专业中间结构、标注/benchmark 方法、失败模式、专家反馈与 qualification 体系。Provider 可以替换，稳定专业语义和评价数据不应随模型一起消失。

**source_trace:** `docs/project/README.md`; `docs/modules/capability/README.md`; `docs/modules/evaluation/README.md`.

### Q049
**answer:** Current 可以证明有限的研究算法/Agent/Knowledge/Tool/Eval 基础以及部分个人 Context/Tool slices；“真实专业反馈→治理后的 regression→研究问题→Provider qualification→受控 release”完整闭环没有 Current 证据。09 和 05 目前把它写成 Target/Gap。

**source_trace:** `docs/project/README.md`; `docs/modules/domain/README.md`; `docs/modules/evaluation/README.md`; `docs/evidence/README.md`.

### Q050
**answer:** Case Workspace 的架构理由是复杂工作包含材料、事件/证据候选、开放问题、人类决定、WorkProduct validity 等长期结构，聊天记录不适合作为唯一持久视图。历史确有法院侧测试/Pilot，但没有恢复足够 UX 行为证据证明用户已经验证了这种具体 Workspace 形态，所以它仍是 Target 产品设计。

**source_trace:** `docs/modules/application/README.md`; `docs/project/README.md`; PF-018/PF-019.

## E. Knowledge / RAG / GraphRAG

### Q051
**answer:** 系统不必因为 2 份材料未完成就一律阻断；关键是当前 Task Class 是否依赖它们。条款定位可能可以继续，全案金额/争议判断如果缺失材料可能改变结论，就应保持 partial/blocked/abstain，而不是只靠一个轻提示把不完整答案升级成完整结论。

**source_trace:** `docs/modules/knowledge/README.md`.

### Q052
**answer:** retrieval miss 只能证明当前 route 没找到，不能证明全案不存在。做否定判断至少要知道要求覆盖的材料 Scope 已准备、必要 route/来源被检查、关键缺口已经处理；否则只能说“当前检索未发现”。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/project/README.md`.

### Q053
**answer:** `updated_at` 只能说某些派生变了，无法标识一套 OCR/chunk/embedding/graph 结果是否属于同一完整、可验证版本。KnowledgeGeneration 给可重建派生一个整体身份，使后台构建失败时能继续服务上一代，并让查询/引用知道使用了哪套配方和结果。

**source_trace:** `docs/modules/knowledge/README.md`.

### Q054
**answer:** readiness 规则跟 Task Class/Scope/required capabilities 相关，通常应由 Knowledge 消费上层任务需求而不是每个调用点散写。配置复杂度是真实成本，所以文档也明确：简单小语料任务应缩小到基础 lexical/dense index 和最小 readiness，不为所有问题建立完整 profile。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/modules/capability/README.md`.

### Q055
**answer:** 历史 WorkProduct 不应绑定“当前 chunk 42”这种可重建位置，而应在正式接纳时绑定稳定 DocumentVersion/SourceSpan 或可恢复位置。Knowledge 的 CitationLineage 解释候选当时怎样找到；Domain 的正式引用绑定保存 WorkProduct 真正采用的材料版本和位置。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/modules/domain/README.md`.

### Q056
**answer:** PF-031 能证明的很窄：HotpotQA retrieval-only `limit=5` smoke 中，local GraphRAG sampled Recall@5 曾从 baseline 1.00 回退到 0.80；经过 fusion/seed/alias/ranking 修复后，同日 rerun 回到 1.00，并记录 MRR/FullChainHit。它不能证明 GraphRAG 普遍优于 baseline、不能解释客户质量反馈，也不能证明各改动的独立因果贡献或生产质量。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-031; `docs/modules/evaluation/README.md`.

### Q057
**answer:** 如果真实法律 Task Class 上 Hybrid Retrieval 已达到质量门槛，而 GraphRAG 没有稳定增加需要的证据覆盖或多跳能力，就应该关闭默认图路径或只留少数 query class。09 要用 baseline/ablation/kill test 让实现存在不等于永久保留。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/modules/evaluation/README.md`.

### Q058
**answer:** Target 是后台构建新的 KnowledgeGeneration，所有必要 artefact/manifest 校验完成后再原子切 ServingPointer；查询只读已经激活的一代，避免 vector/graph 混世代。当前完整 generation lifecycle 和原子 serving switch 未被 Evidence 证明，因此这是设计目标，不是 Current 保证。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/evidence/README.md`.

### Q059
**answer:** 继续检索应绑定一个尚未满足的 evidence gap，并检查新一轮是否真的带来新的有效材料；当任务所需范围满足、增量信息很少或预算达到边界就应停止。“模型主观觉得再搜一下可能更好”不是充分停止/继续条件。

**source_trace:** `docs/modules/knowledge/README.md`.

### Q060
**answer:** 不做跨 PostgreSQL/Object/vector/graph 的全局 2PC，而是各 Store 完成自己的可重建写入和校验，最后只原子改变“哪一代对外服务”的小指针。这样强一致缩在 owner-local 边界，派生 Store 可重试/重建，避免最慢依赖拖进全局事务。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/architecture/architecture.md`.

### Q061
**answer:** Target 明确要求 failed v2 不得替换 last-good v1；但在本轮 Blue allowlist 的 `docs/evidence/` 和 canonical governance 中，我没有找到 Q061 所述 #212/“failed v2 replaces last-good manifest”的 Current 记录。因此我只能回答 Target 行为和“generation activation 未 implementation-proven”，不能确认这个具体 diagnostic premise。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/evidence/README.md`; `unknown_or_unsupported: #212 diagnostic not present in allowed canonical evidence`.

### Q062
**answer:** 在允许来源内，我不能确认“当前代码已经被 #212 证明错误”这个具体事实；如果该 diagnostic 以后进入 canonical Evidence，应把它描述成 Current implementation defect，而不是推翻 Target 的 last-good serving invariant。现阶段只能说完整 generation isolation/activation 仍未证明。

**source_trace:** `docs/modules/knowledge/README.md`; `docs/evidence/README.md`; `unknown_or_unsupported`.

## F. Runtime / Long-running Agent / Recovery

### Q063
**answer:** Current 能证明 AgentRun application/service/store、checkpoint、部分 resume/cancel 和 unknown-effect 入口等基础。不可变 PlanVersion、Single Controller、Replan Barrier、完整跨 Owner recovery 等在 Runtime README 中仍属于 Target/Gap，不能因为设计写得完整就说已实现。

**source_trace:** `docs/evidence/current-runtime-baseline.md`; `docs/modules/runtime/README.md`; `docs/evidence/README.md`.

### Q064
**answer:** 两个 Controller 同时看到新材料，一个可能激活新计划并取消旧分支，另一个仍基于旧前提继续派后续 Step；重启后会出现两个“当前计划”和不可解释的 late result 归属。Single Controller 只串行化控制事实，不阻止 Worker/模型并行。

**source_trace:** `docs/modules/runtime/README.md`.

### Q065
**answer:** 原地改 plan 会让已经在途的 Worker 无法证明自己基于改前还是改后的依赖。PlanVersion 把运行前提冻结为可识别身份，使 late result 能按材料/计划因果重新验收，也让恢复时知道哪些未来工作已被哪次 Replan 取代。

**source_trace:** `docs/modules/runtime/README.md`.

### Q066
**answer:** 不应因为来自旧 Plan 就一律丢，也不能因为结果质量高就直接复用。要比较它绑定的输入/材料版本、Capability/安全条件和当前计划依赖；前提仍成立时可以重新验收复用，已经 stale 时丢弃或重算。

**source_trace:** `docs/modules/runtime/README.md`; `docs/architecture/architecture.md`.

### Q067
**answer:** 重启后先查询 Domain 是否已经存在匹配的正式提交/完成证明。已经提交就修 Runtime projection/checkpoint，不 replay Formal Admission；只有 Domain 确认没有提交，才重新进入当前有效的提交路径。Checkpoint 证明控制进度，不拥有业务完成事实。

**source_trace:** `docs/modules/domain/README.md`; `docs/modules/runtime/README.md`; `docs/architecture/architecture.md`; `docs/evidence/README.md` notes this owner-first path is not fully implementation-proven.

### Q068
**answer:** Cancel 只能停止还没有不可逆发生的未来工作。WorkProduct 如果实际上已经正式提交，就仍是历史事实；Cancel 可以阻止后续 Step/交付或触发新的失效/撤回流程，但不能把 Domain 记录改成“从没发生”。

**source_trace:** `docs/architecture/architecture.md`; `docs/modules/runtime/README.md`; `docs/modules/domain/README.md`.

### Q069
**answer:** Provider 临时 503、输入和语义不变时是 Retry；新证据改变任务前提时要 Replan；POST 已发出但响应丢失、需要查清远端是否已执行时是 Reconcile。把 Replan 当 Retry 会反复算旧世界，把 Reconcile 当 Retry 可能重复现实动作。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/effects/README.md`.

### Q070
**answer:** 等待不会冻结材料、资格和权限。Resume 时 Runtime 要恢复自己的控制状态，再读取当前 Knowledge/Capability/Security/Domain facts；条件仍有效才继续，否则重新验收、申请批准或 Replan，而不是从旧代码位置无条件续跑。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/security/README.md`.

### Q071
**answer:** LangGraph/Generic Host 可以提供 graph execution、checkpoint、interrupt、调度等通用机制，Zuno 没必要重写。只有“当前计划基于什么前提、旧结果怎样重验收、Domain/Effect 已经发生时怎样 owner-first 恢复”等领域控制语义需要由 Zuno 定义；如果 Host 已能承载这些语义且验证足够，Native Runtime 应保持很薄或退出主路径。

**source_trace:** `docs/modules/runtime/README.md`; `docs/project/README.md`; `docs/architecture/architecture.md`.

### Q072
**answer:** Target 上真实 Attempt/Usage 由 Model Gateway 记录，Run 级总预算与是否继续由 Runtime 控制，从而避免 SDK、Gateway、外层 Agent 各自无限重试。Current 是否已经完整实现跨层统一 budget settlement 没有充分证据，所以不能声称已解决 27 次放大问题。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/model-gateway/README.md`; `docs/evidence/README.md`.

### Q073
**answer:** 永久 Specialist topology 不是默认设计。只有高价值、可独立并行研究在相同任务/预算下稳定优于单 Agent + parallel Tool call 时才值得保留；否则应使用临时 Subagent 或直接删掉 persistent multi-agent。

**source_trace:** `docs/project/README.md`; `docs/modules/runtime/README.md`; `docs/modules/evaluation/README.md`.

### Q074
**answer:** Current Evidence 可以证明部分 persistence/resume/cancel baseline，以及 Slice C 的若干 fault window；但正式 AdmissionReceipt、02↔04 owner-first crash recovery、Reconciliation convergence、cancel-in-flight orchestration等仍未 implementation-proven。不能把“checkpoint 能恢复”扩大成完整长任务恢复已生产验证。

**source_trace:** `docs/evidence/current-runtime-baseline.md`; `docs/evidence/README.md`; `docs/governance/effect-security-slice-c-review.md`.

## G. External Effects / Security / Tool Safety

### Q075
**answer:** TCP/HTTP timeout 只证明本地在期限内没拿到确定响应，不能证明远端业务事务没有提交。既然请求可能已经越过 send boundary，状态应保持 UNKNOWN 并查询/对账现实结果，而不是直接 FAILED 后盲重试。

**source_trace:** `docs/modules/effects/README.md`; `docs/architecture/architecture.md`.

### Q076
**answer:** 远端 idempotency key 能降低重复执行风险，但它不自动告诉本地第一次请求最终处于成功、拒绝、处理中还是未知，也依赖远端真正按该 key 实现一致语义。出现响应丢失时仍可能需要按 provider effect identity/query 收敛现实状态；只有能确认“安全重放等价”时才可以把 reconciliation 简化。

**source_trace:** `docs/modules/effects/README.md`; `docs/architecture/architecture.md`.

### Q077
**answer:** PR #210 的 fault probe 已证明：provider executor 返回成功后，本地 `record_effect_receipt()` 失败时，executor 只调用一次，Gateway 返回 `reconcile_required`，Attempt/ExecutionReceipt 留在 `UNKNOWN/DISPATCHED/UNKNOWN_EFFECT`，没有 committed EffectReceipt，并成功保存 OPEN/RECONCILE 和 provider effect identity。它证明 exception/persistence-failure fallback，不等于真实进程 crash + 后续收敛已证明。

**source_trace:** `docs/evidence/README.md`; `docs/governance/effect-security-slice-c-review.md`.

### Q078
**answer:** 不能写成 Current 已闭环。现在能持久化 OPEN/RECONCILE、做 escalation/manual assessment，但没有 Current proof 证明 remote-query consumer、RESOLVED writer、conclusive ReconciliationReceipt 或最终 Effect truth 的收敛路径，因此结论是 `NOT_IMPLEMENTATION_PROVEN`。

**source_trace:** `docs/evidence/README.md`; `docs/governance/effect-security-slice-c-review.md`.

### Q079
**answer:** 这个批评成立，而且已经被 #205 定义为 confirmed Target violation。当前路径在缺 durable mandatory-audit proof 时仍会 dispatch 并生成 EffectReceipt，所以 Slice C 的结论是 implementation blocked；不能用“helper 已存在”掩盖 wiring 缺失。

**source_trace:** `docs/governance/effect-security-slice-c-review.md`; `docs/evidence/README.md`.

### Q080
**answer:** #203 在 PostgreSQL fault probe 中于 prepare/Approval 后、send 前撤销 SecurityEpoch，`validate_pre_effect_authorization()` fail closed，executor 0 次、Attempt `FAILED/NOT_DISPATCHED`，没有 EffectReceipt/Reconciliation。它只证明这个具体 pre-send revoke window，不证明 Security 全部完成。

**source_trace:** `docs/governance/effect-security-slice-c-review.md`; `docs/evidence/README.md`.

### Q081
**answer:** #207 证明的是 Approval 和 SecurityEpoch reauthorization 已通过后，在短期 Secret lease 校验前撤销 exact SecretRef，系统仍 fail closed、executor 0 次且没有 Effect。它与 RBAC/SecurityEpoch 是不同凭证生命周期边界；同时它不证明 Secret rotation、旧 lease 传播失效或 retry 获取新 credential。

**source_trace:** `docs/governance/effect-security-slice-c-review.md`; `docs/evidence/README.md`.

### Q082
**answer:** 入口 allow 只说明请求开始时允许。真正读取/外发材料、获取 Secret、执行高风险 Tool 等新的 protected action 发生时必须重新消费当前安全条件，防止等待期间权限/epoch/策略变化形成 TOCTOU。Current 只对部分 pre-send/pre-lease window 有 fault evidence。

**source_trace:** `docs/modules/security/README.md`; `docs/architecture/architecture.md`; `docs/governance/effect-security-slice-c-review.md`.

### Q083
**answer:** Approval 应绑定具体动作语义、目标、版本/安全前提；ToolVersion、材料范围或 SecurityEpoch 的变化可能让旧批准不再适用于新动作。不能把一次 Approval 当永久通行证；Current 已证明 SecurityEpoch pre-send revoke 能让旧 Approval 失效，但更广泛 drift 仍需证据。

**source_trace:** `docs/modules/security/README.md`; `docs/governance/effect-security-slice-c-review.md`.

### Q084
**answer:** 已发生的外部 Effect 是历史事实，不能靠改旧 Receipt 说“失败了”来回滚现实。撤回应创建新的受控 Compensation/Effect，重新检查当前授权/审批、形成新的 Attempt，并记录新的外部结果，同时保留原 EffectReceipt。

**source_trace:** `docs/architecture/architecture.md`; `docs/modules/effects/README.md`.

## H. Evaluation / Measurement / Evidence

### Q085
**answer:** 那次 eval 的价值是暴露回退并证明修复后“小样本上不再低于 baseline”，而不是证明 GraphRAG 更强。它是一条负向/回归工程证据，也支持“GraphRAG 必须接受 baseline 和 kill test”的设计；若长期没有增益，应该删默认路径。

**source_trace:** `docs/governance/project-fact-provenance.md` PF-031; `docs/modules/evaluation/README.md`.

### Q086
**answer:** 允许来源没有证明 LawBench/LJPCheck/CMDL 已成为 Current release gate；它们在 Project/Module 叙事里是研究资产和 Target qualification/regression 方法。Current Eval 仍 `MEASUREMENT_BLOCKED`，所以面试时必须说“计划/设计如何用”，不能说“已经以这些 benchmark 发布模型”。

**source_trace:** `docs/project/README.md`; `docs/modules/evaluation/README.md`; `docs/evidence/current-eval-baseline.md`.

### Q087
**answer:** HumanDecision 首先是当时专业人员在具体 Matter/版本/业务目标下做的业务事实，可能包含写作偏好、案件策略、局部信息、甚至后来被新证据推翻的判断。只有经过用途、权限、脱敏、样本选择和 Reviewer protocol 后，合适的投影才可进入 Eval；不能自动当训练真值。

**source_trace:** `docs/modules/domain/README.md`; `docs/modules/evaluation/README.md`.

### Q088
**answer:** 被线上 Bad Case 驱动专门修过的 case 应进入 regression set，而不能继续被当成独立 holdout 来估计泛化。可信评测需要保留未被调参看到的冻结 test/holdout，同时记录训练/Prompt 暴露；文档明确要求记录 tuning exposure。

**source_trace:** `docs/modules/evaluation/README.md`.

### Q089
**answer:** 引用是否存在、schema 是否合法、action hash、duplicate effect 等有确定规则的优先 deterministic checker；开放式法律论证/表达质量才需要 LLM Judge 或人工。Judge 自己必须版本化、校准并对照人工金标准，Judge 不可用/不可比时保持 BLOCKED，而不是硬出 PASS。

**source_trace:** `docs/modules/evaluation/README.md`; `docs/evidence/current-eval-baseline.md`.

### Q090
**answer:** 我会测：形成 review-ready WorkProduct 的时间；Evidence/Citation completeness/correctness；unsupported/critical claim rate；专家接受、修改、拒绝和补证比例；人工步骤与 latency/token/cost。当前没有这些真实业务 baseline，因此这些是 Measurement Needed，不是已证明收益。

**source_trace:** `docs/modules/evaluation/README.md`; `docs/project/README.md`; `docs/evidence/current-eval-baseline.md`.

### Q091
**answer:** Dataset 上 PASS 只证明特定数据、ProviderVersion、配置和 metric 达标。Production 还需要真实安全/外发资格、容量与成本、跨 Owner recovery、外部 Host/Effect、HA/DR/运维、真实用户与法院环境证据；这些当前多数仍未建立。

**source_trace:** `docs/modules/evaluation/README.md`; `docs/evidence/README.md`; `docs/project/README.md`.

### Q092
**answer:** 现有证据下我会优先给 GraphRAG 做 kill test，因为已经有简单 Hybrid baseline、现有小样本只证明修复回退而不是稳定增益。固定 task class/语料/模型/预算后，若 GraphRAG 对 Evidence Sufficiency/Citation/多跳覆盖没有稳定收益却增加成本/失败面，就关闭默认路径；Memory/Multi-Agent/Native Runtime 也遵循同样原则。

**source_trace:** `docs/modules/evaluation/README.md`; `docs/modules/knowledge/README.md`; PF-031.

## I. Build / Buy / Scale / Fundamentals

### Q093
**answer:** 最难外包的不是 Agent UI 或 durable session，而是：法律 Capability/Task Class 的稳定专业语义与 qualification；正式 WorkProduct/人类判断/Provenance 的业务 Authority；材料/证据的任务级有效性以及外部 Effect 的领域恢复语义。Generic Host、MCP、模型 SDK、checkpoint、tracing 等优先复用。

**source_trace:** `docs/project/README.md`; `docs/architecture/architecture.md`; `docs/modules/capability/README.md`; `docs/modules/domain/README.md`.

### Q094
**answer:** LangGraph 可以直接承担 graph execution、checkpoint、interrupt、Send/并发等框架能力；这些不构成 Zuno 自研价值。它不能替法律业务决定 Candidate 何时正式成立，也不能从一个 timeout 宣布远端 Effect 未发生，更不能定义法律 Capability 的资格，因此 Domain/Effects/Capability 的 Authority 仍需由 Zuno 语义层拥有。

**source_trace:** `docs/modules/runtime/README.md`; `docs/modules/domain/README.md`; `docs/modules/effects/README.md`; `docs/project/README.md`.

### Q095
**answer:** Managed Harness 越成熟，Zuno 越应该把自研 Runtime 缩成承载领域控制语义的薄层，甚至直接使用 Generic Host + Legal Backend。沙箱、长会话、context compaction、subagent 等通用机制应 Buy/Adopt；只有平台无法满足且 Eval 证明收益的 Native Runtime 部分才保留。

**source_trace:** `docs/project/README.md`; `docs/modules/runtime/README.md`; `docs/architecture/architecture.md`.

### Q096
**answer:** 用户量很小时，逻辑上仍需保持真正不同的 Authority：正式业务事实与机器候选分离、材料/引用 provenance、当前授权，以及一旦有外部副作用时的现实 Effect truth。可以 defer 的是独立微服务、复杂 worker 拆分、GraphRAG 默认路径、persistent multi-agent、复杂 Native Runtime、甚至完整 Gateway/Capability registry；简单任务保留模块化单体和受控 RAG。

**source_trace:** `docs/architecture/architecture.md`; `docs/modules/README.md`; `docs/project/README.md`.

### Q097
**answer:** 如果只有一个受控模型、没有多 Provider/地域/独立预算/Role 差异，07 可以缩成统一 adapter，记录调用/Usage 和必要安全边界即可。Model Gateway 的抽象必须由替换性、路由和控制需求证明，而不是架构完整感。

**source_trace:** `docs/modules/model-gateway/README.md`.

### Q098
**answer:** 九域默认可以共处模块化 Python backend，并按资源/故障特征拆少量 Worker，而不是九个微服务。第一个值得拆的通常是出现独立资源或安全隔离需求的工作，例如 OCR/index build、模型 egress 或外部 Effects；具体先拆谁取决于吞吐、Secret/network isolation、故障半径和发布生命周期的测量证据。

**source_trace:** `docs/architecture/architecture.md`; `docs/modules/README.md`.

### Q099
**answer:** 没有真实负载数据时只能做设计级瓶颈推断：OCR/索引可能受 CPU/GPU 和 queue 限制，模型受 provider quota/latency/cost 限制，外部系统受 rate limit 限制；应通过 admission/backpressure/worker scaling 分别处理。不能给出“先炸哪一层”的事实结论，也不能报 QPS/P95，必须停在“需要压测/运行数据验证”。

**source_trace:** `docs/architecture/architecture.md`; `docs/evidence/README.md`; PF-022.

### Q100
**answer:** 简历只保留两条，我会保留有最强个人 provenance 的 Agent/Tool Calling bounded refactor/hardening，以及 Context/Memory foundation + focused tests；它们是我本人能解释到代码和边界的工作。Target 里优先 defer/delete 默认 GraphRAG、persistent Multi-Agent 和重 Native Runtime，除非正式 Eval 证明收益；90 秒主线是“我在已有法律 Agent 系统上做了两条可核验工程切片，并把后来架构复盘严格和历史实现分开”。

**source_trace:** exact resume snapshot; `docs/governance/project-fact-provenance.md` PF-029/PF-032; `docs/project/README.md`; `docs/modules/evaluation/README.md`.

## Blue Batch Close

- Answer count: 100
- External calibration sources used: 0
- Unsupported / explicitly unknown premises identified during answering: Q020, Q021, Q030, Q032, Q061, Q062 and several implementation-detail subclaims.
- Verifier may now evaluate source support and decision impact question by question.
