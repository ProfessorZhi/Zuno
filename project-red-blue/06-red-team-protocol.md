# 红队攻击协议

## 红队职责

红队是只读审计者，不是替候选人补答案的教练。它从最新陈述、项目模型和正式架构出发，逐层攻击，并把暴露的问题路由给蓝队；红队会话不得修改项目事实、正式架构、简历、代码或测试。

红队的目标不是“多问几题”，而是证明一个 Claim 是否经得起连续取证：

```text
Claim
→ 真实性
→ Ownership
→ 必要性
→ 替代方案
→ 机制
→ 实现细节
→ 失败
→ 证据
→ Current / Target 边界
→ 反事实
```

## 会话模式

每轮必须先选模式，避免把面试模拟、架构审计和实现审计混在一起：

| Mode | 主要目标 |
|---|---|
| `PROJECT_REALITY` | 背景、用户、团队、个人贡献、落地和时间线 |
| `ARCHITECTURE` | 产品定位、领域对象、模块边界、Owner、状态、Failure、Build/Buy |
| `IMPLEMENTATION` | 代码路径、Schema、算法、参数、数据、部署、测试和恢复 |
| `FULL_INTERVIEW` | 按真实岗位节奏组合 Reality + Architecture + Implementation + Fundamentals |

同一轮可以包含交叉问题，但必须有一个主模式。

## 会话前读取

### Step 0：刷新外部输入

1. 读取 Zuno 最新 `main`，不得沿用旧 SHA；
2. 读取 `project-red-blue/` 当前事实、Gap 和最近会话；
3. 读取 `ProfessorZhi/internship-work` 最新 `main` 中：
   - 用户最近真实面试 QA / 复盘；
   - `interview/00_面试文案仓库/red-team/`；
   - 最新 `06_来源审计.md`，确认面经研究基线是否已经变化；
4. 如果用户明确要求比较开源/竞品，读取最新官方资料；不得基于旧印象攻击。

截至已核验的 `internship-work@f7d0c450...`，面试红队来源审计记录全量扫描 1,159 份正文、内容级深读 300 份。这个数字只作为当前基线；只要上游更新，下一轮必须重新读取。

### Step 1：读取被审计对象

按范围读取：

1. `docs/architecture/architecture.md`、`docs/architecture/architecture-views.md`；
2. 相关 `docs/modules/`、`docs/decisions/`、`docs/status/`、`docs/evidence/`；
3. `docs/verification/interview-qa/` 中与目标机制相关的既有攻击链；
4. 代码、测试、Git 提交和可复现证据（需要验证 Current 时）；
5. `01-project-facts.md` 的事实状态和重建置信度。

## 七个阶段

### 阶段一：建立上下文和冲突清单

先区分：

```text
USER_CONFIRMED
REPO_EVIDENCE
PUBLIC_CONTEXT
TARGET_ACCEPTED
BLUE_PROPOSAL / RECONSTRUCTION
UNKNOWN
```

同时做跨文档冲突检查：项目背景、架构 Part A、模块文档、Status、简历 Claim 或真实面试回答之间有冲突时，先记录冲突，不替蓝队选择一个“最顺”的版本。

### 阶段二：建立 Claim Inventory

把当前叙事和架构拆成可攻击陈述。每个 Claim 至少记录：

```text
Claim ID
陈述
来源
truth_status
reconstruction_confidence
事实 Owner
关联模块 / Contract
可核验证据
反例
Attack Angles
```

没有 Claim Inventory 不开始长链盘问。

### 阶段三：选择攻击计划

每轮只选择 3–5 条高风险主链，不平均撒题。标准 `ARCHITECTURE` 轮至少包含：

```text
1 条 Project–Architecture Alignment 链
1 条 Ownership / Team Feasibility 链
1 条核心架构机制链
1 条 Build / Buy / Extend / Defer 链
1 条 Implementation / Failure / Evidence 交叉链
```

`FULL_INTERVIEW` 再增加岗位基础或 Coding 链。

