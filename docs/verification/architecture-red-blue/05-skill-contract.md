# Future Skill Contract：Architecture Red-Blue Skill

本文件是后续 Codex Skill 的行为契约，不是当前可安装的插件实现。Skill 的目标是把“事实采集 → 红队盘问 → 蓝队补全 → Canonical 回写 → Red Retest”固化为可重复工作流。

## 触发方式

建议的自然语言入口：

```text
启动 Zuno 架构红蓝队
启动项目落地红队
针对当前架构文档进行红队盘问
按项目背景、团队和用户信息补全 Zuno
对这次蓝队修复做 Red Retest
```

Skill 不应在用户没有明确开始时自动修改架构或项目代码。

## Skill 输入

```text
目标：架构审计 / 项目落地 / 面试压力测试 / 蓝队修复 / Red Retest
范围：总体架构 / 指定模块 / 产品定位 / 团队协作 / 全项目
用户事实：背景、用户、规模、团队、个人贡献、当前状态、约束
参考：当前 Canonical docs、代码、测试、Trace、Eval、已有 Gap
```

缺少 P0 事实时，Skill 先进入 `FACT_INTAKE`，最多连续询问一个小组的问题；允许用户回答 UNKNOWN，但不允许 Skill 自行填数。

## Skill 状态机

```text
IDLE
  → FACT_INTAKE
  → CLAIM_INVENTORY
  → RED_ATTACK
  → BLUE_RESPONSE
  → REFEREE_DECISION
  → BLUE_PROPOSAL
  → USER_APPROVAL
  → CANONICAL_SYNC
  → RED_RETEST
  → CLOSED / BLOCKED
```

### 状态边界

- `FACT_INTAKE`：只采集和标记事实，不修改正式文档；
- `RED_ATTACK`：只问问题和记录 Gap，不给答案、不改文件；
- `BLUE_PROPOSAL`：Agent 可以补充架构、场景、协作、流程和竞品方案，但都标 Proposal；
- `USER_APPROVAL`：任何新事实、架构语义或项目落地描述必须经过用户确认；
- `CANONICAL_SYNC`：只更新正确的 Owner 文档，并运行对应验证；
- `RED_RETEST`：换问法复测，不能沿用原题宣布通过。

## Skill 允许补充的内容

```text
可以补充：场景拆解、最小可交付范围、逻辑/物理架构候选、模块边界、
目标团队协作矩阵、目标开发流程、竞品差异假设、红队问题和验证实验。

不能补充：用户数、团队人数、真实客户、上线状态、性能数字、个人贡献、
生产质量、合作关系或“已经实现”的任何事实。
```

## 交互模式

### `INQUIRE`

只向用户收集背景、用户、规模、团队、个人贡献、当前状态和约束。

### `RED_ONLY`

只盘问架构、竞品、团队、工程、成本、安全和落地，不修改任何文件。

### `BLUE_PROPOSE`

根据已确认事实提出架构、场景、协作和开发过程 Proposal，输出待确认清单。

### `CANONICAL_SYNC`

用户批准后，更新 architecture、模块、ADR、README、Status/Evidence 等正确事实源；设计含义变化时同步 architecture views。

### `RETEST`

在修复后使用新的反事实或约束重新盘问。

## 输出格式

每一轮输出：

```text
事实摘要：
当前被攻击的 Claim：
红队问题：
蓝队回应：
Agent Proposal：
需要用户确认：
Gap Type / Severity：
正式回写目标：
下一问或 Red Retest 问法：
```

模拟面试模式下，候选人只看到“红队问题”；复盘模式才显示 Proposal、Gap 和回写目标。

## 安全与治理约束

- 不保存隐藏思维链；只保存可审计的 Claim、问题、回答摘要、证据、Gap 和决定；
- 不将 Architecture Red-Blue Workspace 变成第二套架构事实源；
- 不把 WorkBuddy、开源项目或行业惯例当作已经验证的产品结论；
- 不以团队小为理由直接删除模块，而是区分逻辑模块、部署域、当前范围和 Target 演进；
- 不未经用户确认修改公开 API、数据库、安全边界或业务 Runtime；
- 任何架构变更完成后必须运行项目规定的文档、链接和架构验证。
