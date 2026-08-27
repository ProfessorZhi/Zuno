# Documentation Narrative Blueprint

> status: research-blueprint
> rewrite_authorization: no

本文件保存本轮研究得到的 Human-first 写作蓝图。它指导下一轮 `project / architecture / modules` 重写，但**本身不拥有 Project Truth 或 Architecture Truth**。

## 1. 全局问题

Zuno 文档当前最大的质量问题不是技术深度不足，而是：

> **很多局部论证都正确，但整篇没有让读者持续知道“为什么我们必须走到下一步”。**

因此下一轮不能再做“九模块平均加深”，而应先建立一个 Global Story Spine。

## 2. Project Story

`docs/project/project.md` 应承担真实项目故事，不伪造 Architecture Evolution 为真实历史。

建议叙事主线：

```text
葛季栋 / LIPLAB 长期智慧司法与软件工程研究
→ 多个独立 Research Artifacts
→ 为什么这些局部成果值得进入一个真实工程系统
→ 最简单产品：Generic Agent Host + Legal RAG + Research Models / Skills
→ 这个方案其实能解决大量简单任务
→ 真正不可外包的 Engineering Gap 出现
→ Research Artifact 需要稳定 Capability / Qualification
→ 材料、Evidence、Formal WorkProduct 开始需要长期 Authority
→ Zuno 的边界逐渐收窄到研究能力工程化 + 法律业务权威
→ Pilot / Current / Target / Evidence / Unknown
→ 团队 / 导师 / 个人 Ownership
→ 今天重新做会少造什么
```

Project 文档应自然支撑 3–5 分钟项目介绍，而不是让面试者先背九模块。

## 3. Architecture Story

`docs/architecture/architecture.md` Part A 应讲一次**概念上的架构成长**。

不要第一屏展示九模块表。先假设：

> Generic Host + Legal RAG + 一组 Research Skills。

然后使用同一个法律任务连续推进。

### Scene A — Uploaded != Ready

100 份材料都 HTTP 上传成功，但关键扫描件仍未 OCR。系统第一次发现“文件存在”不等于“当前任务知识完整可用”。先解释这个错误推断，再引出材料版本、派生知识代际与 task readiness。

### Scene B — Implementation != Capability

传统研究模型与新的 LLM 都能返回事件抽取 JSON。Schema 一样仍不能证明它们对“事件”的定义、适用范围与专业质量相同。先解释为什么 Runtime 不应该绑定论文模型，再引出 Capability / Provider / Qualification。

### Scene C — Machine Output != Formal Truth

模型给出风险结论，专业人员修改并采纳。机器结果与正式业务事实开始分裂；新证据进来后，历史存在与当前有效性又继续分裂。

### Scene D — Finished != Still Acceptable

复杂任务运行二十分钟，新材料进入；旧 Plan 的一个高质量分支晚到。此时“计算成功”不等于“结果仍有资格被当前计划接受”，再引出 Runtime control / plan version / late result / replan。

### Scene E — Timeout != Effect Failed

系统向外围法院系统提交动作，HTTP timeout。网络状态不能证明现实动作没发生，blind retry 可能制造重复 Effect。

### Scene F — Authorized Then != Authorized Now

任务启动时合法，在等待期间权限被撤销；后台 Worker 准备外发数据时必须重新消费当前安全事实。

### Scene G — Can Build != Worth Keeping

GraphRAG、Reflection、Multi-Agent、更贵模型都可以加。最后一个问题不是“还能加什么”，而是“什么证据证明复杂机制值得长期存在”。

最后才归纳：这些不同的事实不能互相冒充，因此形成九个逻辑 Ownership boundaries。

## 4. Module Part A

Part A 可以很长。长度必须来自 Context、Story、Causality、Failure、Recovery、Alternative、Trade-off、Evolution 和 Evidence，而不是对象和标题数量。

### 推荐 Opening Scene

