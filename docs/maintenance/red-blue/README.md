# Zuno Red / Blue Interview Workflow

这里是 **给人看的 Red / Blue Interview Harness 使用说明**。真正的机器运行协议在 `/.agent/red-blue/`；已经结束的 Round 归档在 `../history/red-blue/`。

这三层严格分开：

```text
.agent/red-blue/                         Machine harness / active runtime
docs/maintenance/red-blue/              Human workflow / usage contract
docs/maintenance/history/red-blue/      Closed Round archive / non-canonical history
```

Red / Blue 不拥有 Zuno Architecture Truth。它的工作是检验：**简历上的项目 Claim，是否能仅依赖真实项目文档和本人事实，经受大厂面试式连续深挖。**

## 1. 为什么单独做 Harness

过去 Red / Blue 规则散在 `.agent/programs/`、`.agent/references/`、通用 Agent workflow 和历史目录里。这样虽然能运行，但第一次回来的人需要先知道这些隐含关系。

现在专门收敛成：

- `.agent/red-blue/`：角色、攻击模型、Judge、状态和模板；
- 本目录：人怎样启动、观察和结束一轮；
- `history/red-blue/`：过去发生了什么。

`.agent/programs/` 继续服务一般 implementation / architecture design program，不再承担 Red / Blue runtime。

## 2. Round 的真正输入：简历 + 岗位

Red 不应该先拿着 500 道题随机问。正式 Round 必须先固定：

```text
Resume = repository + commit SHA + exact path
Target = role + JD + interview stage
Zuno = exact main/base SHA
```

简历版本必须显式选择。`ProfessorZhi/internship-work` 的 resume index 中如果某版本标记为“待核验包装稿”，不得自动选择成主基线；只有用户明确指定才可以测试它。

Red 先从这份简历抽取 3–5 条最危险 Claim，例如：

- “主导 / 负责 / 从 0 到 1 / 自研”；
- “高并发 / 生产级 / 企业级”；
- “准确率提升 / 成本下降 / 延迟降低”；
- RAG / GraphRAG / Multi-Agent / LangGraph / MCP / Memory；
- 幂等 / 恢复 / 权限 / 队列 / 缓存 / 分布式；
- 导师、课题组、团队成果与个人 Ownership 可能混淆的描述。

然后才进入连续攻击。

## 3. Red 从哪里学“真实面试官怎么问”

Red 有自己的 interviewer kernel。正常 `kernel-only` 模式只需要：

```text
Red attack model
+ exact resume snapshot
+ role / JD / stage
```

需要更高保真时使用 `calibrated` 模式。校准源按优先级读取：

1. `ProfessorZhi/internship-work`：用户本人真实面试、原始对话、复盘、简历定制材料；
2. `ProfessorZhi/interview-notes`：大量 Agent / RAG / Backend / AI Infra 等公开真实面经；
3. `ProfessorZhi/onboard-anything`：真实面经、八股、高质量工程文章；
4. `ProfessorZhi/xiaolin-interview-notes`：结构化 Agent / RAG / Tool Calling / 基础知识补充，并和上面去重；
5. 模型自己的 interviewer knowledge。

这些材料的作用不是生成“题库全集”，而是学习：

- 面试官会从什么 Claim 进入；
- 第一问和第二问怎样连接；
- 什么回答会让面试官继续追；
- Backend、Agent、AI Infra、System Design 面试分别最在意什么风险；
- 如何从项目自然下钻到 Redis / MySQL / 网络 / OS / 分布式等基础知识。

用户本人真实被问过的问题权重最高。

## 4. Red 的攻击应该长什么样

典型链不是固定清单，而是因果式深挖：

```text
这个 Claim 具体是什么？
→ 为什么需要？
→ 最简单方案是什么？
→ 具体在哪里失败？
→ 为什么不是现成平台？
→ 你本人负责什么？
→ 谁拥有事实 / 状态？
→ Crash 怎么办？
→ Timeout 怎么办？
→ 重复执行怎么办？
→ 权限变化怎么办？
→ Scale / Cost 呢？
→ Evidence 呢？
→ Current 还是 Target？
→ 今天重做还会这样设计吗？
→ 删掉一半复杂度会怎样？
```

回答如果只有名词，Red 就落到 State / Owner / Interface；回答如果只有方案，Red 就回到 baseline / alternative / trade-off；回答如果说“我们”，Red 就进入 Ownership；回答如果说“自研”，Red 就进入 Build / Buy / Extend / Defer。

详细规则见 `/.agent/red-blue/attack-model.md`。

## 5. Blue 为什么必须 Closed-book

Blue 的目标不是代表 ChatGPT 的知识上限，而是验证：

> **Zuno 的简历 + Project / Architecture / Modules 是否本身已经足够支持候选人在面试中回答。**

默认 Blue 只能读：

