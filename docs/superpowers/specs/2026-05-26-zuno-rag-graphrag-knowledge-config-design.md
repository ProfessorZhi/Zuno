# Zuno RAG / GraphRAG Knowledge Config Design

## Goal

把知识库配置从一组混杂的开关，整理成面向用户可理解、面向工程可落地的两层设计：

1. **索引能力模式**：决定当前知识库已经构建哪些索引能力。可以中途升级或降级，但会触发重建或补建受影响索引。
2. **查询检索策略**：每次提问时使用，决定如何召回、重排、补检和组织上下文。

第一版只提供两个主模式：

- **纯 RAG 模式**：文档切分后写入向量库，查询时只走文本/图文向量召回。
- **RAG 入口 + GraphRAG 模式**：先用 RAG 找到高相关 chunk，再从 query 和命中 chunk 中抽取实体作为图谱入口，到 Neo4j 扩展关系路径，最后把 RAG 文本证据和 GraphRAG 关系证据一起返回给 Agent。

## Why This Shape

当前 UI 里 `自动补检 / 混合检索 / 智能补检 / 图谱检索` 看起来像四选一，但它们不是同一层级：

- `混合检索 / 图谱检索` 是检索路径。
- `自动补检 / 智能补检` 是首轮召回质量不足时的 fallback 策略。

如果继续放在同一个单选组里，用户会误以为它们互斥，也不容易理解 GraphRAG 到底何时参与。

## Concepts

### RAG Index

RAG 索引指把文档加工成可检索结构：

```text
原始文件 -> 文本/图片解析 -> chunk 切分 -> embedding -> 向量库 -> chunk 元数据
```

向量库保存的是 chunk 的语义向量和元数据，例如 `chunk_id`、`file_id`、`knowledge_id`、`source_url`。

### GraphRAG Index

GraphRAG 索引指从 chunk 中抽取实体和关系，写入 Neo4j：

```text
chunk -> entity / relation extraction -> Neo4j Entity / Relation -> relation path retrieval
```

成熟模型里应保留 evidence back-link：

```text
Document -[:HAS_CHUNK]-> Chunk
Chunk -[:MENTIONS]-> Entity
Entity -[:RELATES_TO]-> Entity
```

第一版可以先实现轻量结构，但数据模型和接口要为 `Chunk -> Entity` 的证据回链预留字段。

## Infrastructure Roles

这套知识库链路依赖的基础设施职责必须明确，避免把组件混成一层。

- **PostgreSQL**：主业务数据库，保存用户、知识库、文件、Agent 配置、工具配置、任务记录和配置快照。
- **Redis**：短期状态和缓存，保存登录态、验证码、异步任务进度、运行时临时状态。
- **RabbitMQ**：异步任务队列，负责在解析、向量索引、图谱索引等阶段之间传递任务。
- **MinIO**：对象存储，保存上传原始文件、图片、解析中间产物和工具输出文件。
- **Vector DB**：保存 chunk embedding 和检索元数据。企业化部署默认使用 Milvus；Chroma / Milvus Lite 可作为本地轻量 fallback。
- **Neo4j**：保存 GraphRAG 的实体、关系、路径和证据回链。

目标不是让所有组件都出现在每次查询里，而是让它们在对应链路上真实承担职责。

## Index Capability Modes

### 1. Pure RAG

适合普通文档问答、成本敏感场景和快速建库。

Build flow:

```text
file upload
-> MinIO
-> parse text / image
-> chunk
-> text embedding / optional VL embedding
-> vector DB
```

Query flow:

```text
query
-> vector retrieval
-> optional rerank
-> normalized text evidence
-> Agent
```

能力约束：

- 查询模式只能使用 RAG。
- GraphRAG 查询参数应置灰。
- 如果后续升级到 RAG + GraphRAG，不需要重建文本向量索引，但需要基于已有 chunk 补建图谱索引。

### 2. RAG Entry + GraphRAG

适合模块关系、依赖关系、概念网络、调用链、影响分析等问题。

Build flow:

```text
file upload
-> MinIO
-> parse text / image
-> chunk
-> text embedding / optional VL embedding
-> vector DB
-> entity and relation extraction
-> Neo4j graph index
```

Query flow:

