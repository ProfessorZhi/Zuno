# Zuno

Zuno 是一个来自南京大学 LIPLAB 智慧司法研究与工程化背景的法律智能项目。当前仓库同时包含项目叙事、研究谱系、目标架构、模块设计、当前工程证据和维护/审查资料；这些来源职责不同，不能互相倒推。

## 先读什么

第一次接触项目，建议沿这条主线阅读：

1. [Project 主文档](./docs/project/project.md)：项目为什么存在、怎样发展、团队与个人参与、Current / Target / Unknown。
2. [Research Knowledge Base](./docs/research/README.md)：葛季栋/LIPLAB 的研究谱系、Research Artifact 怎样进入 Engineering Capability，以及 WorkBuddy / Dify / Coze / LangGraph 等通用平台已经解决什么。
3. [总体架构](./docs/architecture/architecture.md)：系统为什么按今天的责任边界和恢复语义设计。
4. [九模块设计](./docs/modules/README.md)：每个责任域内部怎样工作、失败和恢复。
5. [当前证据](./docs/evidence/README.md)：今天的代码、测试和运行到底证明到了什么程度。
6. [有效 ADR](./docs/decisions/README.md)：长期架构取舍。
7. [Maintenance](./docs/maintenance/README.md)：运维、Agent/GitHub 工作流和 Red / Blue 历史。
8. [术语表](./docs/terminology.md)。

完整文档路由见 [docs/README.md](./docs/README.md)。

## 八个一级文档域

```text
理解 Zuno：
project → research → architecture → modules

治理和维护 Zuno：
decisions | evidence | governance | maintenance
```

这不是流水线。`research/` 是研究依据，不拥有 Project/Architecture Truth；`maintenance/` 是维护流程和历史，不拥有 Current Evidence。

## 事实边界

项目历史、团队参与和开发过程必须回到[项目事实台账](./docs/governance/project-fact-provenance.md)。总体架构是 Target 设计；Evidence 只说明当前仓库、测试和可复现运行证据。不要把当前代码反写成历史个人贡献，也不要把 Target、Pilot 或 Mock Test 说成 Production。

研究资料同样不能越权：论文提出不等于 Zuno 已实现，导师/课题组成果不等于个人实现，平台 Feature 也不能反向制造 Zuno 需求。研究关系和平台基线见 [`docs/research/`](./docs/research/README.md)。

历史 Red / Blue 讨论保留在 [`docs/maintenance/history/red-blue/`](./docs/maintenance/history/red-blue/)，作为架构审查过程记录，不是当前架构或事实入口。正式接受的结果由维护者写入 `docs/architecture/`、`docs/modules/` 或 `docs/decisions/`。

## 当前工程入口

- 后端代码：`src/backend/zuno/`
- 前端代码：`apps/web/`
- 数据库与迁移：`infra/db/`
- 当前运行和测试证据：[docs/evidence/](./docs/evidence/README.md)
- 运维 Runbook：[docs/maintenance/operations/](./docs/maintenance/operations/)
- 人类可读 Agent/GitHub 工作流：[docs/maintenance/agent-workflow/](./docs/maintenance/agent-workflow/README.md)

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

修改业务代码前请阅读根目录 [AGENTS.md](./AGENTS.md)。
