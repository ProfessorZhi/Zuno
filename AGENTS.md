# Zuno Agent 入口

这是仓库唯一的 Agent 工作入口。先判断任务属于 Project、Architecture、Modules、Red / Blue、Research、Decisions、Evidence 还是 Governance，再读取对应 Owner。事实不清时保留 `UNKNOWN`；不要用 Target、论文、历史 Round 或模型常识填补事实空白。

## docs/ 八个一级目录

```text
System & Review
docs/project/            项目背景、历史、团队与个人参与
docs/architecture/       总体 Target Architecture
docs/modules/            Target 责任分解与模块内部设计
docs/red-blue/           对抗性架构/项目评审方法与 Round 归档

Trust & Evolution
docs/research/           上游论文、算法、法院背景、平台 baseline
docs/decisions/          已接受的长期 ADR / rationale
docs/evidence/           Current code/test/trace/eval/runtime evidence
docs/governance/         provenance、ownership、写作、术语、workflow、operations、validation
```

`.agent/` 是机器路由和临时运行状态，不拥有第二套业务事实。

## 事实边界

- `docs/project/README.md` 是项目级 Human-facing 主文档。Project 解释为什么存在、真实演进、团队和个人参与；不拥有 Target Architecture 或 Current 实现证明。
- `docs/governance/project-fact-provenance.md` 是项目事实账本。导师/团队成果、个人成果、Pilot、Court-side Testing、Production 必须按证据等级区分。
- `docs/research/` 是设计输入。论文提出不等于 Zuno 已实现；法院项目背景不等于 Zuno 已部署；Framework Feature 不等于 Zuno 自研。
- `docs/architecture/README.md` 保存跨责任 Target Architecture；Part A 给人读，Part B 保存精确语义。Architecture Story 可以用概念演化解释设计，但不得伪造成真实项目历史。
- `docs/modules/README.md` 是责任导航。模块正文按语义目录组织：`application/`、`domain/`、`knowledge/`、`runtime/`、`capability/`、`effects/`、`model-gateway/`、`security/`、`evaluation/`。当前 01–09 编号仍是现有 Target 的责任编号，但不再编码进文件路径。
- 每个模块 `README.md` 当前仍同时包含 Part A / Part B / Part C；后续可以在不改变语义的前提下把 Engineering Reference 拆成独立 `reference.md`，但不能复制第二套事实。
- `docs/decisions/` 保存长期接受的 Architecture Decision，不复制完整 Architecture Spec。
- `docs/evidence/` 是 Current Authority。只有代码、Migration、Test、Trace、Eval 或可复现运行能把 Target 提升为 Current。
- `docs/red-blue/` 只拥有评审方法、Transcript 和 Findings。Red Concern、Blue Proposal、AI 共识、旧 Round 都不能直接改变 Project / Architecture / Evidence。
- `docs/governance/terminology.md` 保存跨文档术语；`docs/governance/workflows/` 保存人类/Agent/GitHub 协作规则；`docs/governance/operations/` 保存 Runbook。Runbook 存在不证明 Production Readiness。

## 默认阅读路径

理解项目：

```text
docs/README.md
→ docs/project/README.md
→ docs/architecture/README.md Part A
→ docs/modules/README.md
→ selected docs/modules/<semantic-name>/README.md Part A
→ docs/evidence/README.md
```

研究来源、法院背景、Build/Buy 或平台对比按需读取 `docs/research/`，不要插入第一次阅读主线。

实现 / Review：

```text
docs/architecture/reference.md
→ docs/architecture/README.md Part B
→ docs/modules/reference.md
→ selected docs/modules/<semantic-name>/README.md Part B / Part C
→ docs/decisions/
→ docs/evidence/
→ code / schema / migration / tests
```

项目事实或简历 Ownership 任务额外读取 `docs/project/reference.md` 和 `docs/governance/project-fact-provenance.md`。

## Human-facing Part A

Part A 的目标是让第一次接触 Zuno 的高级工程师能够连续理解：

