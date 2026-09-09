# Zuno

Zuno 是一个来自南京大学 LIPLAB 智慧司法研究与工程化背景的法律智能项目。仓库同时保存项目历史、研究来源、Target Architecture、模块设计、当前工程证据和对抗性审查材料；这些来源职责不同，不能互相倒推。

## 第一次阅读

第一次接触 Zuno，沿一条主线即可：

1. [Project](./docs/project/project.md) — 项目为什么出现、真实演进、团队与个人参与；
2. [Architecture](./docs/architecture/architecture.md) Part A — 从简单方案开始，看哪些真实约束逼出新的事实边界；
3. [Modules](./docs/modules/README.md) — 总体设计怎样分解为局部责任、正常流程和故障恢复；
4. [Evidence](./docs/evidence/README.md) — 今天的代码、测试和运行实际证明了什么。

研究来源按需进入 [Research](./docs/research/README.md)。正文达到独立可读质量以后，再用 [Red / Blue](./docs/red-blue/README.md) 做场景驱动的架构与面试压力测试。

完整文档路由见 [docs/README.md](./docs/README.md)。

## 八个一级文档域

```text
System & Review
project      真实项目背景、历史、团队与个人参与
architecture 理想总体 Target Architecture
modules      Target 责任分解与模块设计
red-blue     对抗性评审方法与 Round 归档

Trust & Evolution
research     论文、算法、法院背景、通用平台 baseline
decisions    长期接受的架构理由
evidence     Current code/test/trace/eval/runtime evidence
governance   provenance、ownership、writing、terminology、workflow、operations、validation
```

`research/` 和 `red-blue/` 对自己的材料有固定归档位置，但不拥有 Project、Target Architecture 或 Current Evidence。

## 事实边界

项目历史、团队参与和个人 Ownership 回到[项目事实台账](./docs/governance/project-fact-provenance.md)。总体架构是 Target；Evidence 只说明当前仓库、测试和可复现运行。Pilot、Mock、Court-side Test 和 Runbook 都不能自动升级成 Production。

论文提出不等于 Zuno 已实现，导师/课题组成果不等于个人实现，Framework Feature 不等于 Zuno 自研。成熟 Agent Platform 已经提供的通用能力优先复用；Zuno 只在法律业务需要稳定专业语义、版本、资格、正式业务事实、恢复或专业 Evaluation 时 Own 领域语义。

历史 Red / Blue 手工轮次保留在 [`docs/red-blue/archive/legacy/`](./docs/red-blue/archive/legacy/)，只用于复盘，不是当前 Architecture Truth 或面试标准答案。

## 当前工程入口

- 后端代码：`src/backend/zuno/`
- 前端代码：`apps/web/`
- 数据库与迁移：`infra/db/`
- 当前运行和测试证据：[docs/evidence/](./docs/evidence/README.md)
- 运维 Runbook：[docs/governance/operations/](./docs/governance/operations/)
- Agent/GitHub 协作规则：[docs/governance/workflows/agent-workflow.md](./docs/governance/workflows/agent-workflow.md)
- 跨文档术语：[docs/governance/terminology.md](./docs/governance/terminology.md)

常用验证：

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_architecture_document_set.py -p no:cacheprovider
```

架构图需要更新时，先修改 `docs/architecture/architecture.md` 与图源，再运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

修改业务代码前请阅读 [AGENTS.md](./AGENTS.md)。