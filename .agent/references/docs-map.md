# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

## Canonical 3 + 3

```text
# System Story
docs/project/                 History / project context / team and personal ownership
docs/architecture/            Overall Target Architecture
docs/modules/                 Target responsibility decomposition and module design

# Knowledge Control
docs/decisions/               accepted architectural rationale
docs/evidence/                Current code/test/trace/eval/runtime evidence
docs/governance/              provenance / owner / documentation / machine routing / validation
```

`docs/research/` 是上游参考，`docs/maintenance/` 是 Governance 的运行与历史附件，`docs/terminology.md` 是受 Governance 管理的术语表。它们保留兼容路径，但不拥有新的 canonical truth domain。

## Human route

```text
docs/README.md
→ docs/project/project.md
→ docs/architecture/architecture.md Part A
→ docs/modules/README.md
→ selected Module Part A
→ docs/evidence/README.md
```

这也是项目介绍和技术面试的默认主线。不要单独维护“面试版本”的第二套项目事实。

## Agent implementation route

```text
docs/architecture/reference.md
→ docs/architecture/architecture.md Part B
→ docs/modules/reference.md
→ selected Module Part B / Part C
→ docs/decisions/
→ docs/evidence/
→ code / schema / migration / tests
```

Project fact or resume-ownership task additionally reads `docs/project/reference.md` and `docs/governance/project-fact-provenance.md`.

## Canonical ownership

| Question | Owner |
| --- | --- |
| 项目为什么存在、怎样发展、团队与个人参与 | `docs/project/` |
| 当前目标系统为什么这样设计 | `docs/architecture/` |
| Target 怎样分解为具体责任与局部 Contract | `docs/modules/` |
| 为什么接受某个长期设计决定 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 文档、事实、Agent 路由怎样治理 | `docs/governance/` |
| 外部研究与平台资料 | `docs/research/`，仅上游依据 |
| Operations / Agent workflow / Red-Blue history | `docs/maintenance/`，治理附件 |

Module count is not a documentation invariant. Current numbered modules are the accepted Target decomposition until Architecture / ADR changes them.
