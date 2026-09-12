# 法律 AI 领域问题证据：Zuno Problem Statement 的外部研究背景

> status: research-reference
> last_verified: 2026-09-12
> canonical_truth: no
> current_implementation_evidence: not-implied

本文件记录法律 AI、法律 RAG 与司法智能系统在专业使用中反复出现的领域问题，用于约束 Zuno 的 Target Problem Statement。它不构成 Zuno 项目历史证据，也不证明当前代码已经解决这些问题。

外部研究能够说明某类风险具有普遍性；Zuno 历史上是否出现过同类故障、根因是什么、修复是否有效，仍需以 `docs/project/README.md`、`docs/governance/project-fact-provenance.md` 与 `docs/evidence/` 为准。

## 检索可靠性不能由“接入知识库”本身证明

Barnett 等人的 RAG 工程经验研究总结了检索、生成与来源关联等多类失败模式，并指出 RAG 的可靠性需要在运行过程中持续验证。对法律系统而言，“答案带有引用”仍然不足以证明所需材料已经被完整覆盖，也不能证明引用内容真正支持当前结论。

Reuter 等人在大规模法律数据集上进一步讨论了 Document-Level Retrieval Mismatch：大量结构相似的法律文档会使 Retriever 选中错误来源文档。法律检索因此需要同时保护文档身份、来源、版本与上下文，不能只依赖 chunk 相似度。

复杂法律与监管文档问答研究还报告了关键 chunk 漏召回、query drift、retrieval laziness 等问题。需要多轮补充证据的任务不能把一次 Top-K 返回结果视为完整材料边界。

**对 Zuno Target 的约束：** Knowledge 需要描述材料范围、版本、来源、加工完成度与任务级就绪；Retriever 只产生候选。一次 retrieval miss 不能自动升级为“全案不存在”。

## 模型输出的语言质量不能代替专业可靠性

法律场景研究持续讨论 hallucination、虚假案例或法条引用、不可解释输出与责任归属问题。RAG 可以降低一部分幻觉风险，却不会消除检索错误、模型误读、证据覆盖不足和无依据推断。

Van Duin 与 Rietveld 在民事司法场景中讨论了 hallucination、automation bias 与不可追溯结果，并强调严格使用条件、人工控制和 AI literacy。Contini 从司法技术与责任关系出发，指出 AI 的不透明和自主性会使最终责任更多落到实际使用者身上。

**对 Zuno Target 的约束：** 模型、检索和专业算法输出保持候选身份；进入长期工作成果以前，需要业务规则与必要的人审。系统保存的不应只有最终文本，还要保留来源、模型输出、人工修改与正式接纳依据。

## 法律依据的有效性具有时间、层级和适用范围

法律材料与先例存在时间有效性、层级、辖区、负面处理和任务范围等约束。语义相似度只能回答“文本是否相关”，不能单独回答“这个来源现在是否有资格支持当前结论”。

**对 Zuno Target 的约束：** 版本、新鲜度、专业资格与当前安全条件需要在适当边界重新判断。历史上曾经合法使用的材料、曾经成立的结果和当前仍可使用的结果是不同事实。

## 长期专业工作需要明确的人机责任链

司法 AI 文献普遍把 human oversight、accountability、transparency 和 auditability 视为高风险部署的重要条件。一个系统如果只能回答“模型最后生成了什么”，无法解释材料来源、人工修改、正式采用和后续失效，就无法形成稳定的专业责任链。

**对 Zuno Target 的约束：** 正式业务事实、运行控制、当前安全决定、外部现实动作和观测记录分别由明确责任方证明。Trace 能帮助诊断执行过程，但不能替业务系统或外部系统宣布事实已经成立。

## Agent 化进一步提高了评价与安全要求

Agent 系统会在多轮过程中动态调用工具、修改状态和改变后续上下文。Anthropic 2026 年的 Agent Evaluation 实践强调 transcript / trajectory 与最终 outcome 的区分，并建议结合代码、模型和人工 Grader；其 Context Engineering 工作则强调有限 attention budget、Just-in-Time retrieval 与结构化外部记忆。

多 Agent 研究系统表明，并行 Agent 对开放式、高价值、可分解研究任务能够带来收益，但同时显著增加 Token、协调与失败成本。最新法律 Agentic RAG 研究也说明，提供法律工具本身并不保证质量提升：收益取决于模型是否能有效规划并实际使用检索工具。

**对 Zuno Target 的约束：** Agentic Retrieval、Subagent、Reflection、长期 Memory 等机制都需要 Task Class 级 Eval、成本测量和退出条件。它们是可替换的执行策略，不应成为法律业务 Authority。

## 主要研究来源

- Scott Barnett, Stefanus Kurniawan, Srikanth Thudumu, Zach Brannelly, Mohamed Abdelrazek. *Seven Failure Points When Engineering a Retrieval Augmented Generation System*. 2024. DOI: `10.1145/3644815.3644945`.
- Markus Reuter et al. *Towards Reliable Retrieval in RAG Systems for Large Legal Datasets*. NLLP 2025. DOI: `10.18653/v1/2025.nllp-1.3`.
- Hui-feng Lin et al. *Fishing for Answers: Exploring One-shot vs. Iterative Retrieval Strategies for Retrieval Augmented Generation*. 2025 preprint. DOI: `10.48550/arxiv.2509.04820`.
- Anna van Duin, Rachel Rietveld. *Generatieve AI en de civiele rechter: op weg naar verantwoord gebruik?* 2025. DOI: `10.5553/tcr/092986492025033002002`.
- Francesco Contini. *Artificial Intelligence and the Transformation of Humans, Law and Technology Interactions in Judicial Proceedings*. 2020. DOI: `10.5204/LTHJ.V2I1.1478`.
- Anthropic. *How we built our multi-agent research system*. 2025.
- Anthropic. *Effective context engineering for AI agents*. 2025.
- Anthropic. *Demystifying evals for AI agents*. 2026.
- *Agentic RAG for Legal Question Answering in Civil Law: Evidence From the Korean Bar Examination*. IEEE Access, 2026.

这些材料用于说明领域约束与设计动因。任何关于 Zuno Current、历史质量问题或真实业务收益的结论，都必须由项目自身 Evidence 证明。
