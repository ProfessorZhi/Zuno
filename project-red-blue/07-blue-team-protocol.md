# 蓝队修复协议

蓝队不是替红队把故事说圆，而是把攻击结果变成可验证的事实、范围收缩、方案比较、Target 重设计或工程任务。

红队证明当前 Target 不合理时，蓝队**可以并且应该修改 Target Architecture**；没有义务为了保持旧设计而强行辩护。唯一硬边界是：现实历史事实不能由 Agent 自己创造，正式架构语义仍需按项目治理规则确认后进入 canonical docs。

## 一、Research First：先研究，再向用户提问

当用户忘记项目细节时，蓝队承担“背景重建助手”角色，固定顺序为：

```text
1. 读取 Zuno 最新 main、Git History、Status、Evidence、项目材料
2. 读取用户真实面试、历史简历、已有项目叙事和 internship-work 红队研究
3. 必要时搜索学校 / 教师 / 法院 / 开源项目 / 竞品等可核验公开资料
4. 把直接事实、公开背景、冲突和 Unknown 分开
5. 生成最多 3 个候选解释，标记 R2 / R3 / R4 和反证
6. 只把真正会改变项目真实性或架构结论的最小问题交给用户确认
```

不要让用户从空白页重新写项目背景或六人团队的完整职责。能由证据恢复的先恢复；只能由本人知道的部分尽量改成 A/B/C、区间或“更接近哪个候选”的低负担确认。

## 二、七类蓝队回应

| 回应 | 适用情况 | 结果 |
|---|---|---|
| `ACCEPT_FACT` | 用户确认且有直接证据 | 进入事实或证据记录 |
| `RECONSTRUCT_CANDIDATES` | 用户记忆不完整，但存在可研究线索 | 输出 1–3 个候选及置信度，等待最小确认 |
| `REJECT_PREMISE` | 红队前提不成立 | 说明反例和证据，不回避后续问题 |
| `SCOPE_DOWN` | 目标过大或复杂度不匹配 | 缩小用户、场景、模块、部署或当前承诺 |
| `ADOPT_OR_EXTEND` | 现成方案已经覆盖关键能力 | 采用/扩展外部能力，重新界定 Zuno Delta |
| `PROPOSE_DESIGN` | 需要新的目标方案 | 标为 `[BLUE_PROPOSAL]`，进入架构确认流程 |
| `REQUEST_EVIDENCE` | 事实或效果无法证明 | 建立代码、实验、Trace、Eval 或用户证据任务 |

## 三、五类修复面

### 3.1 Story Repair

用于背景、用户、团队、个人贡献、时间线和开发过程模糊。

蓝队可以主动恢复候选事实，但不能把 `R1_PUBLIC_CONTEXT` 或 `R2_STRONG_RECONSTRUCTION` 直接写成历史。用户确认后，才把必要内容升级为 `[USER_CONFIRMED]`。

### 3.2 Product / Positioning Repair

用于“为什么值得做”“WorkBuddy 已经存在还有什么意义”“真实用户并不需要这么复杂”等攻击。

结果不一定是增加差异化；允许：

```text
缩小为一个真实用户场景
把 Zuno 变成现有平台的 Domain Extension
明确某些通用能力可替换
删除没有用户价值的目标能力
```

### 3.3 Architecture Repair

用于领域对象、模块边界、Owner、状态、失败、版本、安全或 Project–Architecture Alignment 不成立。

流程：

```text
红队 Gap
→ 复述失败的因果链
→ 提出 1–3 个 Target 候选
→ 比较成本、替代方案和非目标
→ 用户确认架构方向
→ 修改 docs/project/architecture / docs/project/modules / ADR / governance
→ 运行验证
→ Red Retest
```

如果真实背景更偏法院内部司法知识工作，而当前旗舰模型过度绑定企业 Contract / Redline，蓝队应认真评估是否需要上提到更通用的 Legal Matter / Legal Document / Evidence / Finding / Human Decision / WorkProduct 抽象，再把合同审查和司法辅助作为不同 Domain Profile；这只是 `BLUE_PROPOSAL` 示例，不在本文件中提前冻结。

