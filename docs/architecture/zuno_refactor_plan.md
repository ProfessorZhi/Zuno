# Zuno 改造方案：LangGraph + GraphRAG 深度融合与 Domain Pack 平台化

> 目标：把 Zuno 从“能跑的个人 Agent 工作台”升级为“可搭建特定领域 Agent 的本地优先 Agent 工作台”。
>
> 本阶段重点不是多 Agent，也不是先做包名重构，而是先把 **LangGraph 工作流、GraphRAG、Domain Pack、低成本自动化测试、可扩展架构边界** 做扎实，最后再完成 `agentchat -> zuno` 的收口。

---

## 0. 先说结论

这次改造应该坚持四个原则：

1. 不推倒重写，在现有 Zuno 上做架构收束。
2. 不先做包名重构，先做能验证价值的核心闭环。
3. 不把合同审查做成孤立功能，而是做成第一个高质量 Domain Pack。
4. 不为了“看起来更大”而平行造两套 runtime，而是在现有 LangGraph、RAG、GraphRAG、eval 资产上继续深化。

一句话概括这版改造：

```text
先做一个可评估、可复用、低成本开发的 Domain Pack 架构，
再让 LangGraph + GraphRAG 成为 Zuno 的真正中枢能力，
最后再完成包名与目录层面的统一收口。
```

## 0.1 阶段目标总括

### Current Execution Status

This high-level plan describes the long-running target architecture. For the current serial execution status, treat the summary below as authoritative:

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: completed
- `Phase 5`: completed
- `Phase 6`: completed
- Current serial focus: `Phase 7`

为了避免“总方案”只讲终局，不讲阶段边界，这里先把当前阶段目标说清楚：

### 当前

当前最重要的是把 Zuno 从“功能能跑”推进到“主线架构成立”：

- 用 LangGraph 立住运行时主线
- 用 RAG / GraphRAG / BM25 立住知识能力主线
- 用 Domain Pack 立住领域扩展主线
- 用评测、trace、citation、成本控制立住验证主线

### 下一步

下一步重点不是继续散点加功能，而是补足治理层和系统边界：

- Retrieval Orchestrator 的控制面继续收紧
- profile / planner / RetrievalPlan / fallback / citation / scope 等语义继续明确
- 文档系统、目录系统、README、公开展示面继续收口

### 面试前必须做到

面试前，这个项目至少要达到：

- 架构层清晰
- 可扩展、可修改
- 不把关键能力写死
- LangGraph 不是装饰，而是核心运行时
- RAG / GraphRAG 主线完整且可评测
- 合同审查领域示范真实成立

### 面试后继续优化

面试后再继续推进：

- 更完整的多 Agent 体系
- 更严格的企业级检索治理
- 微服务 / 云原生演进
- 异语言后端接入
- 更强的代码工作台能力

### 当前仍未解决的关键问题

截至当前，主线已经比早期清楚很多，但下面这些问题还没有完全解决：

1. LangGraph 已经从方向性能力变成主运行时主线，但后续还要继续把评测、可观测性和更广的公开演示链路固化下来。
2. GraphRAG 已经拿到动态更新、图检索和合同审查场景的最小闭门证据，但版本治理和更稳定的价值证明还需要继续补强。
3. 检索控制面已经成形，普通模式 / 增强模式两档体验也已有最小稳定证据；下一步重点转向评测治理，而不是继续讨论体验口径本身。
4. 自动化评测已经有本地入口，但还需要继续强化成面试前可稳定展示的证据链。
5. 运行时收口与可运行恢复、项目结构治理、公开展示面收口、分层边界强化、LangGraph + GraphRAG 主线深化以及评测证据链固化都已有最小验收结果；当前串行主线应进入 `Phase 7`，继续做面试前总收口。
6. 目录结构和公开展示面已经明显改善，但还需要继续压掉混乱入口和历史痕迹。
7. 项目结构仍处在 `src/backend + src/frontend + apps/desktop` 的混合语义阶段；这不是错，但还没有完全达到面试前最好讲、最好维护的清晰结构。

这意味着：

```text
旧阶段里的很多能力已经出现，
但新的执行体系下，
当前更稳妥的口径仍然是：
确认 `Phase 1-4` 验收结果稳定，
再线性推进 `Phase 5-7`。
```

### 后续阶段划分

为了避免把“运行时收口”“项目结构治理”“文档展示面”“分层边界”“能力深化”“价值证明”“面试前收口”混成一团，后续阶段明确拆成新的七段：