```text
query
-> RAG top-k chunk retrieval
-> extract candidate entities from query + top-k chunks
-> Neo4j 1-hop / 2-hop relation expansion
-> merge text evidence + graph relation evidence
-> optional rerank / context compression
-> Agent
```

能力约束：

- 查询模式可以选择 RAG，也可以选择 RAG + GraphRAG。
- 如果查询选择 RAG，则只走向量召回，不使用 Neo4j。
- 如果查询选择 RAG + GraphRAG，则 RAG 结果和 GraphRAG 结果都返回给 Agent，GraphRAG 作为关系补充而不是替代 RAG 证据。

返回给 Agent 的上下文必须区分证据来源：

```json
{
  "text_evidence": [
    {"chunk_id": "...", "content": "...", "score": 0.86}
  ],
  "graph_evidence": [
    {"path": "Zuno -> RabbitMQ -> worker", "source_chunks": ["..."]}
  ]
}
```

如果图谱入口为空或 Neo4j 无结果，系统应降级为 Pure RAG，而不是直接返回空结果。

## GraphRAG Parameters

GraphRAG 参数分为两类，不能都放进“索引设置”。

### Graph Index Parameters

这些参数影响 Neo4j 图谱如何构建，修改后需要重建或补建图谱索引：

- entity extraction mode：规则抽取 / LLM 抽取 / 规则 + LLM 辅助。
- relation schema：通用关系 / 代码依赖关系 / 文档概念关系。
- entity normalization：是否做别名合并、大小写归一、同义实体合并。
- evidence backlink：是否建立 `Chunk -> Entity` 证据回链。
- graph entry source：是否优先使用 RAG 命中 chunk 作为图谱入口来源。

### Graph Query Parameters

这些参数只影响查询阶段，修改后不需要重建索引：

- graph hop limit：默认 2-hop，允许 1-hop / 2-hop / 3-hop。
- max paths per entity：每个实体最多返回多少条关系路径。
- max graph evidence：最终交给 Agent 的图谱证据条数。
- graph score threshold：如果后续引入关系置信度，可按阈值过滤路径。

跳数默认 2-hop 是为了控制噪声；3-hop 作为高级选项开放，但不作为默认值。

## Chunk Strategy

Chunk 策略属于建库索引配置。只要改了 chunk 策略或 chunk 参数，就必须重建对应文件的索引，因为 chunk_id、chunk 内容、embedding 和图谱实体关系都会变化。

### General Chunk

默认策略。

适合普通文档、网页文本、杂项资料。

规则：

- 优先按分隔符切分，例如空行 `\n\n`。
- 每块受 `chunk_size` 控制。
- 相邻块保留 `overlap`，避免边界信息丢失。
- Markdown 文档优先保留标题路径。

### Parent-Child Chunk

适合长文档和技术文档。

规则：

- parent chunk 保存较完整上下文。
- child chunk 用于精确召回。
- 命中 child 后，把 parent 作为上下文回填。

好处是兼顾精确召回和完整上下文。

### Q&A Chunk

适合 FAQ、客服问答、面试题、手册问答。

第一版只支持显式 Q&A 结构解析，例如：

```text
Q: xxx
A: yyy
```

或 Markdown 里的固定问答格式。

不默认用 LLM 自动生成 Q&A，因为自动生成会引入成本、幻觉和难以审计的问题。后续可以作为增强功能。

## Image Indexing

图片处理属于建库索引配置。改动图片处理策略后，需要重建受影响文件的索引。

### Text Only

```text
image -> OCR/VLM description -> text embedding
```

适合希望图片内容也能被普通文本问题搜到的场景。

### VL Only

```text
image -> VL embedding
```

适合以图搜图或强视觉语义检索场景。

### Dual Channel

```text
image -> OCR/VLM description -> text embedding
image -> VL embedding
```

这是高质量默认选项。查询时可以同时返回：

- 图片描述文本。
- 图片 source_url / object key。
- VL 召回分数。

如果当前回答模型不支持多模态输入，Agent 只使用图片描述和图片链接；如果支持多模态，再把图片 URL 作为可见证据传入。

## Retrieval-Time Strategy

查询时策略不应该和建库索引模式混成一个四选一。

建议 UI 拆成：

### Retrieval Mode

- **RAG**：只用向量召回。
- **RAG + GraphRAG**：用 RAG top-k 作为图谱入口，再扩展关系路径。