```text
exact resume snapshot
AGENTS.md
docs/project/
docs/architecture/
docs/modules/
docs/decisions/
docs/evidence/
docs/governance/project-fact-provenance.md
```

项目 / 架构主问题优先从 Part A 回答。Part A 应让候选人自然讲出：

```text
现实问题
→ 最简单方案
→ 失败场景
→ 概念边界
→ 为什么这样设计
→ 典型故障 / 恢复
→ alternative / trade-off
→ Current / Target
```

Red 再追字段、事务、CAS、并发、Crash Window 时，Blue 才进入 Part B / Part C / ADR / Evidence。

Blue **不能**临时打开真实面经、用户过去 QA、八股仓库、论文、Web 或 Red 的标准答案补知识。Blue 答不出来就说明文档、简历或架构存在 Gap。

## 6. ChatGPT 怎么跑

支持两种常见方式。

### 真人模拟

Red = ChatGPT，Blue = 用户本人。

用户可以直接说：

```text
启动 Zuno Red Team，目标 Backend / Agent 二面，使用我指定的简历版本。
```

Red 一次只问一个主问题，不提示答案。用户回答后继续追。用户说“结束 / 复盘”后再让 Judge 汇总。

### ChatGPT Red / Blue 对攻（chatgpt-duel）

同一个 ChatGPT Controller 依次模拟：

```text
Red → Blue → Judge → Red follow-up
```

为了避免答案泄漏，Red hidden intent / 面经校准内容不进入 Blue 可见上下文。单个聊天中的这种隔离属于程序性隔离；如果把结果当正式文档验收，建议用独立子 Agent / context。

## 7. Autonomous Agent 怎么跑（autonomous-agent）

Autonomous 模式让 Controller 创建独立 Red、Blue、Judge context，并严格使用 `.agent/red-blue/protocol.md` 的 allowlist。

建议状态机：

```text
INIT
→ pin resume / Zuno SHA / role
→ Red claim mining
→ optional interview calibration
→ ask
→ Blue closed-book answer
→ Judge
→ continue same chain / next claim
→ close
→ archive
```

Agent 可以自主跑完整 Round，但**不能自主修改架构或简历**。它只产生 Gap Report。修复必须是后续独立任务。

## 8. Judge 不负责“教会 Blue”

Judge 只输出：

- `PASS / PARTIAL / FAIL / UNSUPPORTED_CLAIM`；
- Gap type；
- severity；
- source support；
- 是否继续同一攻击链；
- Round 结束后的修复优先级。

特别区分：

```text
NARRATIVE_GAP
DOC_GAP
ARCHITECTURE_GAP
TRADEOFF_GAP
EVIDENCE_GAP
IMPLEMENTATION_GAP
OWNERSHIP_GAP
MEASUREMENT_GAP
PROJECT_REALITY_GAP
RESUME_CLAIM_RISK
```

Blue 回答失败不等于架构失败。只有 Owner 冲突、状态语义冲突、Recovery 不闭环、Security Authority 不清、Contract 不成立、重要反例无法处理等，才优先升级 Architecture Gap。

## 9. Part A 是这套 Harness 的核心验收对象

真正理想的结果是：面试官问出问题后，Blue 不是在几个文档中拼词，而是能从 Part A 的故事里自然截出回答。

例如 Red 问：

> 为什么不用 WorkBuddy / Dify？

好的 Blue 不应背 Feature checklist，而应该能够从 Project / Architecture 的发展故事自然回答：哪些通用 orchestration 本来就应该复用，真正需要 Zuno 自己拥有的是什么专业 semantic authority、research capability、domain fact、effect recovery 或 evaluation responsibility。

如果这个问题必须临时读外部平台文章才能回答，说明当前 Part A 仍有 Narrative / Documentation Gap。

## 10. Round 结束与修复

完整闭环：

```text
Round
→ Judge report
→ archive raw record to docs/maintenance/history/red-blue/
→ choose highest-value Gap
→ Narrative / Docs / Architecture / Evidence / Resume fix
→ PR + CI + merge
→ reread main
→ Red retest with different wording
```

不要针对某一道题直接加一个 FAQ。修复目标应该是让同类问题都能从更好的项目 / 架构故事中自然得到回答。

## 11. Skill 化

这套 Harness 后续适合导出为通用 Skill：

```text
Red/Blue Architecture Interview Harness Skill
```

Skill 应带：

- Role / context firewall；
- Claim mining；
- interviewer personas；
- attack graph；
- answer-shape triggers；
- Closed-book Blue；
- Judge / Gap taxonomy；
- Round templates / closure。

Skill 不应带：

- Zuno 当前架构正文；
- 某份个人简历正文；
- 历史 Round；
- 当前 `current.md`；
- 固定“500 题标准答案”。

这样 Skill 可以迁移到其他项目 / 候选人，而 Zuno 的事实仍在运行时从仓库读取。