1. `Phase 1`
   先完成运行时收口与可运行恢复，重点是把当前尾巴收完，尤其是原来最难的 rename / bridge / contract / runtime 入口问题，并先让 `zuno` 稳定跑起来
2. `Phase 2`
   单独进行项目文件夹与结构治理，把应用入口、核心能力、评测、文档、工具、基础设施、测试边界收清楚
3. `Phase 3`
   单独进行文档与展示面收口，把 README、架构文档、开发文档、发布边界和 GitHub 展示面统一起来
4. `Phase 4`
   强化分层架构与运行时边界，让控制层 / 服务层 / DAO 层 / 基础设施层和 runtime contract 真正收硬
5. `Phase 5`
   深化 LangGraph / RAG / GraphRAG / Domain Pack / 动态更新 / 两档检索体验这条实现主线
6. `Phase 6`
   固化本地 embedding、本地评测、五项指标、自动化测试、trace、citation、grounding 这条证据链
7. `Phase 7`
   做面试前总收口，对齐代码、目录、文档、评测、展示面和讲解口径

这个拆法的核心目的不是多造阶段名，而是：

```text
先收运行时命名与桥接，
再收项目结构，
再收文档展示面，
再收硬分层边界，
再深化实现主线，
再固化证据链，
最后做面试前总收口。
```

这样风险最低，也最容易形成清晰的 GitHub 演进节点。

补充两条执行约束：

1. 这些 phase 默认线性推进，不并行推进多个 phase。
2. 每个 phase 内部的多个任务可以并行，但 phase 结束前必须做一次和本阶段目标直接相关的简单测试，然后再同步文档并推送 GitHub。

### 面试前的结构目标

面试前不要求把整个仓库激进改造成纯 `apps/ + packages/` 结构，但必须做到：

1. 一眼看出哪些目录是应用入口，哪些目录是核心能力，哪些目录是评测、工具、文档和基础设施。
2. 后端内部能稳定解释控制层、服务层、DAO 层、基础设施层分别在哪里。
3. LangGraph、GraphRAG、Domain Pack、eval、runtime registry 这条主线有稳定目录归属。
4. 历史残留和过时入口不继续污染主阅读路径。
5. 后续如果要继续统一成更完整 monorepo 结构，当前目录也不成为阻碍。

所以面试前的正确目标不是：

```text
为了形式统一而做一次高风险全仓大迁移
```

而是：

```text
先把现有项目结构治理到清晰、稳定、可扩展，
再把未来继续统一 monorepo 的路径写清楚。
```

这部分工作默认归到新的 `Phase 2`，不再混在新的 `Phase 1` 里面做。

### 面试前最终目标

后续这些 phase 继续推进，最终不是为了“阶段完整”本身，而是为了完成文档里定义的那套目标架构：

```text
以 LangGraph 为核心运行时，
以 RAG / GraphRAG / Domain Pack 为知识主线，
具备 GraphRAG 动态更新、两档检索体验、本地评测、自动化测试、
清晰项目结构、清晰分层边界和正式 GitHub 展示面的本地优先 Agent 工作台。
```

也就是说，后续阶段的最终落点必须是：

1. 深入运用 LangGraph，而不是停留在简单 LangChain agent 封装
2. 深入运用 GraphRAG，而不是只做概念演示或表层接入
3. 让代码结构、项目结构、评测证据和文档口径最终一致

### 架构文档同步规则

后续每完成一次“大更新”，都要回到 `docs/architecture/` 做一次同步检查。

检查动作至少包括：

1. 当前这次改动解决了哪些原本写在架构文档里的问题
2. 哪些“未解决问题”现在已经不该继续保留
3. 哪些阶段目标已经完成，哪些阶段目标仍然未完成
4. 当前入口文档、README、phase 计划、spec 之间是否仍然口径一致

原则是：

```text
架构文档不是只在最开始写一次，
而要随着主线推进持续收口，
把已经解决的问题删掉，把仍未解决的问题保留下来。
```

---

## 1. 当前判断

### 1.1 当前项目适合继续改造

Zuno 已经具备工作台雏形：

- 后端：FastAPI / SQLModel / PostgreSQL / Redis / RabbitMQ
- Agent：LangChain / LangGraph / MCP / Skills / local CLI tools
- 知识库：Milvus / Neo4j / GraphRAG 相关能力
- 前端：Vue + Electron
- 部署：Docker Compose 一键启动 PostgreSQL、Redis、RabbitMQ、Milvus、Neo4j、MinIO、后端、Worker、前端

所以不建议推倒重写。应该在现有结构上做架构收束和能力深化。