这个选项受建库模式约束：如果知识库没有图谱索引，只能使用 RAG。

不在普通 UI 暴露 Pure GraphRAG。纯图谱检索依赖实体入口，空召回风险高，适合作为内部诊断或高级调试能力。

### Quality Controls

这些是查询时参数，通常不需要重建索引：

- `top_k`
- `rerank_top_k`
- `score_threshold`
- `rerank_enabled`
- `rerank_model`
- `auto_refill_enabled`
- `smart_refill_enabled`

`rerank_model` 改了不需要重建索引，因为 rerank 发生在召回之后。

### Refill Policy

自动补检不是检索模式，而是 fallback policy。

第一版定义两种：

- **Auto Refill**：首轮结果为空、数量不足或分数低于阈值时，再扩大 top-k 或重写 query 补检一轮。
- **Smart Refill**：根据失败原因选择补检动作，例如 query rewrite、切换到 RAG + GraphRAG、降低 score threshold 或扩大 top-k。

默认推荐：

```text
Pure RAG knowledge: RAG + Auto Refill
RAG + GraphRAG knowledge: RAG + GraphRAG + Smart Refill
```

补检跟随当前检索模式：

- RAG 查询下，补检只补向量召回，例如 query rewrite、扩大 top-k、放宽阈值。
- RAG + GraphRAG 查询下，先补 RAG；如果 RAG 命中但图谱无路径，再补 GraphRAG，例如改用命中 chunk 中实体、扩大 hop、增加路径上限。

## Rebuild Rules

### Must Rebuild Index

修改这些配置后，必须重建受影响文件的索引：

- chunk mode：general / parent-child / Q&A
- chunk size
- overlap
- separator
- cleaning rules
- image indexing mode：text only / VL only / dual channel
- text embedding model
- VL embedding model
- vector DB backend migration：Chroma -> Milvus
- GraphRAG enable / disable
- graph extraction prompt or schema
- entity normalization rule
- evidence backlink setting

原因：这些会改变 chunk、embedding、图片向量、实体或关系结构。

### No Rebuild Needed

修改这些配置通常不需要重建索引：

- top_k
- rerank_top_k
- score threshold
- rerank enabled
- rerank model
- retrieval mode 在已有索引能力内切换
- auto refill / smart refill
- graph hop limit
- max paths per entity

原因：这些只影响查询阶段，不改变已入库的索引内容。

### Partial Rebuild

索引能力中途变化时，尽量做局部重建：

- Pure RAG -> RAG + GraphRAG：保留向量索引，对已有 chunk 补建 Neo4j 图谱。
- RAG + GraphRAG -> Pure RAG：可以保留图谱索引但标记为 inactive，也可以按清理策略删除 Neo4j 图谱数据。
- Chroma -> Milvus：必须重建向量索引，GraphRAG 是否重建取决于 chunk 是否变化。
- embedding model change：必须重建向量索引；如果 chunk 不变，Neo4j 关系可保留。
- chunk strategy change：向量索引和图谱索引都必须重建。

### Document Update

新增或更新文档时，只重建该文档对应的索引：

```text
delete old chunks / vectors / graph edges for file_id
-> parse updated file
-> rebuild vector index
-> rebuild graph index if enabled
```

删除文档时，也必须同步删除：

- vector DB 中的 chunk vectors
- Neo4j 中与该 file/chunk 关联的实体关系证据
- PostgreSQL 中的 knowledge_file 元数据
- MinIO 中的原始对象，按保留策略决定是否物理删除

## Recommended UI Shape

### Basic

```text
知识库模式
  ○ 纯 RAG
  ○ RAG + GraphRAG
```

如果选择纯 RAG：

- 查询模式锁定为 RAG。
- GraphRAG 查询参数置灰。

如果选择 RAG + GraphRAG：

- 查询模式可选 RAG 或 RAG + GraphRAG。
- GraphRAG 索引参数和查询参数可配置。

### Optional Presets

质量预设可以后续作为快捷入口，不作为第一版必须功能。

- 节能：General Chunk + Text Index + RAG + no rerank
- 标准：General/Parent-Child + Text Index + RAG + rerank
- 高质量：Parent-Child + Dual Channel + RAG + GraphRAG + rerank + smart refill

### Advanced

