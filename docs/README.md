# Zuno Documentation

Zuno 的主文档只围绕六个长期问题组织。前三个目录描述系统本身，后三个目录约束我们怎样决定、证明和维护这些描述。

```text
System Story
project/        我们为什么来到这里：背景、历史、团队、个人参与、项目约束
architecture/   理想的 Zuno 应该怎样工作：总体 Target Architecture
modules/        总体架构怎样分解为具体责任单元，以及这些单元怎样协作

Knowledge Control
decisions/      为什么接受某个长期设计决定
evidence/       今天到底实现、测试和证明到了哪里
governance/     谁拥有事实、文档怎样维护、Agent 怎样读取和修改
```

> 根规则：**Project 解释现实，Architecture 描述目标，Modules 分解责任；Decisions 保存理由，Evidence 证明现实，Governance 保护真相。**

## 第一次阅读：只走一条主线

第一次理解 Zuno，不需要先读 Research、ADR、CI、Red/Blue 或大量 Contract。按下面顺序建立 mental model：

1. [`project/project.md`](./project/project.md) —— 项目为什么出现、经历过什么、团队和个人实际做过什么。
2. [`architecture/architecture.md`](./architecture/architecture.md) Part A —— 从简单法律问答开始，理解材料版本、候选、正式业务事实、长任务、恢复和现实副作用怎样推导出总体架构。
3. [`modules/README.md`](./modules/README.md) —— 沿一项法律工作理解当前 Target decomposition，再选择相关模块 Part A 深入。
4. [`evidence/README.md`](./evidence/README.md) —— 最后回到代码、测试、Trace、Eval 和运行事实，检查哪些 Target 今天已经 Current。

这四步形成完整故事：

```text
真实项目
→ 原始工程问题
→ 理想总体架构
→ 责任分解
→ 当前证据
```

面试也使用同一条主线：项目背景和个人角色从 Project 讲起，系统设计进入 Architecture，深挖某个问题时进入对应 Module；只有被追问“现在真的实现了吗”才切到 Evidence。不要为了面试单独维护第二套项目故事。

## 两种阅读视图

Zuno canonical docs 同时服务人和机器，但两者需要不同的信息密度。

### Human View

Part A 给人连续阅读。它负责解释现实场景、简单 baseline、为什么 baseline 开始失效、架构如何从约束中产生、典型故障如何恢复，以及什么时候可以删除复杂度。

Part A 可以重排章节和改写语言，只要不改变事实层级、Owner、Authority、Recovery 和 Current/Target。

### Engineering / Agent View

机器入口以 `reference.md` 或现有文档的 Part B 为主。它负责稳定索引：Owner、Authoritative Fact、Contract、Version、Completion Proof、Retry/Replan/Reconcile、Persistence、Security、Failure 和 Source Map。

机器不应从 Human Narrative 猜字段或实现状态。涉及实现时按以下顺序读取：

```text
architecture/reference.md
→ modules/reference.md
→ 目标模块 Part B / Part C
→ decisions/
→ evidence/
→ code / schema / migration / tests
```

## 六个 canonical domain

| Domain | Canonical question | Human entry | Machine / precise entry |
| --- | --- | --- | --- |
| `project/` | 这个项目为什么存在，历史和个人参与是什么？ | `project.md` | `reference.md` + governance provenance |
| `architecture/` | 理想系统应该怎样工作？ | `architecture.md` Part A | `reference.md` + `architecture.md` Part B |
| `modules/` | 总体设计分解成哪些责任，它们怎样工作？ | `README.md` + Module Part A | `reference.md` + Module Part B/C |
| `decisions/` | 为什么接受某个长期约束？ | ADR 正文 | ADR metadata / decision record |
| `evidence/` | 今天实际证明了什么？ | Evidence README | code/test/trace/eval references |
| `governance/` | 哪份信息由谁拥有，怎样保持一致？ | `README.md` | `documentation-architecture.md` + provenance/ownership rules |

文档架构本身不冻结模块数量。当前 Target Architecture 仍可采用现有九个逻辑责任域，但“九个”是系统设计结果，不是 Documentation Architecture 的先验约束；未来责任合并或拆分必须由 Architecture / ADR 推导，而不是为了目录整齐。

## Current / Target / Unknown

三种事实层级必须始终分开：

- **Current**：今天只能由代码、Migration、Test、Trace、Eval 或真实运行结果证明；主要进入 `evidence/`。
- **Target**：今天接受的理想设计；主要进入 `architecture/` 与 `modules/`，不能自动升级成已实现。
- **Unknown**：当前证据不足的历史、个人任务、质量、Pilot 或生产事实；保持 Unknown，直到新的可靠证据出现。

Project 还可以维护 **History**，但 History 不能覆盖 Current，也不能把今天的 Target 反写成过去已经采用的设计。

## 支持材料与兼容目录

当前仓库仍保留 `research/`、`maintenance/` 和根级 `terminology.md`，以避免一次迁移制造大面积断链。它们从现在起不再作为与六个 canonical domain 平级的 Truth Owner：

- `research/` 是 Project / Architecture 的上游参考材料，只能提出和校准设计，不能覆盖 Target 或 Current；
- `maintenance/` 是 Governance 的运行附件，保存 Agent workflow、Operations、Red/Blue 和历史记录；
- `terminology.md` 是 Governance 管理的跨文档术语表。

后续可以按链接成本逐步物理迁移，但迁移不能复制第二套事实。

## Truth hierarchy

出现冲突时按下面顺序处理：

```text
Current code / migration / test / trace / eval
> canonical Project / Architecture / Module facts
> accepted ADR
> historical review / research
> speculation
```

其中 Target 文档可以规定未来应该怎样实现，却不能证明今天已经实现；History 可以解释项目怎样走到今天，却不能证明当前代码仍然采用历史实现；团队成果和个人成果也必须严格分开。
