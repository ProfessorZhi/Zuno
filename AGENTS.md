# Zuno Agent 入口

这是仓库唯一的 Agent 工作入口。先从问题本质和当前证据出发，不从旧目录、惯例或架构模板倒推答案；事实不清时保留 `UNKNOWN`，不要用 Target 设计填空。

## 正式文档 Owner

```text
docs/project/                         项目级 Human-first 叙事；只保留 README.md + project.md
docs/architecture/                    总体 Target Architecture，固定四文件
docs/modules/                         九个冻结 Target 责任域；Deep Design V2 + Detail Design Candidate V1（9/9）
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
- `docs/project/project.md` 是唯一项目级 Human-first 主文档，集中回答项目为什么出现、为什么值得立项、为什么不只用通用平台、项目怎样发展、团队和参与事实、哪些差异已经证明以及项目级 Reviewer / 技术面试追问。
- `docs/governance/project-fact-provenance.md` 保存项目事实来源、允许表述、禁止扩张和下一步取证要求；它是事实账本，不替代 Project 叙事。
- `docs/architecture/architecture.md` 是唯一总体架构正文；`architecture-views.md` 与 `architecture.html` 是展示配对，不能拥有第二套架构事实。
- `docs/modules/README.md` 是模块导航、任务主线和跨模块 Ownership 入口；`01-*.md` 到 `09-*.md` 都达到 Deep Design V2 / Cross-Module Consistency，并在 B14.1–B14.8 进入 Detail Design Candidate V1。Candidate 不是 Current Evidence、服务清单、数据库冻结或默认实现授权。
- Red / Blue Archive 记录为什么质疑和怎样判断，不等于 Architecture Truth、Current Evidence、ADR 或实施授权。
- `Current` 由代码、测试和 Evidence 证明；`Target` 是设计；`Future` 是可选方向；`History` 只解释过去。`Pilot` 不等于 `Production`。

## 必读顺序

一般项目、架构或文档任务：

1. `docs/README.md`
2. `docs/project/project.md`
3. `docs/architecture/architecture.md`：理解系统时先读 Part A；实现、测试、Migration、Recovery、Contract 或 Security 时再读 Part B。
4. 需要看图时同时读 `architecture-views.md` 与 `architecture.html`。
5. `docs/modules/README.md`；属于某个责任域时读对应 `docs/modules/0X-*.md`。先读 Part A，再读 B1–B14、Part C、相关 ADR、Evidence 和 Human-first 标准。
6. 字段级 Contract、DB / Manifest / Checkpoint / Registry、并发、Migration、Crash Window 或 Failure Injection 任务必须继续读该模块 B14.1–B14.8；这些是 Detail Freeze Candidate，不得跳过 B1–B13 / Part C 单独实现。
7. `.agent/README.md`、`.agent/system.yaml`、`.agent/references/`。

实现任务必须先读 Project 必要上下文、总体架构 Part A/B、相关模块 Part A/B/C（含 B14.1–B14.8）、ADR、Evidence 和 Governance，再读代码。不要把类名、目录、依赖、Mock、Target 文档或测试存在当成 Production Evidence。

## 项目问题与架构问题不要混在一起

“为什么项目可以立项”“为什么不用通用平台”“项目走到了什么阶段”“历史参与者做了什么”优先回 `docs/project/project.md`。个人贡献只能使用已经恢复的历史事实，不能用今天的 Target 文档反推。

“谁拥有这个状态”“为什么 Checkpoint 不能证明正式提交”“POST 超时怎样恢复”“权限撤销后谁重新门禁”“字段 / CAS / Crash Window 怎样闭合”属于 Architecture / Module 问题。

“现在实现了吗”“正式 benchmark 跑了吗”“Full CI 通过了吗”只回 `docs/evidence/` 和真实 workflow / runtime 结果。

## 架构文档治理

`docs/architecture/` 只能有：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `docs/modules/`；项目来源、定位、开发故事和参与事实进入 `docs/project/project.md`；图形变化时同步图源和 HTML。不要创建 `.agent/architecture/` 或 `.agent/modules/` 镜像。

Round 02 已冻结九个 Target 责任域。当前模块状态：

```text
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V2
module_deep_design_coverage: 9/9
cross_module_consistency: AVAILABLE_V1
module_human_narrative: DEEPENED
module_detail_design_candidate: AVAILABLE_V1
module_detail_design_candidate_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
```

这表示九个模块的 Owner、跨模块 Contract、状态 / 失败 / 恢复、安全 / 持久化、取消 / 晚到和一致性已经深化，并把冻结前字段、版本 / 新鲜度 Guard、幂等、事务 / 持久化、Crash Window、Schema Evolution 和 Failure Injection 写入 B14.1–B14.8。

**Candidate 仍不是 Freeze。** 下一道门是 Module Detail Freeze Review。没有完成冻结审查和用户明确 Implementation Authorization 时，不创建大规模业务表、Migration 或 Runtime 实现。

Codex 不得自行改变以下总体原则：九个责任域；七对象最小领域内核；EvidenceCandidate / Evidence 与 CitationLineage / WorkProductCitationBinding 分离；Domain mutation + matching AdmissionReceipt 同领域事务；PostgreSQL Domain facts 与 LangGraph Checkpointer 控制状态分离；KnowledgeGeneration / task Readiness 分离；validated manifest 才 Serving；Single Controller；所有 Native Runtime entrant 有 Plan；Retry / Replan / Reconcile 分离；Outcome Unknown 不盲重试；08 持续授权；Telemetry 不替代 Durable Audit / Business Truth；跨 Store 默认无 2PC；复杂机制继续 Evidence / Measurement gated。

如果 Detail Candidate / Freeze Review 发现必须新增 / 删除逻辑模块、改变总体 Owner、扩大 Canonical Legal Kernel、改变 Admission / Invalidation / Lifecycle / Security / Effect 等跨模块不变量，停止局部设计并升级 Architecture Gap，不能在字段、Migration 或代码里偷偷改变总体架构。

## Detail Freeze Review 规则

进入某模块冻结审查时，至少逐项确认：

- B14.1–B14.8 与 Part A、B1–B13、Part C 是否同义；
- 核心 identity / version / freshness 是否足够且无第二 Owner；
- 状态转换 Guard、幂等 namespace、事务 / CAS、Crash Window 是否闭合；
- Cancel / Late Result / Retry / Replan / Reconcile 是否不会伪造历史；
- Migration / Upgrade 是否保留历史和 paused / pending work；
- Failure Injection 是否覆盖并发、权限变化、响应丢失、重复投递和恢复；
- 是否引入没有证据支持的微服务、全局锁、2PC、Event Sourcing 或第二套 Runtime。

只有这些问题在模块内部和跨模块都闭合，才考虑把该模块从 Candidate 升到 Detail Freeze。

## Red / Blue 规则

Red / Blue 是人工协调的 Architecture Stress Test。它可以盘问 Runtime、Knowledge、Domain、Tool、Security 等边界，但不把工程协作多线程写成 Zuno Runtime 事实。原始记录进入 `docs/history/red-blue/`；接受的结果必须写回 Architecture / Module / ADR。

FACT GAP 回到用户确认和 Project / fact provenance；Architecture Gap 才进入架构修订。不得将 Red Concern、Blue Proposal 或 Round 内容自动实现。

## 修改、验证和提交

- 不修改业务代码、数据库、Migration、依赖或安全边界，除非用户明确授权。
- 不覆盖用户已有未提交修改；提交前检查目标 SHA / main 漂移和任务范围。
- 文档修改完成后至少验证 docs entrypoints、内部链接、repo structure、Agent system、doc boundaries 和对应 focused tests。
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

更多路由见 `.agent/references/task-routing.md` 和 `.agent/references/workflow.md`。当前 Program 状态见 `.agent/references/current-program.md`；验证地图见 `.agent/references/verification-map.md`；机器路由见 `.agent/system.yaml`。