### 1.2 当前主要问题

当前 Zuno 的问题不是“功能少”，而是“能力分散、边界不稳、领域化能力不成体系”：

1. `agentchat` 这个包名偏窄，长期会限制平台表达，但它不是这轮的第一优先级。
2. Zuno 已经用了 LangGraph，但还没有形成统一的“领域问答工作流中枢”。
3. GraphRAG 现阶段更像原型，难以支撑中文合同审查这类强领域任务。
4. 领域变化部分还没有插件化，缺少 Domain Pack 机制。
5. 测试和开发成本需要被设计进去，不能每轮改动都消耗真实 embedding 和大模型 API。
6. 目录边界还不够清楚，后续如果继续叠功能，维护成本会越来越高。

### 1.3 这轮真正要解决的核心问题

这轮不是单纯“增加合同审查功能”，而是要解决下面这个平台问题：

```text
如何让 Zuno 具备一种稳定方式，
把“领域 schema、图谱抽取、图检索、回答生成、评估、成本控制”
作为可插拔能力接入到统一 Agent Runtime 中。
```

如果这个问题解决了：

- 合同审查可以成为第一个高质量示范 Domain Pack
- 后续论文阅读、代码库问答、行业知识问答都能复用同一套骨架
- 未来多 Agent 也有稳定的子图和子能力挂载点

---

## 2. 改造目标

### 2.1 产品定位

Zuno 的定位应该是：

```text
Zuno：本地优先的可扩展 Agent 工作台
```

一句话描述：

```text
支持用户通过模型、Prompt、MCP、Skills、工具、知识库和 Domain Pack，
搭建不同领域的问答与任务执行 Agent。
```

合同审查只是第一个高质量示范插件：

```text
Contract Review Domain Pack：合同审查领域 GraphRAG 插件
```

### 2.2 本阶段产出目标

这轮改造结束时，应该至少得到下面这些结果：

1. 有一个可运行的 `contract_review` Domain Pack MVP。
2. LangGraph 成为领域问答主流程的显式编排层。
3. GraphRAG 从“正则原型”升级为“支持 schema / evidence / hybrid retrieval 的可扩展版本”。
4. 开发期有低成本模式，离线测试可跑。
5. 自动化评估能比较 offline / local / demo 三种开发配置。
6. 包名最终可以从 `agentchat` 收口到 `zuno`，但不阻塞前面能力落地。
7. 项目目录结构达到正式 GitHub 项目下“清晰、稳定、好讲解”的水位。

### 2.3 这轮不做什么

当前阶段不做：

- 多 Agent 生产化开发
- 大规模 UI 重做
- 为了改名或统一外观而做的大范围目录迁移
- 平行新造第二套 Agent Runtime

补充一条：

- 不在新的 `Phase 1` 尚未完成时做全仓路径革命

---

## 3. 核心架构思路

### 3.1 不平行重造，而是做能力收束

当前仓库已经有：

- LangGraph 相关 Agent
- RAG / GraphRAG / retrieval planner / orchestrator
- eval 资产

所以这轮不是另起炉灶，而是把这些资产收束成一条更稳定的主线：

```text
Domain Pack
  -> LangGraph Domain QA Workflow
  -> Retrieval Orchestrator
  -> Vector + Graph Hybrid Retrieval
  -> Answer + Citation
  -> Evaluation + Cost Control
```

### 3.2 统一接线点

这轮必须先定一个稳定接线点，否则后面所有设计都会悬空。

建议采用：

```text
knowledge / agent 可选绑定 domain_pack_id
```

推荐优先级：

1. 第一优先：knowledge 绑定 `domain_pack_id`
2. 第二优先：agent 默认声明 `domain_pack_id`
3. 保留未来能力：对话时动态指定 `domain_pack_id`

这样做的原因：

- 图谱抽取和检索首先依赖知识材料本身
- Agent 可以有默认领域，但知识库更适合作为 schema 的真实归属点
- 后续一个 Agent 访问多个 knowledge 时，也能按 knowledge 维度切 pack

### 3.3 三层能力分层

```text
第一层：统一 Runtime 层
- LangGraph workflow
- State / checkpoint / trace / permissions

第二层：检索与知识层
- Vector retrieval
- Graph retrieval
- Fusion / planner / orchestrator

第三层：领域扩展层
- Domain Pack
- schema
- extraction prompt
- retrieval policy
- answer/report template
- eval dataset
```

这样分层后：

- LangGraph 负责编排
- GraphRAG 负责领域知识路径
- Domain Pack 负责变化部分