```text
现实背景
→ 最简单方案
→ 简单方案已经能解决什么
→ 哪个具体场景使假设失效
→ 新的事实边界为什么出现
→ 正常流程
→ 典型故障与恢复
→ 替代方案与成本
→ 什么条件下删除复杂度
→ Current / Target / Unknown
```

不要从模块名、对象名、Framework 名或 Contract 列表开始。不要为了面试增加 FAQ。技术含量通过因果和失败窗口暴露，不通过术语数量暴露。

## Research-to-Engineering

始终保护：

```text
Research Artifact
!= Capability
!= Provider
!= Qualified Provider
!= Formal Business Fact
```

研究关系至少区分：

```text
DIRECT_LINEAGE
CAPABILITY_LINEAGE
CONCEPTUAL_LINEAGE
BACKGROUND_ONLY
UNVERIFIED
```

成熟平台已经提供的 Conversation、Workflow、MCP、Tool Calling、Checkpoint、Generic RAG、Generic Memory、Model SDK、Tracing、Generic Eval 等能力优先复用。Zuno 只在业务约束要求稳定法律语义、事实 Authority、资格、版本、正式准入、恢复或专业 Evaluation 时 Own 领域语义。

Native Runtime、GraphRAG、Reflection、Persistent Multi-Agent、独立服务等复杂机制均为 Measurement-gated；已经实现不代表应该永久保留。

## Architecture 不变量保护

文档整理不得偷偷改变现有 Target Architecture。若修改会新增/删除责任域、改变 Owner、Authority、Admission、Invalidation、Lifecycle、Security、Effect、Recovery 或跨模块 Contract，停止局部编辑并升级为 Architecture Revision / ADR。

当前应继续保护的高层语义包括：

- Domain durable facts 与 Runtime control/checkpoint 分离；
- Knowledge material/version/readiness 与检索结果分离；
- Candidate 与 Formal Business Fact 分离；
- Retry / Replan / Reconcile 分离；
- Unknown external outcome 不盲重试；
- 长任务受保护动作需要持续授权；
- Telemetry 不替代 Durable Audit / Business Truth；
- 跨 Store 默认无 2PC；
- Capability Provider 可替换且资格受 Evaluation 约束；
- 复杂机制继续通过 baseline / ablation / kill test 决定保留。

## Red / Blue

正式只保留两种模式：

```text
CHATGPT_AUTO
AGENT_AUTO
```

用户可以中途干预，但没有第三种人工候选执行模式。

启动 Red / Blue 前，Project / Architecture / 目标 Module Part A 必须先达到独立可读质量。Red 用业务场景、替代方案、故障窗口、Evidence 和 Ownership 施压；不要围绕内部名词做 trivia drill。Blue 保护项目目标，不保护当前架构，可以回答“简单方案已经足够”“应复用平台”“应删除该机制”“需要 Architecture Revision”或“证据不足”。

CHATGPT_AUTO 是同一对话中的程序性角色隔离；重大 Finding 不能因同一模型 Red/Blue 同意就成立。AGENT_AUTO 使用独立上下文，适合正式 Closed-book retest。

Red / Blue 长期方法和历史在 `docs/red-blue/`；机器运行协议与 active state 在 `.agent/red-blue/`。旧手工 Round 只在 `docs/red-blue/archive/legacy/` 复盘，不再是正式模式。

## 修改与验证

- 不扩大个人 Ownership，不把导师/团队成果写成个人成果。
- 不把 Pilot、Mock、Court-side Test、Benchmark 或 Runbook 写成 Production。
- 不覆盖用户已有未提交修改；提交前检查 base SHA 与 main 漂移。
- Documentation Migration 要同步更新导航、`.agent` 路由、validator 和链接，不保留永久平行入口。
- Validator 锁 Owner、Authority、Source Precedence、Current/Target 和必要入口，不锁自然语言标题或固定篇幅。
- 文档改动至少检查 entrypoints、内部链接、repo structure、Agent system、doc boundaries 和相关 focused tests。
- 不声称 `FULL CI PASSED`，除非完整 CI 确实执行并通过。

常用验证：

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

更多机器路由见 `.agent/system.yaml` 与 `.agent/references/`。