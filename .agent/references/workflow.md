# 文档与 Agent 工作流

## Source of truth

`AGENTS.md` 是仓库规则入口；`.agent/system.yaml` 是机器路由。

Canonical docs 使用 System & Review + Trust & Evolution 两组责任：

```text
System & Review:
project / architecture / modules / red-blue

Trust & Evolution:
research / decisions / evidence / governance
```

`research/` 只提供上游研究依据；`red-blue/` 只拥有面试 / 对抗评审过程。两者都不能覆盖 Project、Architecture、Modules 或 Evidence 的事实 Authority。

完整文档架构见 `docs/governance/documentation-architecture.md`，机器导航见 `.agent/references/docs-map.md`。

## 文档修改

1. 确认 latest main SHA 和用户已有修改。
2. 先判断任务属于 Project、Architecture、Module、Decision、Evidence、Governance 还是 Red/Blue Review。
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

## Resume-first Red / Blue

Red / Blue 路由为：

```text
docs/red-blue/README.md             Human method
docs/red-blue/workspace/README.md   Active workspace contract
docs/red-blue/rounds/               Closed round history
.agent/red-blue/                     Machine protocol / current state / Red Skill
```

正式 Round：

```text
Resume Builder reads current Zuno docs / Evidence
→ builds and freezes 01_simulated_resume.md
→ Red reads only resume + JD + attack-model.md + general knowledge
→ Blue reads resume + Red questions + allowed Zuno docs
→ Red Evaluation reads resume + questions + Blue answers, still no Zuno docs
→ Blue Architecture Reflection routes actual gaps
→ Workflow Retrospective audits Red quality and harness quality
→ user feedback is preserved
→ close / archive
```

一个 Round 默认一批 100 问。需要修复或再测时，新建 Round 并重新生成模拟简历，不在旧 Round 继续追加问题。

Round 不能直接成为 Project / Architecture / Current Truth，也不能在同一轮里修改 Skill / docs 后重新宣布通过。

## 可导出的 Skills

稳定以后可以抽方法为 Skill，但 Skill 不携带与仓库竞争的 Zuno Truth。

优先级：

1. Resume-first Red Interview Skill；
2. Research → Architecture Traceability；
3. GitHub Architecture Review Closure；
4. Human-first Architecture Documentation Review。

Red Skill 沉淀 Claim 取证、精品思维、全链路追踪、Ownership、Build/Buy、故障反例、Evidence、项目下钻基础与 Simplification；不打包 Zuno Architecture 正文或历史 Blue 标准答案。

## 清理与收尾

迁移只删除已经有稳定新 Owner 的副本。不要为了目录整齐复制第二套事实，也不要删除代码、Migration、可复现 Evidence 或用户未确认的资产。

## Current / Target 铁律

不得把：

- 设计文档 → 已实现；
- Demo / Pilot → Production；
- 团队/导师成果 → 个人实现；
- Framework capability → Zuno 自研；
- “应该可以” → “已经验证”。

需要时明确写 `Current / Target / Evidence / Unknown / Measurement Needed`。