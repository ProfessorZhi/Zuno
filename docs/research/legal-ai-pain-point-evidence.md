# 法律 AI 痛点证据：Zuno Problem Statement 的外部研究背景

这份笔记只回答一个问题：法律 AI / RAG 系统在真实专业场景中反复遇到哪些问题，哪些问题足以支撑 Zuno 的 Target Problem Statement。

它不是 Zuno 的项目历史证据。论文能够证明某类风险在法律 AI / RAG 领域反复出现，不能证明 Zuno 历史上已经遇到、解决或量化了同一种问题。Zuno 自己的历史事实仍以 `docs/project/README.md`、`docs/governance/project-fact-provenance.md` 和 `docs/evidence/` 为准。

## 检索本身会错，RAG 不能把“接了知识库”当成可靠性证明

Barnett 等人在 RAG 工程经验研究中总结了检索、生成和源链接等多类失败点，并指出系统可靠性需要在运行中持续验证。对法律系统，这意味着“模型有引用”仍然需要继续追问：检索是否找到了正确材料、是否漏掉关键材料、引用是否真的支持结论。

Reuter 等人在大规模法律数据集上进一步观察到 Document-Level Retrieval Mismatch：大量结构相似的法律文档会让 Retriever 选中错误来源文档。法律检索因此不仅是 Top-K 和向量相似度问题，还要保护文档身份、来源和上下文。

Lin 等人研究复杂法律 / 监管文档问答时也报告了 Top-K 漏掉关键 chunk、query drift、retrieval laziness 等问题。复杂问题需要多轮补证时，一次检索结果不能被当作“证据已经完整”。

**对 Zuno Target 的含义：** Knowledge 需要描述材料范围、版本、来源、处理完成度和任务级就绪；Retriever 只产生候选。一次 retrieval miss 不能自动升级成“全案不存在”。

## 语言模型的流畅性不能承担法律事实责任

法律场景中的研究反复讨论 hallucination、虚假案例 / 法条引用、黑箱输出和不可追溯结论。RAG 可以降低部分幻觉，却不能消除 Retriever 错误、模型误读和无依据推断。

Van Duin 与 Rietveld 对民事司法中的生成式 AI 讨论了 hallucination、automation bias 和不可追溯结果，并强调严格使用条件、人工控制与 AI literacy。Contini 从司法技术与责任关系出发，指出 AI 的不透明和自主性会使责任更多落到使用者身上；这使“系统建议了什么”和“专业人员正式接受了什么”必须保持可区分。

**对 Zuno Target 的含义：** 模型、检索和专业算法输出保持候选身份；进入长期正式工作成果以前需要业务规则和必要人审。系统要保存当时的来源、模型输出、人类修改和最终接纳依据，而不是只保存最终文本。

## 法律有效性会随来源、时间和权限变化

法律材料与先例存在时间有效性、层级、辖区和负面处理等约束。单纯语义相似无法判断一个来源当前是否仍有资格支撑结论。另一方面，司法 AI 还面对敏感材料、数据外发、隐私和持续授权问题。

**对 Zuno Target 的含义：** 版本、新鲜度、当前安全条件和专业资格必须在受保护边界重新判断。历史上曾经合法使用的材料或曾经成立的结论，不自动证明现在仍可访问或仍然有效。

## 长期专业工作需要可追溯的人机责任链

司法 AI 文献普遍把 human oversight、accountability、transparency 和 auditability 视为高风险部署条件。真正需要解释的不是“模型能不能生成一段文本”，而是这段结果依据什么材料、经过谁的判断、哪些机器步骤只是建议、发生错误后由谁负责修正。

**对 Zuno Target 的含义：** 正式业务事实、运行控制、当前安全决定、外部现实动作和观测记录需要各自有明确责任来源。Trace 可以帮助诊断，但不能替业务或外部系统宣布事实已经成立。

## 研究来源

- Scott Barnett, Stefanus Kurniawan, Srikanth Thudumu, Zach Brannelly, Mohamed Abdelrazek. *Seven Failure Points When Engineering a Retrieval Augmented Generation System*. 2024. DOI: `10.1145/3644815.3644945`.
- Markus Reuter et al. *Towards Reliable Retrieval in RAG Systems for Large Legal Datasets*. NLLP 2025. DOI: `10.18653/v1/2025.nllp-1.3`.
- Hui-feng Lin et al. *Fishing for Answers: Exploring One-shot vs. Iterative Retrieval Strategies for Retrieval Augmented Generation*. 2025 preprint. DOI: `10.48550/arxiv.2509.04820`.
- Anna van Duin, Rachel Rietveld. *Generatieve AI en de civiele rechter: op weg naar verantwoord gebruik?* 2025. DOI: `10.5553/tcr/092986492025033002002`.
- Francesco Contini. *Artificial Intelligence and the Transformation of Humans, Law and Technology Interactions in Judicial Proceedings*. 2020. DOI: `10.5204/LTHJ.V2I1.1478`.

SciSpace 检索还返回了多篇关于司法 AI 的 bias、opacity、human oversight、due process、hallucinated citations 和 provenance logging 研究。这里优先保留能够直接支持 Zuno Problem Statement、且与当前 Target 边界最相关的文献；不把论文中的风险强行写成 Zuno 已验证的产品问题。