### 3.4 Build / Buy Repair

用于自研能力被成熟开源或商业方案替代。

每次必须得到 `ADOPT / EXTEND / BUILD / DEFER` 之一。若结论是 `ADOPT` 或 `EXTEND`，正式架构要同步更新 Ownership：外部方案负责什么，Zuno 只保留什么 Contract，升级/失效时如何降级。

### 3.5 Implementation / Evidence Repair

Target 合理但 Current 没有实现、失败语义、测试、Trace、Eval 或指标时，不修改叙事假装完成。拆成 Codex 工程任务，包含实现范围、Migration、状态转换、失败、恢复、幂等、安全、可观测性、测试和验收。

## 四、Replaceable Infrastructure / Irreplaceable Domain Contract

蓝队必须主动问：

> 如果明天把当前 Agent Runtime、Memory backend、RAG engine、Vector DB 或 Tool adapter 换掉，Zuno 哪些业务事实和治理责任必须仍然成立？

如果一个能力能被替换且不丢失领域事实，它更接近 **Replaceable Infrastructure**，不应拿来当核心差异化。

只有直接承载用户业务事实、证据关系、版本、人工决策、权限、安全 Gate、审计与恢复责任的 Contract，才有资格成为 **Domain Control Plane**。即便这些 Contract 最终也运行在外部框架上，Ownership 仍由 Zuno 的领域层定义。

因此面对 WorkBuddy / Dify / OpenViking 等，蓝队允许得出：

```text
通用 Agent Runtime / UI / Memory backend 可以 ADOPT 或 EXTEND；
Zuno 自己保留法律/司法领域事实、Evidence、Review/Human Decision、权限与审计 Contract；
如果这些领域 Contract 也没有真实需求支撑，则继续 SCOPE_DOWN，而不是强行 BUILD。
```

## 五、团队协作模型

可提出“产品/范围、领域能力、平台工程、前端交付、质量与发布”等角色接口，但必须标明这是 `[BLUE_PROPOSAL]`。现实团队结构用候选模型恢复：例如先生成“2 Agent + 2 后端 + 1 前端 + 1 模型/基础设施”和“按业务纵切小队”两个版本，再让用户选择更接近哪一个。

只有用户确认现实团队结构后，才可写入项目事实。目标团队模型需要写清：决策人、实现人、评审人、发布人、事故响应人和替补关系。

## 六、修复后同步路由

| 内容 | 正式去向 |
|---|---|
| 产品定位、范围和工作流 | 总架构 Part A / `01 Product` |
| Domain Model 与跨模块 Alignment | 总架构 / 相关模块 / ADR |
| Owner、Contract、Failure | 对应模块文档 / ADR |
| 技术取舍、Build/Buy | `docs/decisions/` / ADR |
| 用户、规模、质量和上线状态 | `docs/status/` / `docs/evidence/`；现实事实仍需可靠来源 |
| 面试叙事和攻击摘要 | `project-red-blue/` / `docs/verification/interview-qa/` |
| 团队治理和交付过程 | `docs/governance/` 或项目材料 |
| Current 实现缺口 | Codex 工程任务 + tests / migration / evidence |

架构含义变化时，按 `AGENTS.md` 更新架构 Markdown、图源和验证器；本目录本身不能成为第二份架构真相。

## 七、关闭前的蓝队自检

蓝队提交修复前必须能回答：

```text
这个修复是在改善真实项目，还是只是在准备一句更漂亮的面试答案？
它是否引入了新的未经确认历史？
它是否降低了不必要复杂度？
它是否认真比较了现成方案？
它是否说明了 Current / Target / Future？
如果架构变了，唯一正式事实源是否同步？
如果只是实现缺口，是否转成了可执行工程任务？
```

任何一项答不上来，都不能进入 `RETEST_PENDING`。
