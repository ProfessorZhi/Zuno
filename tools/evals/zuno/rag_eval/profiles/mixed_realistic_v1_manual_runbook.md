# mixed_realistic_v1 手动验证手册

这份手册的目标不是自动化跑完，而是让你可以在 `Zuno` UI 里手动完成：

1. 导入测试知识库
2. 建一个专用测试智能体
3. 用固定问题手动验证 `RAG + BM25 + GraphRAG`
4. 在 LangSmith 里回看整条链路

## 先决条件

当前建议配置：

- `LangSmith` 已开启
- `Elasticsearch` 已加入 Docker 栈
- `rag.enable_elasticsearch = true`
- `Neo4j`、`Milvus`、`RabbitMQ`、`PostgreSQL`、`MinIO` 都在线

如果你看到 `9200` 不通，说明 BM25 还没真的启用，这时只能测向量和 GraphRAG，不能测完整混合检索。

## 推荐手动导入方式

### 方式 A：直接用 UI 导入

1. 打开“知识库”
2. 新建一个知识库，名字建议：`ZunoMixedRealisticV1`
3. 建库方式选：`RAG + GraphRAG`
4. 查询设置里默认模式先选：
   - `标准检索`
5. 打开文件页，把下面目录里的文件一次性上传：

`.local/evals/agentchat/rag_eval/corpus/mixed_realistic_v1/files`

6. 等索引完成

建议第一轮先不要改 chunk 参数，用默认推荐值。

### 方式 B：脚本导入

如果你不想手点上传，可以执行：

```powershell
python tools/evals/zuno/rag_eval/ingest_prepared_corpus.py `
  --manifest .local/evals/agentchat/rag_eval/corpus/mixed_realistic_v1/manifest.json `
  --knowledge-name ZunoMixedRealisticV1 `
  --output .local/evals/agentchat/rag_eval/runs/mixed_realistic_v1_ingest.json
```

## 推荐建一个专用测试智能体

智能体建议：

- 名称：`MixedRealisticEvalAgent`
- 执行模式：普通问答即可
- 访问范围：只勾这个测试知识库
- 工具：先尽量少，只保留知识库检索相关路径

原因：

- 降低工具调用噪声
- 避免 Web search 或别的 MCP 抢答
- 让 LangSmith trace 更干净

## 第一轮手动测试问题

先按四类各挑 1 到 2 题手测：

### 1. BM25 / 精确词

- `系统用哪个请求头把 trace id 传进来？`
- `图谱抽取任务会投递到哪个 queue 名字？`

预期：

- `标准检索` 应该就能很好命中
- trace 里应看到 `bm25` 参与

### 2. 语义事实

- `为什么标准检索适合作为默认模式？`
- `什么类型的问题更适合 BM25 路线，而不是只靠向量检索？`

预期：

- 向量路径应该能起主要作用
- BM25 是辅助，不一定主导排序

### 3. 跨文档整合

- `部署 Zuno Web 栈时，应用进程和底层依赖分别有哪些？`
- `Zuno 里对象存储、关系库、缓存、向量库和图数据库分别承担什么角色？`

预期：

- 要命中多个 chunk
- 结果里应该能看到更完整的 merged contexts

### 4. GraphRAG

- `ProjectOrion 的 incident escalation 最终关联到哪个看板？`
- `ProjectOrion 的 incident escalation 最终会落到哪个区域？`

预期：

- `图谱增强检索` 应该明显优于 `标准检索`
- trace 里应能看到 graph retriever 和 path / entity 信息

## 你在 LangSmith 里该看什么

优先看这几层：

1. `metadata.profile` / `dataset_name`
   确认这是混合测试集链路

2. `retrieval plan`
   看：
   - `requested_mode`
   - `resolved_mode`
   - `enabled_retrievers`

3. `retriever_runs`
   看：
   - `vector`
   - `bm25`
   - `graph`
   每路各召回了多少条

4. `rounds`
   看是否发生：
   - route broadening
   - query rewrite retry

5. 最终答案与证据
   看是不是：
   - 有证据但回答丢了
   - 没召回到证据
   - Graph 路径有了但最终没排上来

## 你手动切模式时怎么测

建议每道关键题至少测两次：

1. `标准检索`
2. `图谱增强检索`

如果某道题是精确术语题：

- `标准检索` 理应已经够好
- 如果它还不稳，通常说明 BM25 没接上，或者 ES 索引没建好

如果某道题是关系链题：

- `图谱增强检索` 应该更强
- 如果没有提升，通常要看：
  - 图谱索引是否生成
  - graph retriever 有没有命中实体
  - graph path 有没有被最终融合进去

## 最后再跑批量评测

等你手测 6 到 8 题觉得链路正常，再跑：

```powershell
python tools/evals/zuno/rag_eval/run_eval.py `
  --dataset tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl `
  --knowledge-id <knowledge_id> `
  --profiles baseline_rag,rag_rerank_recall_first,rag_graph_chunk_backed `
  --output-dir .local/evals/agentchat/rag_eval/runs/mixed_realistic_v1_first_pass `
  --trace-langsmith
```

## 现在这套手册的边界

这版是“先能真实测起来”的手册，不是最终基准。

后续我建议继续补：

- 更多 `keyword_exact` 样本，拉开 BM25 优势
- 更多 `graph_relation` 样本，验证 GraphRAG 稳定性
- 一个显式 `rag_bm25_hybrid` profile，别再借旧名字解释