| Module | Opening scene / core tension |
| --- | --- |
| 01 Application | Runtime 结束了，但 UI / 外部系统究竟能不能显示“正式完成”？ Product Projection != Owner Truth |
| 02 Legal Domain | 模型结论被专家修改采纳，后来新 Evidence 进入。 Candidate != Formal Fact；History != current validity |
| 03 Knowledge | 100 份文件上传成功，关键扫描件仍未 OCR。 Uploaded != Ready；retrieval miss != fact absent |
| 04 Runtime | 新证据进入后，旧 Plan 的高质量分支晚到。 Finished != still acceptable |
| 05 Capability | 旧研究模型和新 LLM 都做事件抽取。 Implementation != Capability；Conformance != Qualification |
| 06 Effects | POST timeout，不知道外围系统到底执行没有。 Transport != real-world effect |
| 07 Model Gateway | 本地研究模型、私有 LLM、云 Provider 都可调用。 Available != permitted != qualified |
| 08 Security | 10:00 有权限，10:20 执行动作时权限已经撤销。 Auth at start != authorization now |
| 09 Evaluation | GraphRAG / Reflection / 强模型都能加，却不知道谁贡献了收益。 Can build != worth keeping |

这些不是固定章节模板，只是要求每篇先建立读者能看见的真实矛盾。

## 5. Causal Transition

理想 Part A 的段落关系：

```text
我们原本直接做 X
→ 在简单任务里它完全合理
→ 具体场景 Y 出现
→ 最直觉的修复 Z 仍然失败
→ 真正需要分开的其实是两种语义 / 两个 Authority
→ 工程上后来把它叫作某个术语
→ 这个边界又留下一个新问题
→ 下一段自然继续
```

禁止退化成：

```text
### Concept A
定义
### Concept B
定义
### Concept C
定义
```

## 6. Writing Standard V2 候选原则

下一轮 Governance 可以吸收，但不要机械化：

- **Global Story Spine First**：整篇先有主因果链。
- **Research Provenance**：Research Artifact / Capability / Provider / Current 分开。
- **Baseline Before Differentiation**：先诚实写简单方案和成熟平台已经能做什么。
- **Concept Before Name**：现实矛盾先于内部对象名。
- **Failure Before Mechanism**：先解释错误直觉为什么失败。
- **Causal Transition**：章节之间继承未解决问题。
- **Authority Before Plumbing**：先问谁能决定事实，再谈 Receipt / DB / CAS。
- **Can Host != Should Own**：平台能承载不等于平台应该拥有领域语义。
- **Deletion Condition**：复杂机制必须有退出条件。
- **Ownership Honesty**：导师 / 课题组 / 团队 / 个人严格分开。
- **Interview Extractability**：正文中的核心因果段落能自然截成面试答案。
- **Evidence-aware Claims**：没测过就继续写 Hypothesis / Target。

不要新增固定标题数、每段必须几个 why、术语比例、硬字符数等反向激励。

## 7. Human Review Questions

人工验收 Part A 时优先问：

1. 读完前 20% 后，陌生高级工程师是否知道这个模块为什么存在？
2. 删除所有 PascalCase 内部对象名以后，设计因果还能否复述？
3. 上一节是否真的留下了下一节要解决的问题？
4. 复杂方案出现前，是否诚实讲了简单 baseline 为什么可行、又在哪里失败？
5. 文档是在说“平台做不到”，还是准确区分“平台可以 Host / Zuno 必须 Own”？
6. Crash / timeout / permission change 的恢复有没有回到明确 Authority？
7. 如果用户量小十倍、平台能力更强或测量收益不足，哪些层应该删除？
8. 读完以后记住的是几个真实矛盾，还是几十个对象名？

## 8. Rewrite Priority

### P0

`project.md` → overall Architecture Part A → 05 Capability → 03 / 02 / 09。

### P1

`modules/README` → 04 → 06 → 08。

### P2

01 → 07 → Architecture Views → Reference consistency → Governance V2。

目录和 Research Knowledge Base 建立完成前，不把这个 Blueprint 直接写成新的 canonical architecture。
