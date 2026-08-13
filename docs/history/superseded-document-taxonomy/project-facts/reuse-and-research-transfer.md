# Reuse and Research Transfer

status: canonical-history
canonical_question: 哪些能力是复用、扩展、自建或研究成果转化？
owner: Project Facts / Technology Provenance
replaces: 无；从 `technology-reality.md` 拆出来源与 Ownership 边界

## 分类规则

```text
REUSE              直接使用外部软件、服务或基础设施
EXTEND             在外部能力之上增加 Adapter、配置或项目代码
BUILD              项目自身定义的业务 Contract、策略或实现
RESEARCH TRANSFER  研究论文/算法/数据方法转化为项目候选能力
UNKNOWN            尚无足够证据分类
```

分类不能替代历史状态；每一行仍需标记事实标签、Evidence ID 和 Strength。

## 当前技术来源矩阵

| 对象 | 分类候选 | 历史状态 | Evidence | Strength | 不能推出 |
|---|---|---|---|---|---|
| OpenViking | `REUSE / EXTEND` | `[USER_CONFIRMED]`：用户参与 Memory/Context 接入 | E-USER-004 | E1 | 不证明当前仓库仍使用、用户拥有整个 Memory 或它处于生产关键路径 |
| LangGraph | `REUSE / EXTEND` | `[USER_CONFIRMED]`：用户学习并参与 Agent；具体使用范围 UNKNOWN | E-USER-004 | E1 | 不证明完整 Runtime 主链路或用户实现框架 |
| PostgreSQL / Docker / 其他中间件 | `REUSE` 候选 | `[UNKNOWN]` 历史使用 | E-REPO-001/002 仅为当前仓库表面 | E3（当前仓库） | 不证明历史项目使用 |
| Tool Calling Strategy | `BUILD` 候选 | `[USER_CONFIRMED]`：参与相关开发 | E-USER-004 | E1 | 不证明具体策略、代码位置或效果 |
| Legal Domain Model | `BUILD` / `TARGET_ONLY` 候选 | `[TARGET_ONLY]` | 当前架构 ADR | E3/E5 仅限当前文档/实现范围 | 不证明历史产品已有正式 Domain Kernel |
| 葛季栋团队法律研究 | `RESEARCH TRANSFER` 候选 | `[PUBLIC_CONTEXT]` | E-PUBLIC-002 | E4 | 不证明论文算法已集成到 Zuno 或可直接商用复用 |
| 法院 QA / Eval | `PROJECT OWNED` 候选 | `[UNKNOWN]` | 待历史 Artifact / 用户确认 | E0 | 不证明已经存在版本化数据集或 Gold Evidence |

## Reuse First 边界

通用基础设施优先复用；项目自身必须拥有法律业务 Contract、证据语义、权限/版本/审核、
项目 QA 和工具调用策略的真实边界，前提是这些历史或 Target Claim 各自有证据。不能用
“自研”提升产品价值，也不能用“开源”自动否定领域差异。

## 研究转化规则

研究论文、官方代码、模型或数据集进入项目前，必须单独核验：

```text
Paper / Repo / Dataset
 → license and commercial scope
 → pinned version
 → input/output Contract
 → reproduction / benchmark
 → adapter or provider boundary
 → rollback / replacement path
```

研究成果只能作为 `Capability Provider` 或 Eval 设计输入，不能直接写入 Canonical Domain
State。详细公开能力矩阵见 [`../../../project-reconstruction-lab/sources/legal-ai-capability-matrix.md`](../../../project-reconstruction-lab/sources/legal-ai-capability-matrix.md)。

## Owner 边界

本文件负责历史技术来源与研究转化边界；当前技术事实进入 [`technology-reality.md`](technology-reality.md)，
正式 Adopt/Extend/Build/Defer 决策进入 [`../../../project-reconstruction-lab/05-red-blue/`](../../../project-reconstruction-lab/05-red-blue/README.md)
和 ADR。