---

## 4. 推荐目录结构

### 4.1 重构原则

目录整理要服务于“边界清晰”，而不是为了改动而改动。

这轮可以先按最终形态设计，但实施时分阶段迁移，避免一次性大搬家。

### 4.2 目标目录结构

```text
src/backend/
  agentchat/                  # 过渡期保留，最终改名为 zuno
    __init__.py
    main.py
    settings.py
    config.example.yaml

    api/
    config/
    core/
    database/
    evals/
    fixtures/
    middleware/
    prompts/
    schema/
    services/
    system_skills/
    tools/
    utils/

    domain_packs/

  alembic/
  fastapi_jwt_auth/
  alembic.ini
```

最终收口后：

```text
src/backend/
  zuno/
    ...
```

### 4.3 `core/`：统一 Runtime 与 LangGraph

```text
src/backend/agentchat/core/
  agents/
    general_agent.py
    react_agent.py
    codeact_agent.py
    agent_factory.py
    agent_config.py

  graphs/
    __init__.py
    states.py
    domain_qa_graph.py
    contract_review_graph.py
    tool_execution_graph.py

  runtime/
    agent_runtime.py
    event_stream.py
    checkpoint.py
    permissions.py
```

说明：

- `agents/` 保留现有 Agent 入口概念。
- `graphs/` 放显式 StateGraph 工作流，不再把复杂领域逻辑散落进多个 agent 文件。
- `runtime/` 统一执行、状态、事件流、权限、checkpoint。

### 4.4 `services/`：基础能力服务

```text
src/backend/agentchat/services/
  llm/
    providers.py
    deepseek_provider.py
    qwen_provider.py
    openai_provider.py
    ollama_provider.py

  embedding/
    providers.py
    local_bge_provider.py
    qwen_embedding_provider.py
    fake_embedding_provider.py
    cache.py

  knowledge/
    document_loader.py
    chunker.py
    vector_indexer.py
    retriever.py

  graphrag/
    core/
      models.py
      interfaces.py
      evidence.py

    extractors/
      regex_extractor.py
      structured_extractor.py
      cached_extractor.py

    graph_store/
      neo4j_client.py
      graph_writer.py
      graph_schema.py
      entity_resolver.py

    retrievers/
      entity_linker.py
      graph_retriever.py
      hybrid_retriever.py

    orchestrator.py
    evaluator.py

  domain_pack/
    models.py
    loader.py
    registry.py
    validators.py

  retrieval/
  rag/
  mcp/
  skills/
  tools/
```

说明：

- `retrieval/` 和 `rag/` 不必被立刻推翻，应该逐步吸纳进统一主线。
- `graphrag/` 负责图谱专属能力。
- `domain_pack/` 负责领域变化部分。

### 4.5 `domain_packs/`：领域插件

```text
src/backend/agentchat/domain_packs/
  contract_review/
    pack.yaml
    schema.json
    extraction_prompt.md
    retrieval_policy.yaml
    answer_template.md
    report_template.md
    eval_dataset.jsonl

  paper_reading/
    pack.yaml
    schema.json
    extraction_prompt.md
    retrieval_policy.yaml

  codebase_qa/
    pack.yaml
    schema.json
    extraction_prompt.md
    retrieval_policy.yaml
```

第一阶段只实现 `contract_review`。

---

## 5. Domain Pack 机制

### 5.1 为什么必须有 Domain Pack

GraphRAG 不能长期停留在通用 `Entity` 和 `RELATES_TO` 上。

不同领域的图谱模型天然不同：

```text
合同审查：合同、条款、当事人、义务、金额、期限、风险点、法规
论文阅读：论文、作者、方法、数据集、指标、实验、结论
代码库问答：文件、类、函数、接口、调用关系、依赖关系、测试用例
```

所以领域变化部分必须插件化，而不是硬编码在通用服务里。

### 5.2 Domain Pack 包含什么

```text
pack.yaml                # pack 元信息
schema.json              # 实体类型、关系类型、属性字段
extraction_prompt.md     # 抽取 Prompt
retrieval_policy.yaml    # 检索策略
answer_template.md       # 回答模板
report_template.md       # 报告模板
eval_dataset.jsonl       # 评估集
```

### 5.3 合同审查 Pack 示例

实体类型：

```text
Contract
Clause
Party
Obligation
Amount
Term
Risk
Regulation
Evidence
```

关系类型：

