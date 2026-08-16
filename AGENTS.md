# Zuno Agent 入口

这是仓库唯一的 Agent 工作入口。先从问题本质和当前证据出发，不从旧目录、惯例或架构模板倒推答案；事实不清时保留 `UNKNOWN`，不要用 Target 设计填空。

## 正式文档 Owner

```text
docs/project/                         项目级 Human-first 叙事；只保留 README.md + project.md
docs/architecture/                    总体 Target Architecture，固定四文件
docs/modules/                         九个冻结 Target 责任域的 Deep Design V2 正文与入口
docs/decisions/                       仍然有效的长期 ADR
docs/evidence/                        当前代码、测试、Trace、Eval 和运行证据
docs/governance/project-fact-provenance.md  项目事实来源、事实台账与表述边界
docs/governance/human-first-documentation-standard.md  Human-first 文档写作与分工规则
docs/history/red-blue/                Red / Blue 架构审查过程记录，不是事实或架构源
docs/operations/                      当前仍需执行的运维 Runbook / recovery profile
docs/terminology.md                   跨文档术语
.agent/                               Agent 路由、规则、Program 和验证入口
```

Git history 是普通文件演进和已删除工作区材料的考古来源。当前树不维护 `facts`、旧模块专题、旧 Program 垃圾场或第二套项目故事。

## 文档边界

- `docs/project/README.md` 是很薄的 Project 导航，不维护第二套项目故事。
- `docs/project/project.md` 是唯一项目级 Human-first 主文档，集中回答项目为什么出现、为什么值得立项、为什么不只用通用平台、项目怎样发展、团队和个人参与、哪些差异已经证明以及项目级 Reviewer / 技术面试追问。
- `docs/governance/project-fact-provenance.md` 保存项目事实来源、允许表述、禁止扩张和下一步取证要求；它是事实账本，不替代 Project 叙事。
- `docs/architecture/architecture.md` 是唯一总体架构正文；`architecture-views.md` 与 `architecture.html` 是展示配对，不能拥有第二套架构事实。
- `docs/modules/README.md` 是模块导航、任务主线和跨模块 Ownership 入口；`01-*.md` 到 `09-*.md` 当前达到 Deep Design V2 / Cross-Module Consistency，并拥有扩充后的 Human-first Part A，但仍不是 Current Evidence、独立服务清单或默认实现授权。
- Red / Blue Archive 记录为什么质疑和怎样判断，不等于 Architecture Truth、Current Evidence、ADR 或实施授权。
- `Current` 由代码、测试和 Evidence 证明；`Target` 是设计；`Future` 是可选方向；`History` 只解释过去。`Pilot` 不等于 `Production`。

## 必读顺序

一般项目、架构或文档任务：

1. `docs/README.md`
2. `docs/project/project.md`
3. `docs/architecture/architecture.md`：理解系统时先读 Part A；实现、测试、Migration、Recovery、Contract 或 Security 时再读 Part B。
4. 需要看图时同时读 `architecture-views.md` 与 `architecture.html`。
5. `docs/modules/README.md`；若任务属于某个责任域，再读对应 `docs/modules/0X-*.md`。先读 Part A 理解问题和业务流程，再读 Part B 的 B1–B14、Part C 一致性、相关 ADR、`docs/evidence/README.md` 和 Human-first 标准。
6. `.agent/README.md`、`.agent/system.yaml`、`.agent/references/`。

实现任务必须在读完 Project 必要上下文、总体架构 Part A / B、相关模块 Part A / B / C、ADR、Evidence 和 Governance 后再读代码。不要把类名、目录、依赖、Mock、目标文档或测试存在当成生产证据。

## 项目问题与架构问题不要混在一起

“为什么项目可以立项”“为什么不用通用平台”“项目走到了什么阶段”“我个人历史上做了什么”优先回 `docs/project/project.md`。个人贡献仍只能使用已经恢复的历史事实，不能用今天由 ChatGPT / Codex 维护的架构文档反推。

“谁拥有这个状态”“为什么 Checkpoint 不能证明正式提交”“POST 超时怎样恢复”“权限撤销后谁重新门禁”属于 Architecture / Module 问题。

“现在实现了吗”“正式 benchmark 跑了吗”“Full CI 通过了吗”只回 `docs/evidence/` 和真实 workflow / runtime 结果。

## 架构文档治理

`docs/architecture/` 只能有：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `docs/modules/`；项目来源、定位、开发故事、参与事实和项目级 Reviewer 叙事进入 `docs/project/project.md`；图形变化时同步图源和 HTML，再运行相关文档验证。不要创建 `.agent/architecture/` 或 `.agent/modules/` 镜像。

Round 02 已冻结九个 Target 责任域并打开 Module Decomposition Gate。九篇模块当前达到：

```text
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_freeze: NOT_YET
implementation_authorization: NO
```

这表示主要边界、Owner、跨模块 Contract、状态族、失败、恢复、安全、持久化、取消 / 晚到和一致性语义已经可以接受详细审查；不表示字段级 Contract、最终 enum、数据库表、Migration 或实现已经冻结。

如果模块详细设计发现必须新增 / 删除逻辑模块、改变总体 Owner、扩大 Canonical Legal Kernel、改变 AdmissionReceipt / invalidation / lifecycle / security 等跨模块不变量，必须停止并升级为 Architecture Gap，不能在模块文件中偷偷改总体架构。

## Red / Blue 规则

Red / Blue 是人工协调的 Architecture Stress Test。它可以讨论 Multi-Agent、Runtime、Knowledge 等复杂边界，但不把工程协作多线程写成 Zuno Runtime 事实。原始记录进入 `docs/history/red-blue/`；接受的结果必须写回 `docs/architecture/`、`docs/modules/` 或 `docs/decisions/`。

FACT GAP 要回到用户确认和 `docs/project/project.md` / `project-fact-provenance.md`；Architecture Gap 才能进入架构修订。不得将 Red Concern、Blue Proposal 或 Round 内容自动实现。

## 修改、验证和提交

- 不修改业务代码、数据库、Migration、依赖或安全边界，除非用户明确授权。
- 不覆盖用户已有未提交修改；提交前检查 `git status --short`，只暂存本任务范围。
- 文档修改完成后至少运行 `git diff --check`、文档入口、内部链接、结构、Agent 路由和边界验证；按风险运行 focused tests。
- 真实修改任务必须验证、Commit、Push，除非明确阻塞；只读审计不提交。
- 不声称 `FULL CI PASSED`，除非完整 CI 确实执行并通过。

常用命令：

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

更多路由见 `.agent/references/task-routing.md` 和 `.agent/references/workflow.md`。
当前 Program 状态见 `.agent/references/current-program.md`；验证地图见 `.agent/references/verification-map.md`；机器路由见 `.agent/system.yaml`。
