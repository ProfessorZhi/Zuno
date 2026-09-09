# Zuno Documentation

Zuno 的文档现在只保留八个一级目录。它们不是为了凑成对称结构，而是对应八种长期不同的阅读责任。

```text
System & Review
project/        项目为什么出现：司法背景、研究来源、真实演进、团队与个人参与
architecture/   如果今天重新设计理想 Zuno，总体系统为什么这样工作
modules/        总体架构怎样分解为具体责任，以及每个责任怎样处理正常与失败流程
red-blue/       怎样用业务场景、替代方案和故障反例持续压力测试前三者

Trust & Evolution
research/       哪些论文、算法、平台能力和法院背景可以作为设计输入
 decisions/     哪些长期架构取舍已经正式接受，以及为什么接受
 evidence/      今天的代码、测试、Trace、Eval 和运行实际证明了什么
 governance/    谁拥有事实、文档怎样写、Agent 怎样读取、修改和验证
```

`red-blue/` 是评审系统，不是新的 Architecture Truth Owner。`research/` 是上游依据，也不拥有 Target 或 Current。Project、Architecture、Modules、Decisions、Evidence 和 Governance 继续保持各自唯一事实边界。

## 第一次阅读

第一次接触 Zuno，只走一条主线：

1. [`project/project.md`](./project/project.md) —— 从天津智慧司法与 LIPLAB 研究/工程背景进入，理解项目为什么存在、已有系统是什么、团队和个人实际参与到哪里。
2. [`architecture/architecture.md`](./architecture/architecture.md) Part A —— 从最简单的 Generic Agent Host + Legal RAG + Research Capability baseline 开始，看材料版本、专业资格、正式业务事实、长任务、现实副作用和持续授权怎样逐步逼出新的事实边界。
3. [`modules/README.md`](./modules/README.md) —— 沿同一个法律任务进入局部责任，选择相关 Module Part A 深入。
4. [`evidence/README.md`](./evidence/README.md) —— 回到 Current，检查哪些 Target 今天已经由代码、测试或可复现运行证明。

这条路径必须能够连续形成：

```text
司法与研究背景
→ 已有工程资产
→ 最简单可行方案
→ 真实约束使简单方案失效
→ 总体架构
→ 局部责任
→ 当前证据
```

Red / Blue 不属于第一次阅读路径。正文先达到可独立阅读的教材质量，再使用 [`red-blue/`](./red-blue/README.md) 找作者自己没有发现的 Narrative、Architecture、Evidence、Ownership 或 Simplification Gap。

## Human View 与 Engineering View

Human-facing 文档负责建立 mental model。Project、Architecture 与 Module 的 Part A 先描述现实场景、最简单方案、具体失败、设计如何产生、典型恢复和删除条件，再使用内部术语。

Engineering / Agent View 保存精确规则：Owner、Authority、Contract、Version、Completion Proof、Persistence、Retry / Replan / Reconcile、Security、Failure Matrix 和 Source Map。机器不应从叙事 prose 猜字段或 Current 状态。

实现或审查任务的默认下钻顺序是：

```text
architecture/reference.md
→ architecture.md Part B
→ modules/reference.md
→ selected Module Part B / Part C
→ decisions/
→ evidence/
→ code / schema / migration / tests
```

## 八个一级目录的边界

| Directory | 回答的问题 | 不拥有的东西 |
| --- | --- | --- |
| `project/` | 为什么有 Zuno，项目真实发生过什么，团队和个人做过什么 | Target Architecture、Current 实现证明 |
| `architecture/` | 理想系统的跨责任边界、Authority 与恢复为什么这样设计 | 项目历史、个人 Ownership、Current |
| `modules/` | 每个责任单元内部怎样工作并保护自己的事实 | 新的跨模块 Architecture Truth |
| `red-blue/` | 哪些场景、反例、替代方案仍能击穿当前文档或设计 | Project / Architecture / Evidence Truth |
| `research/` | 论文、算法、司法项目背景和平台 baseline 能提供什么输入 | 已实现、已验证、Production 声明 |
| `decisions/` | 为什么长期接受某个设计选择 | 完整 Architecture Spec、Current Evidence |
| `evidence/` | 今天真正实现和测到了哪里 | Target 设计和历史 Ownership |
| `governance/` | 来源、Owner、写作、术语、Agent workflow、Operations 和验证规则 | 业务 Target 本身 |

文档架构不冻结模块数量。当前九个逻辑责任域仍是现有 Target Architecture 的设计结果；未来合并或拆分必须通过 Architecture Revision / ADR，而不是为了目录好看。

## Current / Target / History / Unknown

- **History**：项目真实过去，主要由 `project/` 与 provenance 维护。
- **Target**：今天接受的理想设计，主要由 `architecture/` 与 `modules/` 维护。
- **Decision**：为什么接受某个长期选择，由 `decisions/` 维护。
- **Current**：代码、Migration、Test、Trace、Eval 或真实运行已经证明的事实，由 `evidence/` 维护。
- **Unknown**：证据不足时保持 Unknown，不使用完整故事替代证据。

Pilot 不等于 Production。导师/课题组成果不等于个人成果。Framework Capability 不等于 Zuno 自研。论文结果不等于 Provider 已 qualified。

## 文档之外的运行入口

`.agent/` 保存机器路由与临时运行状态，不保存第二套业务事实。Red / Blue 的方法和历史归 `docs/red-blue/`，机器 active state 仍可以放在 `.agent/red-blue/`；Agent/GitHub 协作规则与运维 Runbook 归 `docs/governance/workflows/` 和 `docs/governance/operations/`。

出现冲突时，不用目录层级机械裁决。先判断争议属于 History、Target、Decision、Current 还是 Rules，再回对应 Owner。详细规则见 [`governance/documentation-architecture.md`](./governance/documentation-architecture.md)。