```text
CONTRACT_HAS_CLAUSE
PARTY_SIGNS_CONTRACT
CLAUSE_HAS_OBLIGATION
CLAUSE_HAS_RISK
CLAUSE_REFERENCES_REGULATION
RISK_SUPPORTED_BY_EVIDENCE
CLAUSE_CONFLICTS_WITH_CLAUSE
```

示例 `pack.yaml`：

```yaml
id: contract_review
name: 合同审查
version: 0.1.0
description: 用于合同条款问答、风险识别、引用溯源的 GraphRAG 领域插件
schema: schema.json
extraction_prompt: extraction_prompt.md
retrieval_policy: retrieval_policy.yaml
answer_template: answer_template.md
report_template: report_template.md
eval_dataset: eval_dataset.jsonl
```

### 5.4 Domain Pack 的运行责任

Domain Pack 不是“额外文档包”，而是运行时真正参与以下决策：

- 图谱抽取 schema
- relation 白名单
- retrieval policy
- 回答模板
- 报告模板
- 评估数据集

也就是说：

```text
同一个 LangGraph 流程
在不同 Domain Pack 下，
应该表现为不同的知识理解和检索行为。
```

---

## 6. GraphRAG 深度改造

### 6.1 当前问题

当前 `GraphExtractor` 更偏原型：

- 主要依赖规则或正则
- 对中文合同这类领域文本支持不足
- 图谱证据结构不完整

当前 `GraphRetriever` 也还不够领域化，它缺少：

- domain schema
- LLM 结构化抽取
- 实体归一化
- typed relation
- evidence
- relation confidence
- entity linking
- hybrid retrieval
- citation verification

### 6.2 改造目标

从：

```text
regex entity -> RELATES_TO -> neighbor query
```

升级为：

```text
Domain Pack schema
  -> structured extraction
  -> entity resolution
  -> typed graph writing
  -> vector + graph hybrid retrieval
  -> evidence bundle
  -> citation verified answer
```

### 6.3 新 Graph Extraction 流程

```text
chunk
  ↓
load domain schema
  ↓
LLM structured extraction / mock extraction / rule fallback
  ↓
validate JSON with Pydantic
  ↓
entity resolution
  ↓
write entities and relations into Neo4j
  ↓
cache extraction result
```

结构化抽取输出：

```json
{
  "entities": [
    {
      "local_id": "clause_001",
      "type": "Clause",
      "name": "违约责任条款",
      "properties": {
        "clause_no": "第八条"
      },
      "evidence": "第八条 违约责任……",
      "chunk_id": "chunk_123",
      "confidence": 0.86
    }
  ],
  "relations": [
    {
      "source": "clause_001",
      "target": "risk_001",
      "type": "CLAUSE_HAS_RISK",
      "evidence": "未约定违约金上限",
      "chunk_id": "chunk_123",
      "confidence": 0.81
    }
  ]
}
```

### 6.4 新 Graph Retrieval 流程

```text
query
  ↓
query understanding
  ↓
entity linking
  ↓
vector retrieval from Milvus
  ↓
graph traversal from Neo4j
  ↓
merge evidence bundle
  ↓
answer generation
  ↓
citation check
```

返回结果不要只是字符串路径，而应该包含结构化证据：

```json
{
  "graph_paths": [
    {
      "nodes": [],
      "relations": [],
      "evidence": [],
      "source_chunks": [],
      "score": 0.82
    }
  ]
}
```

### 6.5 Neo4j 写入建议

第一版不要让 label 完全动态，避免混乱。可以统一：

```cypher
(:GraphEntity {
  entity_id,
  name,
  type,
  domain_pack_id,
  knowledge_id,
  chunk_id,
  evidence,
  confidence
})
```

关系类型优先使用 Domain Pack 白名单：

```cypher
(:GraphEntity)-[:CLAUSE_HAS_RISK {
  relation_id,
  evidence,
  chunk_id,
  confidence,
  domain_pack_id
}]->(:GraphEntity)
```

如果担心动态关系类型过多，第一版也可统一：

```cypher
[:DOMAIN_RELATION {type: "CLAUSE_HAS_RISK"}]
```

但从可读性和领域表达上，typed relation 更好。

---

## 7. LangGraph 深度融合

### 7.1 目标不是“开始用 LangGraph”，而是“让 LangGraph 成为统一编排层”

Zuno 不是完全没用 LangGraph，而是还没有形成统一的领域问答工作流中枢。

所以这轮目标不是从零引入，而是：

```text
把现有 Agent / retrieval / GraphRAG / tool 调用能力
收束进一个稳定的 Domain QA Workflow
```

### 7.2 `DomainQAGraph`

