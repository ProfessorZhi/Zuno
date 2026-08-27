# Zuno Research Knowledge Base

`docs/research/` 保存**经过来源核验的研究背景、Research-to-Engineering 推导、外部平台能力基线和文档叙事研究**。

它回答：

> Zuno 从哪些研究问题与外部技术事实出发？这些材料怎样帮助我们理解项目和架构？

它**不是**第四套 Zuno Architecture Truth。

## Canonical boundary

Research 可以解释、挑战或支持 Zuno 的 Project / Architecture，但不能覆盖它们：

```text
判断 Zuno Current:
Code / Test / Runtime Evidence
> Canonical Docs
> ADR
> Research / History / External Material
> Speculation
```

- 项目真实历史、团队与个人 Ownership：`docs/project/`
- 总体 Target Architecture：`docs/architecture/`
- 九个责任域设计：`docs/modules/`
- 当前实现/运行证明：`docs/evidence/`
- 长期接受的架构决策：`docs/decisions/`
- 来源、表述和文档规则：`docs/governance/`

研究结论只有在完成独立的 Project / Architecture / Module / ADR 修改后，才成为对应 canonical 文档的一部分。

## 目录

- [`deep-research-report-2026-08-27.md`](./deep-research-report-2026-08-27.md)：本轮“葛季栋/LIPLAB → Research Artifact → Engineering Capability → Zuno → 通用 Agent 平台边界 → Documentation”研究快照。
- [`jidong-ge-liplab-lineage.md`](./jidong-ge-liplab-lineage.md)：导师/课题组研究谱系、身份消歧规则和 lineage 分类。
- [`research-to-engineering-traceability.md`](./research-to-engineering-traceability.md)：Research Artifact 如何转化为 Engineering Capability，以及与 Zuno 责任域的关系。
- [`agent-platform-baseline.md`](./agent-platform-baseline.md)：WorkBuddy / Dify / Coze / LangGraph 等通用平台的能力边界与 Build / Buy / Extend 基线。
- [`documentation-narrative-blueprint.md`](./documentation-narrative-blueprint.md)：Project / Architecture / Module Part A 的故事化重写蓝图与 Interview Extractability 原则。

## Research relation taxonomy

论文、项目和研究成果与 Zuno 的关系必须显式区分：

- `DIRECT_LINEAGE`：有证据证明研究项目/问题直接构成 Zuno 的项目来源或业务背景。
- `CAPABILITY_LINEAGE`：研究成果形成可被工程化的专业能力来源，但不证明当前实现已经集成。
- `CONCEPTUAL_LINEAGE`：研究问题影响设计思想；不能声称代码直接源自该论文。
- `BACKGROUND_ONLY`：仅说明课题组背景，不应进入 Zuno 架构因果链。
- `UNVERIFIED`：身份、论文归属或与 Zuno 的关系尚未可靠确认。

`Paper != Capability != Provider != Qualified Provider != Formal Business Fact`。

## 时间敏感信息

外部 Agent 平台、模型、Framework、价格、协议和云产品能力会快速变化。平台比较必须记录 `last_verified`，过期以后先重新核验官方文档，再继续用作 Build / Buy 决策依据。

## 写作原则

研究材料进入 Human-first 文档时遵循：

1. 先真实问题，后研究成果；
2. 先可行 baseline，后差异化；
3. 先解释平台已经解决什么，再解释 Zuno 必须 Own 什么；
4. 先概念和失败场景，后内部术语；
5. 导师/课题组/团队/个人 Ownership 严格分开；
6. 未被 Evidence 证明的优势继续写成 Hypothesis / Target / Measurement Needed。
