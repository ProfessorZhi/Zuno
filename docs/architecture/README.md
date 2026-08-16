# Zuno 总体架构文档

`docs/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## Canonical Question

Product、Domain、Logical Capability、Physical Service / Deployment、Data、Security 和 Eval 如何形成一个可恢复、可验证、可被简化或替换的跨层目标闭环？

Round 02 已完成，Canonical Revision 已通过 Review，总体 Target Architecture 已冻结。总体架构说明九个 Logical Responsibility Modules、Platform / Infrastructure Responsibility Layer、Optional Context Provider、三条 E2E Flow、A/B/C Kill Test 和 State / Failure / Recovery 边界。九个责任域不是九个进程或服务；Module Decomposition Gate 已打开，但只授权 Module Design，不自动授权实现。

## 阅读顺序

第一次阅读只读 `architecture.md` 的 Part A：先理解产品问题、责任分层、状态 Owner、失败恢复和替代方案。第二次再读 Part B 的 Contract、State、Retry、Security 和验证要求。

总体架构读懂以后，再进入 [`../modules/README.md`](../modules/README.md)。模块文档现在已经形成 **Design Baseline V1（设计基线 V1）**：每个责任域不仅解释“为什么存在”，还给出上下游、权威事实、主要 Contract、正常流、状态族、失败分类、恢复、持久化、安全、可观测性和 Current / Target / Gap。它们仍然不是九份微服务说明书，也不表示字段、数据库、API 和实现已经冻结。

推荐的模块详细设计顺序不是机械的 01→09，而是：

```text
02 法律领域与工作成果 + 03 知识与证据
→ 08 安全与治理 + 06 工具运行与外部效果
→ 05 专业能力与技能 + 04 智能体运行与控制
→ 07 模型网关 + 09 可观测性与评测
→ 01 应用与集成
```

这个顺序先确定业务事实和证据，再确定可信执行，最后确定智能执行、Provider 和产品组合；它是设计顺序，不是部署或调用顺序。

可读性门的最低问题是：一个不了解 Zuno 的高级工程师，能否不用代码和 Part B 解释“为什么存在、谁拥有状态、失败如何恢复、什么时候应该保持简单或删除复杂度”。工程门的最低问题则是：读完模块 Part B 后，能否知道哪些事实不可旁路、恢复锚点是什么、实现还不能自行决定什么。

## 文件职责

- `architecture.md`：跨层架构正文、九个责任域、全局边界、状态 / 失败 / 恢复语义和 Current / Target / History 解释。
- `architecture-views.md` + `architecture.html`：不可拆分的图源与展示配对，不拥有第二套架构事实。
- `README.md`：目录边界、阅读入口和维护规则，不承载专题 Contract。
- `../modules/`：九个责任域的模块级 Design Baseline V1；字段级 Contract、完整状态枚举、数据库和实现仍需逐模块 Review。

## 重要边界

- 本目录不记录项目故事；这些内容统一在 `../project/`。
- 本目录不记录当前运行证据；可复现证据在 `../evidence/`。
- 本目录不记录实施计划、运维 Runbook 或 ADR；这些分别进入 `.agent/programs/`、`docs/operations/` 和 `docs/decisions/`。
- 旧专题和 11 模块不再作为平行 Canonical；Red / Blue 过程归档见 [`../history/red-blue/README.md`](../history/red-blue/README.md)，旧材料由 Git 历史保留。
- 长期责任分类和跨边界恢复决定见 [ADR-0013](../decisions/0013-round-02-responsibility-taxonomy.md) 与 [ADR-0014](../decisions/0014-round-02-cross-boundary-authority-and-recovery.md)。
- 物理服务拆分继续受 [ADR-0012](../decisions/0012-evidence-gated-physical-service-split.md) 约束；九个逻辑模块不能自动推导九个网络服务。

## 维护

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `../modules/`；图形变化时同步图源和 HTML，再运行：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
```

不得创建第五个架构文件、`.agent/architecture/` 或 `.agent/modules/` 镜像，也不得建立第二套 Domain / Runtime / Service / State registry。
