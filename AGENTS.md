# Zuno Agent 入口

这是仓库唯一的 Agent 工作入口。先从问题本质和当前证据出发，不从旧目录、惯例或架构模板倒推答案；事实不清时保留 `UNKNOWN`，不要用 Target 设计填空。

## 正式文档 Owner

```text
docs/project/                         人类可读的项目故事入口（README、背景、团队、开发过程）
docs/architecture/                    总体 Target Architecture，固定四文件
docs/modules/                         九个冻结 Target 责任域的模块设计正文与入口
docs/decisions/                       仍然有效的长期 ADR
docs/evidence/                        当前代码、测试、Trace、Eval 和运行证据
docs/governance/project-fact-provenance.md  项目事实来源与表述边界
docs/governance/human-first-documentation-standard.md  Human-first 文档写作与分工规则
docs/history/red-blue/                Red / Blue 架构审查过程记录，不是事实或架构源
docs/operations/                      当前仍需执行的运维 Runbook / recovery profile
docs/terminology.md                   跨文档术语
.agent/                               Agent 路由、规则、Program 和验证入口
```

Git history 是普通文件演进和已删除工作区材料的考古来源。当前树不维护 `facts`、旧模块专题、旧 Program 垃圾场或第二套项目故事。

## 文档边界

- `docs/project/README.md` 是第一次进入项目故事时的简短导航。
- `docs/project/project-background.md` 回答项目为什么存在、研究与法院背景、用户问题、产品故事和仍未恢复的事实。
- `docs/project/team-and-contributions.md` 回答团队规模、用户何时加入、实际参与方向和个人职责边界。
- `docs/project/development-process.md` 回答项目如何从已有代码发展到 Agent、Memory / Context、Tool Calling、Demo、法院测试和 Pilot。
- `docs/governance/project-fact-provenance.md` 保存给 Reviewer / Agent 使用的项目事实来源边界；它不替代 Project 故事。
- `docs/architecture/architecture.md` 是唯一总体架构正文；`architecture-views.md` 与 `architecture.html` 是展示配对，不能拥有第二套架构事实。
- `docs/modules/README.md` 是模块导航、三条任务主线和跨模块 Ownership 入口；`01-*.md` 到 `09-*.md` 是模块级 `design-baseline-v1`，不是 Current Evidence、独立服务清单或默认实现授权。
- Red / Blue Archive 记录为什么质疑和怎样判断，不等于 Architecture Truth、Current Evidence、ADR 或实施授权。
- `Current` 由代码、测试和 Evidence 证明；`Target` 是设计；`Future` 是可选方向；`History` 只解释过去。`Pilot` 不等于 `Production`。

## 必读顺序

一般项目、架构或文档任务：

1. `docs/README.md`
2. `docs/project/README.md`
3. `docs/project/project-background.md`
4. `docs/project/team-and-contributions.md`
5. `docs/project/development-process.md`
6. `docs/architecture/architecture.md`：理解系统时先读 Part A；实现、测试、Migration、Recovery、Contract 或 Security 时再读 Part B。
7. 需要看图时同时读 `architecture-views.md` 与 `architecture.html`
8. `docs/modules/README.md`；若任务属于某个责任域，再读对应 `docs/modules/0X-*.md`。先读 Part A 理解问题和业务流程，再读 Part B 的 B1–B14、相关 ADR、`docs/evidence/README.md` 和 Human-first 标准。
9. `.agent/README.md`、`.agent/system.yaml`、`.agent/references/`

实现任务必须在读完总体架构 Part A / B、相关模块 Part A / B、ADR、Evidence 和 Governance 后再读代码。不要把类名、目录、依赖、Mock、目标文档或测试存在当成生产证据。

## 架构文档治理

`docs/architecture/` 只能有：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `docs/modules/`；图形变化时同步图源和 HTML，再运行相关文档验证。不要创建 `.agent/architecture/` 或 `.agent/modules/` 镜像。

Round 02 已冻结九个 Target 责任域并打开 Module Decomposition Gate。当前九篇模块正文已经形成 `Design Baseline V1`：主要边界、Owner、跨模块 Contract、状态族、失败语义、恢复、安全、持久化和验证方向可作为后续逐模块详细设计基线，但不代表字段级 Module Freeze，也不授权 Codex 自动实现全部模块。

如果模块详细设计发现必须新增 / 删除逻辑模块、改变总体 Owner、扩大 Canonical Legal Kernel、改变 AdmissionReceipt / invalidation / lifecycle / security 等跨模块不变量，必须停止并升级为 Architecture Gap，不能在模块文件中偷偷改总体架构。

## Red / Blue 规则

Red / Blue 是人工协调的 Architecture Stress Test。它可以讨论 Multi-Agent、Runtime、Knowledge 等复杂边界，但不把工程协作多线程写成 Zuno Runtime 事实。原始记录进入 `docs/history/red-blue/`；接受的结果必须写回 `docs/architecture/`、`docs/modules/` 或 `docs/decisions/`。

FACT GAP 要回到用户确认和 `docs/project/`；Architecture Gap 才能进入架构修订。不得将 Red Concern、Blue Proposal 或 Round 内容自动实现。

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