这是 Zuno 的核心问答图。

```text
START
  ↓
load_agent_config
  ↓
resolve_domain_pack
  ↓
route_intent
  ↓
rewrite_query
  ↓
vector_retrieve
  ↓
entity_link
  ↓
graph_retrieve
  ↓
merge_context
  ↓
maybe_call_tool
  ↓
generate_answer
  ↓
citation_check
  ↓
END
```

### 7.3 State 设计

```python
class DomainQAState(TypedDict):
    user_id: str
    agent_id: str
    dialog_id: str
    query: str

    domain_pack_id: str | None
    knowledge_ids: list[str]

    intent: str | None
    rewritten_queries: list[str]

    vector_contexts: list[dict]
    graph_paths: list[dict]
    tool_results: list[dict]

    draft_answer: str | None
    citations: list[dict]
    final_answer: str | None

    trace_metadata: dict
    cost_metadata: dict
```

### 7.4 合同审查图

第一版优先复用 `DomainQAGraph`，不要过早拆太多图。

第二版再抽出独立 `ContractReviewGraph`：

```text
START
  ↓
parse_contract
  ↓
extract_contract_schema
  ↓
build_contract_graph
  ↓
detect_missing_clauses
  ↓
detect_risk_clauses
  ↓
retrieve_policy_evidence
  ↓
generate_review_report
  ↓
citation_check
  ↓
END
```

### 7.5 为什么这算深度使用 LangGraph

因为每一步都是节点，状态可测试、可追踪、可恢复。

不是简单：

```text
agent.invoke(messages)
```

而是：

```text
每个节点有输入输出
每个节点可以单测
每个节点可以 LangSmith trace
每个节点可以统计成本
每个节点可以失败重试
```

---

## 8. 模型、成本与开发配置

### 8.1 开发期不要一直用高成本配置

开发期建议：

```text
Embedding：本地 bge-small-zh / bge-m3 / fake embedding
LLM 抽取：DeepSeek / mock extraction
Answer：DeepSeek / 本地小模型 / mock
```

最终演示再切：

```text
Embedding：千问 text-embedding-v4
LLM：DeepSeek / Qwen / OpenAI-compatible model
```

### 8.2 Provider 设计

```text
services/llm/providers.py
services/embedding/providers.py
```

统一抽象：

```python
class LLMProvider:
    async def chat(self, messages: list[dict], **kwargs) -> dict: ...

class EmbeddingProvider:
    async def embed_documents(self, texts: list[str]) -> list[list[float]]: ...
    async def embed_query(self, text: str) -> list[float]: ...
```

实现：

```text
DeepSeekProvider
QwenProvider
OpenAIProvider
OllamaProvider
LocalBGEEmbeddingProvider
QwenEmbeddingProvider
FakeEmbeddingProvider
```

### 8.3 缓存机制

新增：

```text
embedding_cache
  - text_hash
  - model_name
  - dimension
  - embedding
  - created_at

graph_extraction_cache
  - chunk_hash
  - domain_pack_id
  - schema_version
  - extractor_model
  - extraction_json
  - created_at
```

缓存 key：

```text
embedding_cache_key = sha256(chunk_text + model_name + dimension)
graph_cache_key = sha256(chunk_text + domain_pack_id + schema_version + extractor_model)
```

### 8.4 开发期配置分层

```yaml
profiles:
  dev_offline:
    embedding_provider: fake
    graph_extractor: mock
    answer_provider: mock
    use_milvus: false
    use_neo4j: false

  dev_local:
    embedding_provider: local_bge
    graph_extractor: mock
    answer_provider: deepseek
    use_milvus: true
    use_neo4j: true
    max_documents: 3
    max_chunks_per_document: 20

  demo:
    embedding_provider: qwen
    graph_extractor: deepseek
    answer_provider: deepseek
    use_milvus: true
    use_neo4j: true
```

这样可以保证：

- 日常开发不依赖真实 API
- 本地调试能看到真实检索路径
- 最终演示再切高质量模型

---

## 9. 自动化测试与评估

### 9.1 保留并扩展现有 RAG Eval

当前已有 `evals/rag_eval`，里面有：

- `python_notes_eval.jsonl`
- `metrics.py`
- `prepare_python_notes_corpus.py`
- `ingest_prepared_corpus.py`
- `run_eval.py`

它已经可以比较 baseline RAG、rerank、GraphRAG 等配置，并生成本地指标。这个要保留，并继续扩展。

### 9.2 新增合同审查评估目录

