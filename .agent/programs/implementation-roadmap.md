# Zuno Architecture Surface Cleanup V1 执行计划

Program ID：`zuno-architecture-surface-cleanup-v1`

## 目标

在目标运行时第一轮 slice 已经形成之后，把 Zuno 从“能力很多”收口成“封面清楚、目录清楚、文档清楚、本地 Agent Skill System 清楚”的成熟项目外形。

本目录就是当前执行计划包。所有 phase 文件平铺在 `.agent/programs/`，不再嵌套到 program 子目录。每次新 program 都从 `PHASE01` 开始编号；旧 program 的 active phase 文件从当前前台移除，证据放入 `docs/history/programs/`。

## 边界

- Current：代码和测试已经证明的当前事实。
- Foundation：已有最小可调用切片，但产品行为还不成熟。
- Target：下一阶段要实现的架构。
- Future：本程序之外的未来方向。
- History：已经归档的证据和被替换计划。

## 当前判断

Zuno 当前最重要的目标不是继续堆 feature，而是成熟项目封面化：

```text
README 一眼懂项目
docs 一眼懂 Current / Target / Roadmap
src 一眼懂 API / Agent / Memory / Capability / Knowledge / Platform
.agent 一眼懂本地 Agent Skill System
tools 一眼懂怎么维护
tests 一眼懂怎么防回归
```

旧目标运行时 V2 的执行证据保留在：

```text
docs/history/programs/zuno-target-runtime-v2/
```

## 执行 Phase

1. [PHASE01：公开封面与架构叙事收口](PHASE01_public-architecture-surface.md)
2. [PHASE02：本地 Agent Skill System 收口](PHASE02_local-agent-skill-system.md)
3. [PHASE03：tools / tests 工作流防回归](PHASE03_tools-tests-guardrails.md)
4. [PHASE04：后端六层 facade 分层](PHASE04_backend-facade-layers.md)
5. [PHASE05：大文件轻拆](PHASE05_large-file-light-split.md)
6. [PHASE06：架构图与 HTML 展示页](PHASE06_architecture-diagrams-html.md)

## 停止条件

- 不要跳过 phase。
- 不要在未授权 phase 修改 runtime、frontend、Docker、DB、eval runner 或依赖。
- 不要恢复 root `domain-packs/`、Domain Pack frontend pages 或旧 DomainQAGraph。
- 不要在代码和测试证明前把 Target 写成 Current。
- 不要把 `.agent/references/` 当普通索引继续膨胀；它是本地项目 skill / lesson / playbook。
- 如果执行计划被替换，旧 phase 文件从 `.agent/programs/` 当前前台移除；需要保留的证据归档到 `docs/history/programs/`。

## 参考

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- `.agent/system.yaml`
- [closure-checklist.md](closure-checklist.md)
