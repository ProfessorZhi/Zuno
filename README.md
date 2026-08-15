# Zuno

Zuno 是一个来自智慧司法研发与工程化背景的法律智能 Agent 平台项目。当前仓库同时包含产品代码、架构设计、当前证据和项目恢复材料；这些来源的职责不同，不能互相倒推。

## 先读什么

如果你第一次接触项目，按下面顺序阅读：

1. [项目说明](./docs/project/README.md)
2. [项目背景](./docs/project/project-background.md)
3. [团队与开发分工](./docs/project/team-and-contributions.md)
4. [开发过程](./docs/project/development-process.md)
5. [总体架构](./docs/architecture/architecture.md)
6. [模块边界](./docs/modules/README.md)
7. [有效 ADR](./docs/decisions/README.md)
8. [当前证据](./docs/evidence/README.md)
9. [Red / Blue 审查历史](./docs/history/red-blue/README.md)（需要理解架构为什么这样演进时再读）
10. [术语表](./docs/terminology.md)

完整文档路由见 [docs/README.md](./docs/README.md)。

## 事实边界

项目背景、团队参与和开发过程来自用户回忆、公开研究背景和仍未恢复的历史事实；严格来源边界见[项目事实来源说明](./docs/governance/project-fact-provenance.md)。总体架构是 Target 设计；Evidence 只说明当前仓库、测试和可复现运行证据。不要把当前代码反写成历史个人贡献，也不要把 Target 说成 Production。

历史 Red / Blue 讨论保留在 [`docs/history/red-blue/`](./docs/history/red-blue/)，作为架构审查过程记录，不是当前架构或事实入口。正式接受的架构结果由维护者写入 `docs/architecture/` 或 `docs/decisions/`；普通一次性讨论和中间输出不进入仓库，Git history 仍是文件演进的考古来源。

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
