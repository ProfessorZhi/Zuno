# Zuno 文档地图

本文只导航，不拥有 Project、Architecture、Module 或 Current 语义。

## 八个一级目录

```text
# System & Review
docs/project/                 project history / context / team & personal ownership
docs/architecture/            overall Target Architecture
docs/modules/                 Target responsibility decomposition
docs/red-blue/                adversarial review method + archived rounds

# Trust & Evolution
docs/research/                upstream research / algorithms / court background / platform baseline
docs/decisions/               accepted architectural rationale
docs/evidence/                Current code/test/trace/eval/runtime evidence
docs/governance/              provenance / owner / documentation / workflow / operations / validation
```

`docs/red-blue/` 和 `docs/research/` 对自己的评审/研究材料是 canonical location，但不能覆盖 Project、Architecture、Modules 或 Evidence 的事实 Authority。

## Human route

```text
docs/README.md
→ docs/project/README.md
→ docs/architecture/README.md
→ docs/modules/README.md
→ docs/modules/<semantic-name>/README.md
→ docs/evidence/README.md
```

Research 按需进入，不作为第一次阅读固定中转。Red / Blue 在正文已经独立可读后才运行。

## Agent implementation route

```text
docs/architecture/reference.md
→ docs/modules/reference.md
→ docs/modules/<semantic-name>/reference.md
→ relevant neighboring module reference.md
→ docs/decisions/
→ docs/evidence/
→ code / schema / migration / tests
```

需要理解“为什么存在”时，从 reference 回到同目录 README；不要从 README 猜字段、状态或 Current。

当前语义模块目录：

```text
application/      01 Application & Integration
domain/           02 Legal Domain & Work Product
knowledge/        03 Knowledge & Evidence
runtime/          04 Agent Runtime & Control
capability/       05 Capability & Skill
effects/          06 Tool Runtime & Effects
model-gateway/    07 Model Gateway
security/         08 Security & Governance
evaluation/       09 Observability & Evaluation
```

每个目录：

```text
README.md      Human Narrative
reference.md   Part B Engineering Reference + Part C Cross-Module Consistency
```

编号仍属于当前 Target decomposition；目录名表达责任语义，不把顺序冻结进文件系统。

Project fact / resume ownership 任务额外读取 `docs/project/reference.md` 与 `docs/governance/project-fact-provenance.md`。

## Ownership map

| Question | Owner / source |
| --- | --- |
| 项目为什么存在、怎样发展、团队与个人参与 | `docs/project/` |
| 当前 Target 为什么这样设计 | `docs/architecture/` |
| Target 怎样分解为具体责任与局部 Contract | `docs/modules/` |
| Red / Blue 方法、Transcript、Findings、旧 Round | `docs/red-blue/`，non-authoritative for system truth |
| 外部研究、算法、天津法院/LIPLAB 背景、平台 baseline | `docs/research/`，upstream only |
| 为什么接受某个长期设计决定 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| provenance、术语、Agent workflow、Operations、validation | `docs/governance/` |

Current target module count can change only through Architecture Revision / ADR; module count is not a documentation invariant.