# 文档与 Agent 工作流

## Source of truth

`AGENTS.md` 是仓库规则入口；`.agent/system.yaml` 是机器路由。

Canonical docs 使用 3 + 3 模型：

```text
System Story:
project / architecture / modules

Knowledge Control:
decisions / evidence / governance
```

`research/` 只提供上游研究依据，`maintenance/` 只提供运行、协作和历史附件；两者都不能覆盖 Project、Architecture、Modules 或 Evidence。

完整文档架构见 `docs/governance/documentation-architecture.md`，机器导航见 `.agent/references/docs-map.md`。

## 文档修改

1. 确认 latest main SHA 和用户已有修改。
2. 先判断任务属于 Project、Architecture、Module、Decision、Evidence 还是 Governance。
3. Human Narrative 任务优先读对应 Part A；实现和精确 Review 必须读 Architecture / Module machine reference。
4. 先定义 Canonical Owner、边界和迁移清单，再修改。
5. Research 结论进入 canonical docs 前区分 lineage，并由真正 Owner 接纳；Research 本身不升级为 Target/Current。
6. 实施前必须读取 Evidence，禁止把 Target Contract 当成已实现。
7. 修改 Owner / Authority / Recovery / Security 时同步 Architecture、相关 Module、ADR 和 semantic validators。
8. 运行 focused tests、文档验证和 diff review；按用户约定完成 merge / direct-main 后重新读取 exact main HEAD。

## Human / Machine dual view

Human View 负责理解和面试：现实问题 → baseline → baseline failure → design causality → flow → failure/recovery → trade-off。

Machine View 负责实施：Owner → Fact → Contract → Version → Completion Proof → Persistence → Idempotency → Recovery → Security → Failure Matrix → Source Map。

两种视图共享事实语义，但不需要共享文章结构。

## Research

```text
paper / platform / external material
→ verify source
→ record as upstream reference
→ decide Project / Architecture / Module relevance
→ canonical Owner accepts or rejects
→ Current still requires Evidence
```

## Red / Blue and maintenance

Red / Blue、Operations、Agent workflow 和历史审查仍保留在 `docs/maintenance/` 兼容路径，并由 Governance 管理。它们可以发现 Gap，但不能直接成为 Project / Architecture / Current truth。

## 清理与收尾

迁移只删除已经有稳定新 Owner 的副本。不要为了目录整齐复制第二套事实，也不要删除代码、Migration、可复现 Evidence 或用户未确认的资产。