```text
src/backend/agentchat/evals/contract_review_eval/
  README.md
  contract_eval.jsonl
  fake_contracts/
    loan_contract_001.md
    service_contract_001.md
    lease_contract_001.md
  expected_graphs/
    loan_contract_001.graph.json
  run_contract_eval.py
  reports/
```

### 9.3 合同评估数据样例

```json
{
  "id": "contract_001_q1",
  "query": "这份合同是否约定了违约责任？",
  "gold_evidence": [
    {
      "document": "loan_contract_001.md",
      "text_contains": "违约责任"
    }
  ],
  "reference_answer": "合同包含违约责任条款，应引用第八条。"
}
```

### 9.4 测试分层

#### Level 0：纯离线单元测试

不连 API，不连 Milvus，不连 Neo4j。

```text
test_domain_pack_loader.py
test_contract_schema_validation.py
test_mock_graph_extractor.py
test_fake_embedding_provider.py
test_domain_qa_graph_offline.py
```

#### Level 1：本地集成测试

使用本地 embedding / mock extraction / 本地 Neo4j。

```text
test_contract_ingest_pipeline.py
test_graph_writer_neo4j.py
test_hybrid_retriever_local.py
```

#### Level 2：小样本真实模型测试

只跑 5-20 个 chunk。

```text
run_contract_eval.py --profile dev_local
```

#### Level 3：演示评估

完整跑合同审查插件：

```text
run_contract_eval.py --profile demo --trace-langsmith
```

### 9.5 评估指标

```text
Retrieval Recall@K
Context Precision@K
Graph Path Hit Rate
Entity Extraction Precision
Relation Extraction Precision
Citation Accuracy
Faithfulness
Answer Correctness
LLM Call Count
Embedding Call Count
Estimated Cost
Latency
```

### 9.6 CI 建议

CI 不跑真实 API。

只跑：

```bash
pytest tests/test_domain_pack_loader.py
pytest tests/test_mock_graph_extractor.py
pytest tests/test_fake_embedding_provider.py
pytest tests/test_domain_qa_graph_offline.py
python src/backend/agentchat/evals/contract_review_eval/run_contract_eval.py --profile dev_offline
```

真实评估手动跑。

---

## 10. 多 Agent 规划：当前不开发，只预留

### 10.1 当前阶段

```text
单主 Agent + LangGraph workflow
```

### 10.2 为什么暂时不做多 Agent

多 Agent 会增加：

- 调试复杂度
- token 成本
- 上下文污染风险
- 工具权限管理复杂度
- 状态同步复杂度

当前最重要的是先把：

```text
Domain Pack + GraphRAG + LangGraph Runtime + Eval
```

做扎实。

### 10.3 未来多 Agent 的核心价值

```text
职责隔离
上下文隔离
工具隔离
权限隔离
记忆隔离
失败隔离
并行执行
审计隔离
评估隔离
人机协作边界
```

### 10.4 未来结构

```text
Supervisor Agent
  ├── Research Agent
  ├── GraphRAG Agent
  ├── Tool Executor Agent
  ├── Citation Verifier Agent
  └── Report Writer Agent
```

当前只需要在 `core/graphs/` 保留 subgraph 接口即可。

---

## 11. 历史开发路线图归档

这一节保留的是较早一版的阶段拆分，主要用于回溯“这些能力最初是怎么分批落地的”。

注意：

```text
这一节不是当前主执行 phase 体系。
当前主执行 phase 体系以 docs/architecture/plans/zuno-refactor-execution-plan.md 为准，
并且已经改成新的 Phase 1-7 线性编号。
```

### Phase 0：先确定接线点与改造边界

先完成设计确认，不急着大规模搬目录。

- 明确 `domain_pack_id` 的归属与传递方式
- 明确复用现有 retrieval / GraphRAG / LangGraph 资产的策略
- 明确这轮只做 `contract_review` 一个 MVP pack
- 明确 `agentchat -> zuno` 延后到最后

验收标准：

- 有一份统一的运行责任说明
- 代码层能明确知道 pack 在哪里挂载、谁读取、谁执行

### Phase 1：目录收束，但不先改包名

- 新增 `core/graphs/`
- 新增 `services/domain_pack/`
- 新增 `domain_packs/contract_review/`
- 新增 `services/llm/` 和 `services/embedding/`
- 清理 GraphRAG 模块结构

验收标准：

- 目录边界清楚
- 旧能力还能运行
- 不因为目录整理破坏现有启动链路

### Phase 2：Domain Pack MVP

