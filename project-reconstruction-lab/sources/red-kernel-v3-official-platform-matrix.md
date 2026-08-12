# RED-KERNEL-V3 官方竞品证据快照

access_date: 2026-08-12
evidence_class: PUBLIC_CONTEXT
source_rule: 只记录官方产品页、官方文档、官方 GitHub 与官方许可证；没有公开证据的字段保持 UNKNOWN。

## 分层结论

| 对象 | 产品层级 | 官方公开能力 | 尚未证明的边界 | V3 结论 |
|---|---|---|---|---|
| [Tencent WorkBuddy](https://www.workbuddy.cn/work/) | Complete / horizontal Agent Workspace | 专家角色、Skills、MCP 生态、自然语言任务执行；企业产品页另宣称模型、权限、审计、OpenAPI 与企业插件能力 | 面向 Zuno 的 Canonical Matter/Fact/Finding 状态契约、证据依赖失效、法律评测接口 UNKNOWN | 默认 Host 候选；不以公开资料证明其不足或不安全 |
| [Dify](https://dify.ai/) | Agent / Workflow App Platform | Workflow、RAG、Agent、工具、MCP/API 发布、模型接入、可观测与自托管/VPC 路径 | 法律领域状态与法律评测不是其公开的原生 Contract；仓库为带额外条件的 Apache 2.0 变体，商用部署须复核 | BUY/EXTEND 候选，不能直接当法律 Domain Owner |
| [Pi mono](https://github.com/badlogic/pi-mono) | Agent Harness / Toolkit | Agent core、tool calling、session/state、LLM API、coding agent、UI/Slack 扩展 | 企业租户、法律事实所有权、证据门控、HITL 审计与生产运维边界 UNKNOWN | 运行时/嵌入候选，不是完整产品竞品 |
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) | Agent Runtime Framework | durable execution、persistence/checkpoint、interrupt/resume、HITL、低层图编排 | 不负责 Zuno 的 Matter、Evidence、Finding 或法律正确性 | 可作为 Runtime Provider；不作为 Domain Model |
| [RAGFlow](https://github.com/infiniflow/ragflow) | Retrieval / Context / Agent Provider | 深度文档解析、chunking、多路召回/融合/rerank、引用、MCP/API；Apache 2.0 | 法律 Canonical State、Fact/Article 版本、人工决定与 Domain 依赖 UNKNOWN | Retrieval Provider 候选；Graph 仍须 Kill Test |

## 证据边界

- “官方页面宣称有能力”不等于 Zuno 已完成集成，也不等于满足法律场景的安全或质量要求。
- WorkBuddy 的公开能力足以使“Zuno 必须自建完整 Host/Runtime”成为未证伪前的失败假设；但公开资料没有证明它提供 Zuno 所需的法律 Canonical State Contract。
- Dify 仓库的 `LICENSE` 明确写出多租户和前端标识等额外条件，不能把“可见源码”直接转换成“无条件商用复用”。
- Pi 的官方仓库路径与公开搜索结果存在版本/组织信息不一致，具体发行包与许可证应在采用前锁定 commit 并复核；本矩阵不把 UNKNOWN 填成事实。
- 只有公开仓库明确带许可证的代码才进入可复用候选；论文、数据集、模型权重与代码分别审查，论文结果不能代替集成证据。