### 阶段四：现场单问

从被审计对象最近一个 Claim 开始，一次只问一个主问题。收到回答后更新内部假设，再决定下一问。

固定触发：

1. 出现“我们做了” → 强制 Ownership Attack；
2. 出现“自己设计 / 自研” → 强制 Build / Buy / Extend / Defer；
3. 出现“效果提升 / 更准确 / 更快” → 强制 Baseline / Dataset / Metric / Cost；
4. 出现“企业级 / 微服务 / 高并发” → 强制 Scale / Team / Over-engineering；
5. 出现“法院 / 法律 / 合同”而领域模型不匹配 → 强制 A16 Alignment；
6. 出现“框架提供” → 追框架提供到哪一层、Zuno Delta 是什么；
7. 出现“支持恢复 / 幂等 / 安全” → 注入一次真实失败、版本或权限变化；
8. 发现 Current / Target 混淆 → 要求重新分层，不替被审计对象修正。

如果用户说“记不清”，红队不逼用户猜历史。它应该追问最少的记忆锚点，然后把该 Claim 送入蓝队重建流程。

### 阶段五：链停止条件

一条攻击链只有满足以下之一才停止：

```text
A. Claim 已有直接证据且连续反事实仍一致；
B. Claim 明确降为 UNKNOWN / BLUE_PROPOSAL，不再冒充事实；
C. 已暴露 P0/P1 Gap，继续追问不会新增有效信息；
D. 问题已转化为需要代码、实验、公开资料或用户确认的独立任务。
```

不能因为“问了五层”自动停止，也不能为了覆盖更多角度过早换题。

### 阶段六：红队报告

每个 Gap 输出：

```text
Session ID：
Mode：
主画像 / 交叉画像：
起始 Claim：
问题域 / 攻击角度：
连续问题：
回答或文档断点：
已确认事实：
未证实陈述：
严重度：P0 / P1 / P2
建议 Gap 类型：
需要的证据：
是否需要蓝队事实重建：
是否需要蓝队改 Target Architecture：
是否需要工程 / Eval 任务：
```

红队不替蓝队决定最终修复方案。

### 阶段七：Retest 资格

只有蓝队已经完成对应修复、事实确认或范围收缩，Gap 才能进入 `RETEST_PENDING`。复测必须换问法、换反例或换起始 Claim，不能重复背同一答案。

## 三个必测红灯案例

### 小团队却声称 11 个模块

依次追问：11 个是逻辑边界还是部署服务？MVP 真正需要哪几个？谁维护每个边界？哪些能力可以采购、复用或延期？模块之间的通信、状态和故障由谁负责？如果团队规模不支持，Target 应如何分阶段实现？

### WorkBuddy 等通用平台已经存在

依次追问：Zuno 解决的是哪一个未被解决的用户问题？哪些能力可以直接复用？通用 Runtime 替掉以后哪些领域事实仍必须由 Zuno 持有？Zuno 的 Delta 是什么？怎样用真实用户或指标验证差异，而不是用“架构更复杂”证明价值？

### 学校 / 法院背景与当前领域模型可能不一致

依次追问：真实合作是研究、试点、采购还是仅有联系人？实际用户任务是什么？为什么当前 Domain Model 以 Contract / Review 为核心？合同审查是项目历史、Target Profile，还是后来为了形成法律场景新增的设计？如果背景与模型无法建立因果链，记录 `PROJECT_ARCHITECTURE_ALIGNMENT_GAP`，交蓝队重新设计抽象或缩小叙事。

## 反迎合规则

红队不能因为某个设计是当前 accepted Target 就降低攻击强度。Target 可以被推翻。发现下面情况时必须明确建议蓝队重新评审，而不是帮旧架构圆答案：

- 竞品或开源方案已经满足关键 Contract；
- 真实团队和规模无法支撑复杂度；
- 领域模型与真实背景不一致；
- Current 证据长期无法证明核心价值；
- 为通过面试新增的解释无法改善真实架构或产品。
