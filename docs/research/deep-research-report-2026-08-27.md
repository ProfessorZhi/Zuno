# Zuno 深度研究报告（2026-08-27）

> status: research-snapshot
> last_verified: 2026-08-27
> canonical_truth: no
> purpose: 为下一轮 Project / Architecture / Module Human-first Rewrite 提供研究依据

## 1. 研究问题

本轮研究不是给既有九模块“找论文背书”，而是重新追问：

```text
葛季栋 / LIPLAB 长期研究
→ 真实智慧司法与软件工程问题
→ Research Artifacts
→ Engineering Capabilities
→ Zuno Product / Architecture
→ 与通用 Agent 平台的能力边界
→ Interview-native Documentation
```

核心假设需要被验证，而不是预设：Zuno 是否真正填补了 `Research Artifact → Engineering-grade Legal Capability` 的工程断层？如果通用平台可以合理承担某层，应明确复用或删除 Zuno 的重复实现。

## 2. Executive Diagnosis

当前 Zuno 文档的主要问题不是 Part A 太短，也不是总体架构缺少技术内容，而是 **Global Narrative Continuity 不足**。

大量局部判断本身是合理的：

- Uploaded != Knowledge Ready；
- EvidenceCandidate != Evidence；
- Runtime completed != Domain committed；
- Transport timeout != Effect failed；
- Initial authorization != authorization now；
- Provider available != Provider qualified；
- Can build != worth keeping。

但这些判断还没有被讲成一条连续的架构成长故事。读者容易看到很多“正确知识点”，却不清楚为什么前一个矛盾必然把系统推到下一个边界。

真正需要提升的是：

- Research Story：为什么这个项目从课题组长期研究体系中出现；
- Project Story：真实项目从研究成果走向工程系统时发生了什么；
- Evolution Story：九个责任域怎样由不同 Authority 冲突逐步逼出；
- Platform Story：为什么大量通用能力应当复用成熟平台；
- Module Transition Story：每个 Part A 的下一段为什么必须存在；
- Interview Extractability：正文能否自然截出 30–90 秒的大厂面试答案。

## 3. 最可信的 Zuno 定位

本轮研究最有证据支撑的定位不是“另一个 Legal Agent Platform”，也不是“比 WorkBuddy / Dify 更完整的 Runtime”，而是：

> **Zuno 是面向智慧司法场景的研究能力工程化 + 法律业务权威系统层。**

它需要解决的不是重新发明 Conversation、Workflow、Tool Calling、MCP、Checkpoint、Generic Memory、Generic RAG、模型 SDK 或 Tracing；这些通用能力原则上应尽量复用成熟平台与基础设施。

Zuno 更值得 Own 的是：

- 课题组 Research Artifact 如何形成稳定专业 Capability semantics；
- 不同 Provider 对哪些任务真正 qualified；
- 当前法律材料究竟是哪一版，派生知识是否满足任务需要；
- 机器结果什么时候只是 Candidate，什么时候经过正式准入成为 Business Fact；
- 新证据、材料版本和人工判断如何影响旧 WorkProduct；
- 长任务中 Runtime State 与 Domain State 如何各自恢复；
- 外围系统 timeout 后现实 Effect 到底发生没有；
- 权限在长任务中变化时当前动作还能不能继续；
- 什么 Evidence 证明 GraphRAG、Reflection、Native Runtime、强模型等复杂机制值得留下。

这仍是 Architecture / Product Thesis，不是已经通过正式 benchmark 证明的业务优势。

## 4. 葛季栋 / LIPLAB 研究谱系

研究必须先做作者身份消歧。目标作者固定为南京大学软件学院葛季栋（Jidong Ge），以后论文进入 VERIFIED SET 时应优先使用南京大学官方资料、DBLP/ORCID、明确 affiliation 和已确认 co-author network 交叉核验；仅姓名相同不算。

现阶段更有价值的谱系不是“论文清单”，而是研究问题的长期演化：

