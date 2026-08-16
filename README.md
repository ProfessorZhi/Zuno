# Zuno

Zuno 是一个来自智慧司法研发与工程化背景的法律智能 Agent 平台项目。当前仓库同时包含项目叙事、目标架构、模块设计、当前工程证据和架构审查历史；这些来源职责不同，不能互相倒推。

## 先读什么

第一次接触项目，建议只沿一条主线阅读：

1. [Project 主文档](./docs/project/project.md)：项目为什么存在、为什么值得做、为什么不只用通用平台、项目怎样发展、团队与个人参与以及项目级 Reviewer 追问。
2. [总体架构](./docs/architecture/architecture.md)：系统为什么按今天的责任边界和恢复语义设计。
3. [九模块设计](./docs/modules/README.md)：每个责任域内部怎样工作、失败和恢复。
4. [当前证据](./docs/evidence/README.md)：今天的代码、测试和运行到底证明到了什么程度。
5. [有效 ADR](./docs/decisions/README.md)：长期架构取舍。
6. [Red / Blue 审查历史](./docs/history/red-blue/README.md)：需要理解架构为什么这样演进时再读。
7. [术语表](./docs/terminology.md)。

完整文档路由见 [docs/README.md](./docs/README.md)。`docs/project/README.md` 只是 Project 的薄入口；项目级连续叙事集中在 `docs/project/project.md`。

## 事实边界

项目历史、团队参与和开发过程来自已确认回忆、公开研究背景和仍未恢复的历史材料；严格来源边界见[项目事实台账](./docs/governance/project-fact-provenance.md)。总体架构是 Target 设计；Evidence 只说明当前仓库、测试和可复现运行证据。不要把当前代码反写成历史个人贡献，也不要把 Target、Pilot 或 Mock Test 说成 Production。

历史 Red / Blue 讨论保留在 [`docs/history/red-blue/`](./docs/history/red-blue/)，作为架构审查过程记录，不是当前架构或事实入口。正式接受的架构结果由维护者写入 `docs/architecture/`、`docs/modules/` 或 `docs/decisions/`。

## 当前工程入口

- 后端代码：`src/backend/zuno/`
- 前端代码：`apps/web/`
- 数据库与迁移：`infra/db/`
- 当前运行和测试证据：[docs/evidence/](./docs/evidence/README.md)
- 运维 Runbook：[docs/operations/](./docs/operations/)

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
