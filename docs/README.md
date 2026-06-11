# Documentation Index

`docs/` 是给人看的正式文档入口，不放本地 Agent 工作流材料。

## Sections

- [architecture/](./architecture/README.md)
  - 当前主架构、分阶段计划、决策记录、RAG / GraphRAG / Domain Pack 设计
- [development/](./development/)
  - 环境搭建、开发说明、分层架构开发规则、迁移、运行手册、GitHub 发布边界
- [reference/](./reference/)
  - 面向读者的稳定参考资料
- [prototypes/](./prototypes/)
  - 原型和实验性材料
- [assets/](./assets/)
  - 文档配图和资源文件

## Reading Order

如果你第一次进入项目，建议按这个顺序读：

1. [README.md](../README.md)
2. [docs/architecture/README.md](./architecture/README.md)
3. [docs/development/public-demo-evidence.md](./development/public-demo-evidence.md)
4. [docs/development/public-demo-runbook.md](./development/public-demo-runbook.md)
5. [docs/development/public-demo-acceptance.md](./development/public-demo-acceptance.md)
6. [infra/docker/README.md](../infra/docker/README.md)
7. [tools/launchers/windows/README.md](../tools/launchers/windows/README.md)

Maintainer entrypoints:

- [docs/development/README.md](./development/README.md)
- [docs/development/github-publish-boundary.md](./development/github-publish-boundary.md)

## Notes

- First-time readers should stop after step 7.

- 当前主入口以 `docs/architecture/` 为准。
- 如果你是第一次读项目，优先走上面的 `Reading Order`，不要先跳进发布分组、staging 计划或本地工作流材料。
- 本地 Agent 工作流入口在仓库根目录的 `.agentmd` 和 `.agent/`，不会作为公开文档的一部分提交到 GitHub。
- 历史 handoff / workflow 材料属于本地内容，不属于公开文档入口。