1. **Software Process / Workflow / Collaboration**：过程、协同、工作流与调度形成长期软件工程背景。与当前 Runtime 更适合标 `CONCEPTUAL_LINEAGE`，不能说直接产生了 PlanVersion 或 Single Controller。
2. **Intelligent Judiciary / Legal NLP**：多源证据、裁判说理、法条推荐、事实—法条关系等构成 Zuno 最直接的项目/能力背景。
3. **Intelligent Software Engineering**：Program Repair、Code Completion、Testing 等大量成果更多形成测试、资格和可替换实现的工程思想背景，不应强接九模块。
4. **Legal LLM / Evaluation**：LawBench、LJPCheck、法律模型等研究显示“一个 headline accuracy 不足以说明法律 AI 是否可靠”，对 Zuno Capability Qualification / Evaluation 有较强 lineage。
5. **近期 LLM / RAG**：可作为能力或概念背景，但只有经过 Current Evidence 才能声称已经进入 Zuno。

研究关系必须标记 `DIRECT_LINEAGE / CAPABILITY_LINEAGE / CONCEPTUAL_LINEAGE / BACKGROUND_ONLY / UNVERIFIED`。

## 5. Research Artifact 进入工程系统时真正缺什么

论文通常回答“某种方法在某组数据上是否有效”。产品系统还必须回答：

- 当前输入对应哪一版材料？
- 派生知识是否完整到足以支撑本任务？
- Provider 的专业语义是否与 Capability 承诺一致？
- Dataset 上通过是否意味着当前案件类型也 qualified？
- 模型升级以后历史结果还能否解释？
- AI 输出只是候选，还是已经被正式业务接受？
- 人工修改以后谁拥有最终事实？
- Crash / timeout / late result 怎样恢复？
- 权限和数据外发政策变化以后动作还能继续吗？
- 复杂能力的质量收益是否值得成本和维护负担？

因此最关键的工程转换是：

```text
Research Artifact
!= Capability
!= Provider
!= Qualified Provider
!= Formal Business Fact
```

这条转换比“九个模块”更适合作为 Zuno 的研究—工程主线。

## 6. 与通用 Agent 平台的边界

2026 年的平台基线已经足够强，不能再用“通用平台没有企业权限、长任务、持久化、RAG、Eval、Tracing”等理由制造差异。

WorkBuddy、Dify、Coze、LangGraph / LangSmith 等平台可以承担或提供大量通用能力：

- Agent Host / Conversation；
- Workflow / DAG / Graph；
- Tool Calling / MCP；
- Checkpoint / Resume / HITL；
- Generic Memory / Generic RAG；
- Model integration；
- Enterprise identity / deployment（依具体产品）；
- Tracing / generic Eval plumbing。

因此专业的论点不是“平台做不到”，而是：

> **平台可以 Host / Invoke / Persist 这些业务语义，但不应该替 Zuno 的法律业务和研究系统定义这些语义，也不会天然成为它们的 Authority。**

WorkBuddy 可以运行 `evidence_analysis` Skill，但 Runtime 本身不天然知道：这次分析对应哪个 DocumentVersion、当前 Knowledge 是否 ready、当前 Provider 对这类案件是否 qualified、返回值只是 Candidate 还是 Formal Finding、新证据是否让旧结果 stale、外围动作 timeout 后真实记录是否已经生成。

这不是平台缺陷，而是领域 Authority 不应由通用 Runtime 隐式拥有。

## 7. Build / Buy / Extend / Delete

建议长期保持下面的默认方向，直到 Evidence 证明需要更复杂方案：

### Buy / Adopt

- DB / Queue / Vector Store / Graph Store；
- Identity Provider / SSO / Secret Manager；
- OCR / Embedding / Generic Rerank；
- MCP / Tool transport；
- Model SDK；
- OTel / 通用 Observability；
- Generic Eval harness；
- Generic Agent Host / Workflow primitives。

### Zuno Own

- Research Capability contract 与专业语义；
- Provider Qualification / scoped eligibility 的业务规则；
- Legal material / evidence provenance；
- Candidate → Formal Domain Authority；
- WorkProduct lifecycle / invalidation；
- 法律任务 Evaluation dataset / decision semantics；
- 必要的 domain-specific Effect / Security semantics。

### Measurement-gated / 可删除

- Native Runtime；
- GraphRAG 默认路径；
- Reflection；
- Persistent Multi-Agent；
- 任何无法通过 baseline / ablation / kill test 证明收益的复杂机制。