- 实现 `DomainPackLoader`
- 实现 `DomainPackValidator`
- 实现 `contract_review/schema.json`
- 实现 `contract_review/extraction_prompt.md`
- 实现 `retrieval_policy.yaml`
- 写单元测试

验收标准：

- `contract_review` pack 能被正确加载和校验
- pack 信息能进入 runtime 或 retrieval 路径

### Phase 3：GraphRAG 重构

- 保留 `RegexGraphExtractor` 作为 fallback
- 新增 `StructuredGraphExtractor`
- 新增 `CachedGraphExtractor`
- 新增 `GraphWriter`
- 新增 `EntityResolver`
- 新增 `DomainGraphRetriever`
- 新增 `HybridRetriever`

验收标准：

- 合同样本文档可以完成结构化抽取
- 能得到带 evidence 的 graph path
- 图谱检索不是只返回字符串拼接结果

### Phase 4：LangGraph Runtime 收束

- 新增 `DomainQAState`
- 新增 `DomainQAGraph`
- 把合同审查 Agent 接入 `DomainQAGraph`
- 支持节点级 trace / cost metadata

验收标准：

- 合同审查问答能走显式 StateGraph
- 节点状态可观察
- 失败点、成本点、检索路径可追踪

### Phase 5：低成本测试与评估

- 新增 fake embedding
- 新增 mock graph extractor
- 新增合同样本文档
- 新增 contract review eval
- CI 跑 offline eval

验收标准：

- 离线开发不依赖真实 API
- 本地至少有一套稳定可重复评估流程

### Phase 6：演示版

- 用 DeepSeek 做结构化抽取和回答
- 可选用千问 embedding 做最终演示
- LangSmith 记录 trace
- 输出评估报告

验收标准：

- 有一套面向展示的真实质量结果
- 可以解释“为什么这个回答成立”

### Phase 7：包名收口 `agentchat -> zuno`

等前面能力稳定后，再做最终品牌与目录统一。

- `src/backend/agentchat` -> `src/backend/zuno`
- 全局 import 替换
- 更新 uvicorn 启动命令
- 更新 Docker / launchers / docs / config path
- 跑基础启动测试

建议采用兼容期：

```text
Phase A：新增 zuno 包，保留 agentchat alias
Phase B：迁移 import 到 zuno
Phase C：删除 agentchat alias
```

验收标准：

- 启动、Docker、launchers、测试、文档全部同步完成
- 改名不改变运行语义

---

## 12. 文档归档建议

关于“架构方向改动”的文档，建议统一收进 `docs/architecture/`，不要再散落到别的目录。

推荐：

```text
docs/architecture/
  README.md               # 架构文档索引
  specs/                  # 稳定的架构设计文档
  plans/                  # 分阶段实施计划
  decisions/              # 关键架构决策记录
```

适用方式：

- 这版大改动：放 `docs/architecture/specs/` 或作为总方案放在 `docs/architecture/`
- 未来多 Agent 设计：放 `docs/architecture/specs/`
- 多 Agent 待办拆解：放 `docs/architecture/plans/`
- 架构取舍和原因：放 `docs/architecture/decisions/`

`docs/development/` 仍然保留给安装说明、迁移步骤、运行手册，不负责承载架构主文档。

---

## 13. 修改后的 README 主线

建议 README 最终改成：

```text
Zuno 是一个本地优先的 Agent 工作台，支持用户通过模型、Prompt、MCP 服务、Skills、工具权限、知识库和 Domain Pack 搭建不同领域的问答与任务执行 Agent。

当前重点能力：
- LangGraph Agent Runtime
- RAG / GraphRAG
- Domain Pack 领域插件机制
- MCP / Skills / local CLI 工具调用
- 本地优先部署
- 低成本自动化评估

当前示范插件：
- Contract Review Domain Pack：合同审查领域 GraphRAG 插件
```

---

## 14. 最终建议

本次改造的核心不是“加一个合同问答功能”，而是：

```text
把 Zuno 从“功能堆叠型 Agent 工作台”
升级为
“支持 Domain Pack 的 LangGraph + GraphRAG Agent 工作台”
```

而且顺序必须正确：

```text
先做统一接线点
  -> 再做 Domain Pack MVP
  -> 再做 GraphRAG 深化
  -> 再做 LangGraph Runtime 收束
  -> 再做低成本评估闭环
  -> 最后做 agentchat -> zuno 改名收口
```

第一阶段不要做多 Agent。先把单主 Agent 的工作流、领域建模、图谱检索、评估体系做深。多 Agent 保留为未来扩展点。
