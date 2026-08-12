# RED-KERNEL-V3 法律智能能力候选矩阵

access_date: 2026-08-12
evidence_class: PUBLIC_CONTEXT
commercial_reuse_rule: GitHub Public != Commercially Licensed；没有 LICENSE 的项目标记 LICENSE_UNKNOWN，不复制源码进入 Zuno。

| 能力/研究 | Primary source | 公开对象 | 论文/公开结果 | 官方代码 | 数据集/模型 | License / 商用复用 | 可进入 Zuno 的最小形态 |
|---|---|---|---|---|---|---|---|
| JIA 事件抽取、事件对齐/共指、冲突检测 | [arXiv:2303.16751](https://arxiv.org/abs/2303.16751) | 论文 | 中文离婚案件法官辅助场景的事件与争议检测研究 | 未在本轮 primary-source 路由中定位 | 数据与模型发布状态 UNKNOWN | LICENSE_UNKNOWN；不能直接复用论文实现 | `EVENT_EXTRACTION` / `EVENT_ALIGNMENT` / `CONFLICT_DETECTION` provider，输出 ConflictProposal |
| Fine-grained Fact–Article Correspondence | [arXiv:2104.10726](https://arxiv.org/abs/2104.10726) | 论文、标注对应关系数据描述 | 报告事实—法条细粒度匹配及下游 LJP 改善 | 官方代码 UNKNOWN | 标注数据发布与许可 UNKNOWN | LICENSE_UNKNOWN | `FACT_ARTICLE_MAPPING` provider，输出映射候选与引用 |
| Statute prediction correlation | [PMLR paper](https://proceedings.mlr.press/v101/feng19a/feng19a.pdf) | 论文 | 研究法条之间相关性用于法条预测 | 官方代码 UNKNOWN | 数据许可 UNKNOWN | LICENSE_UNKNOWN | `LEGAL_APPLICABILITY` 的可选策略，不视为已集成算法 |
| LawBench | [official GitHub](https://github.com/open-compass/LawBench) / [paper](https://arxiv.org/abs/2309.16289) | Benchmark、任务数据与评测说明 | 20 个任务、记忆/理解/应用三层；用于测法律知识与能力 | 官方仓库 | 数据在仓库/链接中分发，需按各来源说明复核 | 仓库 Apache-2.0；第三方/数据来源条款仍需逐项复核 | 法律模型与系统离线基准，不是 Domain Runtime 证据 |
| LJPCheck | [ACL Findings paper](https://aclanthology.org/2024.findings-acl.350/) | 功能测试方法与论文 | 面向法律判决预测的功能测试，含专家参与 | 官方代码/仓库 UNKNOWN | 测试生成与专家标注许可 UNKNOWN | LICENSE_UNKNOWN | 评测方法候选，不复制实现 |
| InternLM-Law | [official GitHub](https://github.com/InternLM/InternLM-Law) / [paper](https://arxiv.org/abs/2406.14887) | 模型仓库、推理说明与评测 | 仓库报告 LawBench 与长文本结果；这是项目自报结果 | 官方代码仓库 | `InternLM2-Law-7B` 权重链接公开；权重/数据条款仍需独立复核 | 仓库 LICENSE 为 Apache-2.0；模型权重与数据不可仅凭代码许可证判定 | 可作为 `MODEL` provider 候选；不能证明 Zuno 质量优势 |

## 进入正式架构前的限制

1. 论文结果是 PUBLIC_CONTEXT，不是 Zuno Current，也不是跨语料、跨任务的质量承诺。
2. Provider 只能返回 `Proposal`、`Candidate`、`Observation`、`Reference` 或 `Receipt`；不能直接写 `FactVersion`、`ConflictVersion` 或 `FindingVersion`。
3. 每个候选 provider 进入 Spike 前必须锁定 commit、模型/数据版本、输入输出 Contract、许可证、复现步骤与退出路径。

## 对 Zuno 架构的可用推断边界

上述研究共同支持的是 `PUBLIC_CONTEXT` 层面的设计启发：法律任务可以被拆成领域能力、
中间结构、功能行为和真实任务结果，而不应只用一个最终生成分数描述。它们不支持以下
更强结论：

- 论文系统已经集成到 Zuno；
- Zuno 当前质量优于 WorkBuddy、Dify 或其他 Host；
- Legal Domain State 已经证明能提升 Native Runtime；
- 研究报告中的指标可以直接迁移为 Zuno 指标；
- 公开仓库、论文代码或模型权重可以未经许可证复核进入商业产品。

因此本矩阵只支持两个下一步候选：

1. 把 Event、Fact–Article、Conflict、Evidence Retrieval 等登记为可替换
   `Legal Capability Contract` 的候选 Provider；
2. 把 L1–L5 评测结构和 A/B/C 对照登记为 Zuno Benchmark 设计输入。

Native Runtime 的必要性仍由 `H2 — Runtime–Domain Integration Advantage` 决定，
不能从研究背景直接升级为事实。