## 8. Zuno Story Spine

未来 Project 与 Architecture 不应从“九模块”开始。

更自然的故事是：

```text
课题组长期研究积累
→ 多个独立 Research Artifacts
→ 最简单产品：Generic Agent Host + Legal RAG + Research Tools
→ 这个方案对简单任务其实足够
→ Artifact 需要变成稳定 Capability
→ 材料上传成功不代表知识 ready
→ AI 输出不代表正式业务事实
→ 长任务产生 Crash / late result / Replan
→ 外部动作产生 Effect uncertainty
→ 长任务期间 Authorization 会变化
→ 模型和研究实现持续替换
→ Evaluation 决定复杂机制是否值得存在
→ 最后才归纳出九个不同 Authority / Ownership boundaries
```

九模块应该是故事的**结论**，不是故事的起点。

## 9. Module Narrative 研究结论

Part A 应是一篇长的 Architecture Essay，而不是 FAQ、对象目录或论文综述。

最有价值的 Opening Scene 包括：

- 03：100 份材料上传成功，但关键扫描件仍未 OCR；
- 05：旧研究模型和新 LLM 都能做“事件抽取”，Schema 相同却不代表专业语义与适用范围相同；
- 02：模型给出法律结论，专业人员修改并采纳，后来新证据进入；
- 04：新证据进入后，旧 Plan 的高质量分支晚到；
- 06：HTTP timeout，不知道外围法院系统是否已经实际执行；
- 08：任务开始时有权限，二十分钟后准备外发时权限已经撤销；
- 09：GraphRAG、Reflection、强模型都能加，但没有人知道究竟谁贡献了收益。

Part A 的段落之间应保持：

```text
上一段留下一个未解决矛盾
→ 下一段先尝试最直觉方案
→ 具体反例证明它不足
→ 才引出新的概念边界
→ 最后才给工程名字
```

## 10. Interview Pressure

真实面试材料反复验证：面试官首先检查的不是术语数量，而是复杂度有没有业务因果。

文档需要能够自然支持：

- 为什么这个项目存在？
- 为什么不是普通 RAG？
- 为什么不用 WorkBuddy / Dify / Coze？
- 哪些东西本来就应该复用 LangGraph？
- 为什么需要 Capability？
- 为什么模型结果不能直接成为业务事实？
- Crash / late result / timeout 怎么办？
- 权限中途变化怎么办？
- GraphRAG / Native Runtime 到底提高了多少？
- 导师/团队做的与个人 Ownership 怎么分？
- 用户量小十倍还需要哪些层？
- 今天重做会删掉什么？

理想状态不是增加 Interview FAQ，而是正文中每个核心决策都有一段可以自然截取的因果叙事。

## 11. Rewrite Priority

### P0

1. `docs/project/project.md`：把 LIPLAB / 智慧司法研究 → Research Artifacts → Generic Host baseline → Engineering Gap → Zuno 变成项目故事第一因。
2. `docs/architecture/architecture.md` Part A：用一个连续法律任务讲“成功如何一步步分裂”，九模块最后出现。
3. `docs/modules/05-capability-skill.md` Part A：成为 Research Artifact → Capability → Provider → Qualification 的核心 Architecture Essay。
4. 03 → 02 → 09：分别承接 Knowledge/Evidence、Formal Authority、Evaluation/Qualification。

### P1

- `docs/modules/README.md`；
- 04 Runtime；
- 06 Effects（保留现有 timeout opener，强化平台边界）；
- 08 Security。

### P2

- 01、07、Architecture Views；
- Reference consistency；
- Governance 写作标准升级。

## 12. Evidence Boundary

本报告是 Research Snapshot，不证明：

- 某篇论文已经进入某个历史 Zuno 版本；
- Zuno 已在 Production 使用；
- Native Runtime / GraphRAG 已经优于 Generic Host；
- 导师/课题组成果由某个个人独立实现；
- 任何 Target Architecture 已经具备 Current Code / Test / Runtime Evidence。

后续每次把研究结论写进 Project / Architecture / Modules，都必须回到对应 canonical owner 与 Evidence hierarchy 重新验证。
