# Zuno Architecture Red-Blue Workspace

> 状态：工作区协议已建立，首次真实项目事实采集待用户提供输入。

这是 Zuno 的集中式架构红蓝队工作区。它不拥有新的 Runtime Contract，也不替代 `docs/architecture/`、`docs/modules/`、`docs/decisions/`、`docs/status/` 或 `docs/evidence/`；它负责把“面试官会怎样挑刺”和“项目实际上怎样落地”组织成一套可反复执行的盘问与修复流程。

## 它解决什么问题

Zuno 不能只回答：

> 我们有 Agent、GraphRAG、Memory、Tool 和 11 个模块。

还必须经得起这些问题：

- 用户为什么需要 Zuno，WorkBuddy 等通用 Agent 已经存在时，Zuno 的不可替代价值是什么？
- 一个小团队为什么要设计这么多模块？当前到底是逻辑模块、代码模块还是独立服务？
- 谁在用、用了多少、现在是否落地、哪些只是 Target？
- 团队成员分别负责什么，哪些是用户本人做的，哪些是框架或其他成员完成的？
- 架构是否超过当前资源、用户规模和交付阶段？删掉一半模块还能不能交付？
- 失败、权限、成本、数据隔离、评测和运维是否有真实闭环？

红队负责证明这些 Claim 经不起哪里；蓝队负责给出事实、收缩范围或修复设计；Codex 负责整理建议并把经确认的变更回写到正确的正式事实源。

## 与现有验证目录的关系

```text
docs/verification/architecture-red-blue/
    项目事实采集、红蓝互动、产品/团队/竞品/落地挑刺、修复路由、Skill 协议

docs/verification/interview-qa/
    现有架构面试攻击题、主题 QA、Deep Dive Chain 和 Coverage/GAP 辅助材料

docs/architecture/ + docs/modules/ + docs/decisions/
    被红队攻击、最终拥有正式架构事实的文档
```

不复制 `interview-qa` 的 267 道题，也不在这里生成第二套模块设计。红蓝工作区调用现有题库；题库若暴露正式架构 Gap，仍按既有 `architecture-gap-report.md` 和 Owner 文档流程处理。

## 文件地图

| 文件 | 唯一职责 |
|---|---|
| `01-project-context-intake.md` | 用户必须提供的项目事实、Agent 可以补充的 Proposal、事实台账和采集顺序 |
| `02-red-blue-interaction.md` | 红队、蓝队、裁判的互动协议，以及如何补全团队协作和开发过程 |
| `03-attack-surface.md` | 产品、竞品、团队、架构、工程、可靠性、安全、成本和落地红灯问题 |
| `04-blue-fix-routing.md` | Gap 分类、修复去向、Canonical 文档回写和关闭标准 |
| `05-skill-contract.md` | 后续 Codex Skill 的触发方式、状态、权限、输出和安全边界 |

## 三种信息状态必须分开

```text
FACT_USER：用户明确提供的项目事实
FACT_REPO：代码、测试、Trace、Eval 或正式文档能够证明的事实
PROPOSAL_AGENT：Agent 根据事实提出的产品、架构、协作或落地方案
DECISION_PENDING：需要用户确认，不能写入正式事实
GAP：红队发现的事实、架构、测量、产品或交付缺口
```

Agent 可以补全结构、提出方案和设计候选，但不能补造用户数量、团队人数、真实客户、上线状态、性能数字或个人贡献。

## 推荐使用方式

```text
1. 先做 Fact Intake，不直接改架构文档
2. 再启动 Red Attack，一次盘问一个 Claim
3. 蓝队确认事实，Agent 给出 Proposal / Scope-down / Alternative
4. 裁判决定接受、拒绝或继续追问
5. 只把已确认内容写回对应 Canonical Owner
6. 用换一种问法 Red Retest
```

后续 Skill 默认先盘问，后补全；默认不自动提交架构语义变化。