高级设置再展开：

- chunk mode
- chunk size
- overlap
- separator
- image indexing mode
- embedding model
- VL embedding model
- rerank model
- top_k / rerank_top_k / score threshold
- vector DB backend
- GraphRAG index parameters
- GraphRAG query parameters

### Status and Actions

页面必须显示当前索引状态，避免用户不知道保存后发生什么：

- vector index status：not built / ready / stale / building / failed
- graph index status：not built / ready / stale / building / failed
- pending files count
- last indexed time

保存动作分为：

- 保存查询设置：只保存即时生效参数。
- 保存并补建图谱索引：适用于 Pure RAG 升级到 RAG + GraphRAG。
- 保存并重建索引：适用于 chunk、embedding、图片索引、向量库迁移等变化。

## Evaluation Plan

为了把这套能力写进简历，必须跑出可解释的评测结果。

### Dataset

构造 `query -> gold evidence` 小型评测集：

- query
- expected chunk_id / file_id
- expected entity / relation path
- answer type：fact / relation / image / mixed

### Metrics

RAG metrics:

- HitRate@K
- Recall@K
- MRR
- NDCG@K

GraphRAG metrics:

- entity hit rate
- relation path hit rate
- graph fallback rate

End-to-end metrics:

- answer groundedness
- citation correctness
- no-answer accuracy

### Trace

LangSmith / Langfuse 用于记录：

- query
- chosen retrieval mode
- top-k chunks
- graph paths
- rerank scores
- final context
- final answer

离线脚本计算指标，trace 系统用于回放失败案例和对比配置。

## Resume-Safe Wording

如果实现并跑通评测，可以写：

```text
设计 RAG / GraphRAG 分层检索策略：轻量模式走向量 RAG，增强模式以 RAG 召回结果作为实体入口进行 Neo4j 关系扩展，并融合文本证据与关系路径上下文；构建离线评测集统计 Recall@K、MRR 等指标，结合 trace 回放定位 chunk、embedding、rerank 与图谱扩展问题。
```

在评测数据未跑出前，不写具体提升百分比。

## Implementation Status

2026-05-26 已落地第一版配置模型改造：

- 后端 schema 新增 `index_capability`、`graph_index_settings`、`vector_backend`、`refill_policy`、`graph_hop_limit`、`max_paths_per_entity`。
- 旧配置值兼容映射：`hybrid` / `graphrag` 会归一到新语义 `rag_graph`，纯 RAG 知识库会锁定 `default_mode=rag`。
- GraphRAG 索引阶段会读取 `index_capability`：只有 `rag_graph` 知识库才构建 Neo4j 图索引，纯 RAG 知识库跳过图索引。
- Docker Compose 新增 Milvus standalone 和 etcd，后端与 worker 等待 Milvus 健康后启动。
- Docker 配置默认向量库从 Chroma 切到 Milvus；Chroma / Milvus Lite 仍作为代码层 fallback。
- 前端配置 payload 和工具函数已切换到 `纯 RAG` / `RAG + GraphRAG` 两种检索语义，并保留旧值兼容。
- `knowledge-config.vue` 已重写为新版配置页：建库方式、索引设置、GraphRAG 索引参数、查询设置、索引模型和即时预览分层展示。
- Docker Compose 静态解析已确认服务包含 `postgres`、`redis`、`rabbitmq`、`minio`、`neo4j`、`etcd`、`milvus`、`backend`、`worker`、`frontend`；2026-05-27 运行态已确认 PostgreSQL、Redis、RabbitMQ、MinIO、Neo4j、etcd、Milvus、backend、worker 均处于 healthy / running 状态。
- 检索链路已支持把 profile 级 `top_k`、`rerank_enabled`、`score_threshold`、`graph_hop_limit`、`max_paths_per_entity` 等查询参数传入 RAG / GraphRAG runtime。
- `RAG + GraphRAG` 已按设计把 RAG 命中 chunk 作为图谱入口来源之一，而不是只从原始 query 直接匹配实体。

尚未完成：

- 检索 orchestrator 仍复用旧 `hybrid` 内部路径作为兼容实现，后续需要把返回 metadata 改成面向产品的 `rag_graph` 命名。
- 当前浏览器验证停在 Zuno 唤醒/登录页，尚未完成配置页面截图级验收。
