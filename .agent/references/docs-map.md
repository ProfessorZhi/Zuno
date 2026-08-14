# Zuno 文档地图

本文只提供导航，不拥有架构或事实语义。项目文档按 Owner 和问题分层；不要把目录结构当成
服务、模块或团队的一一映射。

## 正式层

```text
docs/facts/           项目背景、需求、开发、团队、交付和技术现实
docs/evidence/        当前代码、测试、运行和评测证据
docs/architecture/    总体 Target Architecture 四文件
docs/modules/         当前仅有边界 README，模块设计尚未冻结
docs/decisions/       ADR
docs/governance/      Owner、写作和工程治理
docs/history/red-blue/不可变 Red/Blue Round 归档
```

## 阅读路径

```text
项目现实：facts/README → project-background → requirements-and-workflows
          → development-and-evolution → team-and-ownership
架构：    facts/ → evidence/ → architecture/ → decisions/governance
当前实现：evidence/ → 代码、Migration、测试和可复现运行材料
历史攻防：history/red-blue/（按需；不默认遍历）
```

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目从哪里来、需求和开发如何恢复 | `docs/facts/` |
| 当前仓库和交付状态被什么证明 | `docs/evidence/` |
| Target 为什么这样设计 | `docs/architecture/architecture.md` |
| 图形如何展示 | `docs/architecture/architecture-views.md` + `architecture.html` |
| 长期设计决策 | `docs/decisions/` |
| Red/Blue 历史过程 | `docs/history/red-blue/` |
| Agent 导航和执行规则 | `.agent/` |

历史删除的 interview QA、旧专题和 11 模块原稿不再是 active route；需要考古时使用 Git history。
