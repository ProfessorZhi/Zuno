# Human-first 文档标准

本文约束 Zuno 的文档写作方式，不改变项目事实、Target Architecture、模块边界或历史记录。它把面向人的解释文档与面向工程和 Agent 的证明材料分开，避免所有文档都变成同一种状态表或 Prompt。

## 两类文档

Human-first 文档首先服务新工程师、开发者、架构师、技术负责人、项目合作人员和人类 Reviewer：

- `docs/project/`：项目从哪里来、谁参与、怎样发展；
- `docs/architecture/`：今天认为系统应该怎样组织，以及为什么；
- `docs/modules/`：已冻结责任域内部怎样工作；
- `docs/history/`：设计为什么后来变成今天这样。

Engineering / Agent-first 文档主要服务 Codex、Validator、Reviewer、Operator 和证据核验：

- `docs/evidence/`：代码、测试、Trace、Eval 和运行证据；
- `docs/operations/`：Runbook、部署和恢复操作；
- `docs/governance/`：来源、Owner、Contract、写作规则和 Validator 约束；
- `docs/decisions/`：长期有效的 ADR；
- `.agent/`：路由、自动化和机器上下文。

原则是：Human documents explain，Engineering documents prove，Governance documents constrain。各层通过链接互相查找，不复制另一层的完整内容。

## Human-first 的写法

人打开文档的第一屏应该先知道“这是什么、解决什么问题、现在进行到哪里”。标题后优先使用两三段自然语言，不要让一长串 `status`、编号、Contract 或状态码挡住入口。机器需要的元信息可以放在 HTML comment、front matter 或“当前状态”小节中。

先讲问题和业务场景，再介绍正式术语。例如先说明 Agent 的候选结论为什么不能直接成为案件正式结果，再解释实现层的 Admission、Version 或 Receipt。英文专有名词保留必要的名称，普通概念尽量使用中文，并在第一次出现时给出中英文对照。

表格和 Mermaid 只用来帮助理解关系。表格前要有解释；一张图只表达一个核心关系，优先保留 5–12 个节点。字段级 Contract、完整状态机、错误类型和验证命令应链接到 Governance、Evidence、Decision 或模块工程参考，而不是全部堆在入口文档。

## 四类文档的分工

Project 讲历史和项目事实，不把 Target 设计写成过去已经实现的能力。Architecture 讲总体 Target，不因为 Red Concern 或当前目录存在就自动冻结模块。Modules 只有在模块分解闸门打开后才建立详细正文。History 保留原始问答和演进依据，不成为 Canonical Architecture。

Human-first 不等于营销，不等于删除不确定性，也不等于降低技术严谨性。文档不能添加“行业领先”“生产级”“全面覆盖”等没有证据的宣传；也不能把未知内容改写成确定事实。需要精确来源时链接 Governance，需要当前实现证明时链接 Evidence，需要长期决定时链接 ADR。

## 当前状态与历史保护

`Current`、`Target`、`Future` 和尚未恢复的历史信息必须继续区分。Round Archive 的 Red Question、Blue Answer、Red Review、Reflection 和 Main Judgment 是 append-only 历史，不能为了可读性润色、缩写或重排；可读性通过 README 和摘要解决。

模块 README 可以解释候选边界和开放问题，但不能把候选写成冻结模块。逻辑模块也不自动等于进程、容器、数据库、Worker 或团队；物理部署需要自己的证据门槛。

## 验证原则

Validator 适合检查入口存在、链接有效、目录边界、Raw Archive 未被删除、模块闸门关闭时没有模块正文，以及 Current / Target / History 的路由没有混淆。不要用“每篇必须有几个标题”或“每段不能超过多少字”冒充可读性证明；人类阅读审查仍然是必要步骤。
