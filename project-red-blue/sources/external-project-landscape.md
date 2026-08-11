# 外部项目与产品环境

本文件只保存待研究对象和比较问题，不保存未经核验的市场排名、用户量或竞品结论。

## 待比较对象

WorkBuddy、Dify、RAGFlow、OpenViking、Mem0、Graphiti、Cognee、Microsoft GraphRAG、LightRAG、LlamaIndex、Onyx、Coze Studio、MaxKB、Docling、MinerU。

本轮 Build-vs-Buy 评审优先关注六类能力：

1. 文档解析、结构理解和摄取流水线；
2. 受控证据检索、重排和条件式 Graph Retrieval；
3. Memory Engine 与 Zuno Memory Governance 的分界；
4. Agent Runtime 与 Zuno Plan / Run / Proposal 语义的分界；
5. 企业连接器、权限同步和索引生命周期；
6. 完整 Agent/RAG 平台作为 Fork 基座的反事实成本。

## 比较维度

产品场景、部署方式、数据权限、租户隔离、工具和 MCP、记忆模型、检索能力、版本与迁移、可观测性、失败恢复、许可证、运维成本以及与 Zuno 当前问题的 Delta。

## 官方证据快照

下表只记录“为什么值得进入评审”，不代表已经通过五道 Gate，也不代表 Zuno 已经决定采用：

| 候选 | 官方材料当前可确认的能力 | 进入 Zuno 评审的原因 | 当前结论 |
|---|---|---|---|
| LangGraph | 面向长运行、有状态 Agent 的低层编排，包含持久化、恢复和 Human-in-the-loop 能力 | 适合作为 Agent Runtime Provider，但不能替代 Zuno 的 Domain Contract | `ADOPT_CANDIDATE` |
| RAGFlow | 文档解析、可编排摄取、混合检索、重排、Agent/MCP 和数据源同步能力 | 适合作为 Ingestion/Retrieval Provider 进行 Contract Fit 和 SourceSpan Spike | `TO_REVIEW` |
| OpenViking | 统一管理 Memory、Resource、Skill，支持分层上下文、递归检索和 Session 提取 | 适合作为 Memory Engine 候选，必须验证治理、权限、版本和 Provenance 接口 | `TO_REVIEW` |
| Onyx | 企业连接器、索引任务、权限同步和多种部署形态 | 适合作为 Connector Provider 候选，必须区分 CE/EE 能力与权限同步边界 | `TO_REVIEW` |
| Microsoft GraphRAG | Basic、Local、Global、DRIFT 等不同检索模式 | 支持“Graph 是条件能力而非默认路径”的验证假设 | `TO_REVIEW` |
| Coze Studio | Agent、Workflow、Knowledge、Plugin、API/SDK 和二次开发能力 | 作为完整平台 Fork 基座做 Modification Surface 反事实比较 | `TO_REVIEW` |
| MaxKB / Dify | 完整 Agent/RAG 产品化能力 | 作为“整个平台基座”方案的对照组，而非先验排除 | `TO_REVIEW` |

本轮来源：

- [LangGraph 官方概览](https://docs.langchain.com/oss/python/langgraph/overview)
- [RAGFlow 官方仓库](https://github.com/infiniflow/ragflow)
- [OpenViking 官方仓库](https://github.com/volcengine/OpenViking/) 与 [Memory API](https://docs.openviking.ai/en/api/16-memory)
- [Onyx Connector 官方文档](https://docs.onyx.app/admins/connectors/overview) 与 [官方仓库](https://github.com/onyx-dot-app/onyx)
- [Microsoft GraphRAG 官方查询模式](https://github.com/microsoft/graphrag/blob/main/docs/index.md)
- [Coze Studio 官方仓库](https://github.com/coze-dev/coze-studio)
- [MaxKB 官方仓库](https://github.com/1Panel-dev/MaxKB)

以上快照按 2026-08-11 访问时的官方材料整理；外部项目会持续变化，正式决策必须记录访问日期、版本/Commit 和可复现 Spike。

## 研究规则

版本、协议、部署、许可证和安全能力必须以当前官方文档或可复现测试为准。研究结果只能形成 `[REPO_EVIDENCE]` 或 `[BLUE_PROPOSAL]`，不能直接写成 Zuno 的历史事实。

每个候选必须同时记录：

- Capability Fit：能否完成明确任务；
- Contract Fit：能否输出 Zuno 所需的版本、证据、权限、状态和审计信息；
- Modification Surface：是否会穿透 Domain、Runtime、Persistence、Security、Failure/Effect 和 Operations；
- Operational / License Fit：部署、许可证、数据出口、升级和团队维护成本；
- Evidence：固定数据、失败样例、延迟、成本、质量和维护 Spike。

禁止用“开源项目不够企业级”“我们领域特殊”或“功能很多所以一定可复用”替代上述证据。若只完成资料阅读，结论必须保持 `TO_REVIEW` 或 `UNKNOWN`。
