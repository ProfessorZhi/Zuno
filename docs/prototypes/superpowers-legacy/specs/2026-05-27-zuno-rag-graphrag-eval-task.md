# Zuno RAG / GraphRAG 自动化评测任务

## 任务目标

这项任务不是单纯“把 RAG 跑起来”，而是建立一套**能反哺简历表述**的自动化评测闭环。

最终目标有两个：

1. 为 Zuno 的知识库能力选出一套更优的检索配置，而不是拍脑袋默认开启某个模式。
2. 产出一组可信、可解释、可复现的评测指标，后续可以提炼为简历中的项目亮点。

这套评测必须**正式覆盖 GraphRAG**，但不能先假设 `RAG + GraphRAG` 一定最优。正确流程是先用小样本做参数选择和模式消融，再把最优配置放到大样本资料池上验证。

## 面向简历的结果要求

最后能写进简历的内容，目标是这类表述：

- 基于 LangSmith + 本地离线评测脚本搭建 RAG / GraphRAG 自动化评测链路，覆盖 Recall、Context Precision、MRR、NDCG、Citation Accuracy 等指标。
- 通过小样本实验比较纯 RAG、RAG + Rerank、RAG + GraphRAG 等配置，在混合格式知识库上选出最优检索方案。
- 在大样本技术资料库上完成自动化评测，验证 GraphRAG 在关系型问题、跨文档关联问题上的收益与噪声边界。

注意：简历里只能写**最终真实跑出来**的数字和结论，不能把预期指标当结果写。

## 数据范围

### 第一阶段：小样本调参集

使用当前已经整理好的样本：

```text
F:\resume project\03_rag_eval_dataset\prepared\mixed_tuning_v2
```

这一版包含：

- `markdown_txt`
- `html`
- `pdf`
- `semi_structured`
- `images`
- `office`
- `tables`

用途：

- 快速调参
- 模式消融
- 检查 GraphRAG 是否对“关系型问题”真的有帮助

### 第二阶段：大样本正式评测

使用已经收集并解压的原始资料池，按格式和主题做再抽样，构成正式知识库评测集。

目标不是直接“全量吞完几个 G 就算完”，而是：

1. 保留真实异构资料的复杂度。
2. 控制构建成本和评测时长。
3. 保证问题样本覆盖不同检索难度。

建议正式评测集控制在：

- 原始资料池：`2GB+`
- 实际建库评测子集：`0.8GB - 1.5GB`
- 问题数：`100 - 200`

## 评测阶段设计

## 阶段一：小样本参数选择

目的：

- 确定一套更优的基础参数。
- 判断 GraphRAG 是否值得进入正式大样本评测。
- 找到最适合 Zuno 当前知识库链路的模式组合。

### 需要比较的候选配置

至少比较这几类 profile：

1. `纯 RAG`
2. `RAG + Rerank`
3. `父子分段 + RAG + Rerank`
4. `RAG + GraphRAG`
5. `RAG + GraphRAG + 3-hop`

其中 GraphRAG 相关配置必须正式参与比较，不能只作为附带实验。

### 建议调参维度

第一阶段不宜把参数网格铺得过大，先控制在少量高价值维度：

- chunk strategy
  - `general`
  - `parent_child`
- chunk size
  - `512`
  - `768`
  - `1024`
- overlap
  - `50`
  - `100`
- top K
  - `5`
  - `8`
  - `10`
- rerank
  - `off`
  - `on`
- rerank top K
  - `3`
  - `5`
- score threshold
  - `0.60`
  - `0.70`
  - `0.75`
- graph hop limit
  - `2`
  - `3`
- max paths per entity
  - `5`
  - `10`

### 小样本问题集要求

第一阶段问题数建议为：

```text
30 - 50 条
```

问题必须覆盖这几类：

1. **精确定位型**
   - 单条事实、定义、参数、字段含义
2. **多段汇总型**
   - 需要从多个 chunk 归纳答案
3. **跨文档关联型**
   - 需要联合多个文件的信息回答
4. **关系型 / 结构型**
   - 更适合 GraphRAG 的问题，例如依赖、引用、调用、实体关系
5. **图文混合型**
   - 涉及图片描述、图示说明、结构图

其中第 4 类必须单独标注，因为它是判断 GraphRAG 是否真的有价值的关键。

## 阶段二：大样本正式评测

目的：

- 在更真实、更复杂的资料池上验证阶段一选出的最优配置。
- 形成可沉淀到简历和项目说明中的正式结果。

### 正式对比配置

第二阶段不要继续大范围调参，只保留：

1. `Baseline`
   - 纯 RAG
2. `Strong baseline`
   - RAG + Rerank
3. `Best profile`
   - 阶段一选出的最优配置

如果阶段一证明 GraphRAG 确实最优，则 `Best profile` 可以是：

```text
RAG + GraphRAG + rerank + selected chunk strategy
```

如果阶段一证明 GraphRAG 只在少数关系型问题上有收益，而总体不占优，则不能强行把它包装成全局最优，只能写成：

- 对关系型问题有效
- 适合作为高级增强模式

## 指标体系

本任务统一统计五个核心指标：

1. `Recall@K`
2. `Context Precision@K`
3. `MRR@K`
4. `NDCG@K`
5. `Citation Accuracy`

如果时间和成本允许，可以额外统计两项回答质量指标：

6. `Faithfulness`
7. `Answer Correctness`

但简历第一版优先使用前五项，因为它们更直接反映检索链路质量。

## GraphRAG 专项要求

这次评测不是“顺手开一下 GraphRAG”，而是要**明确测它的收益边界**。

所以必须额外做两件事：

### 1. 单独标记 GraphRAG 友好问题

在评测集里给样本加标签，例如：

```json
{
  "question_type": "graph_relation"
}
```

这类问题包括：

- 某个实体和另一个实体之间是什么关系
- 某个组件依赖哪些模块
- 某个概念在多个文档中如何关联
- 某条路径如何从 A 连到 B

### 2. 单独输出分类型结果

最终报告里不能只看 overall score，还要单独给出：

- `fact`
- `summary`
- `cross_doc`
- `graph_relation`
- `multimodal`

这样才能知道：

- GraphRAG 是否真的提升了 `graph_relation`
- 它有没有拉低其他问题类型
- 3-hop 是增强还是引入噪声

## 评测产物

每次评测输出到：

```text
src/backend/agentchat/evals/rag_eval/runs/<timestamp>/
```

至少包含：

- `config.json`
- `retrieval_results.jsonl`
- `answers.jsonl`
- `judge_results.jsonl`
- `metrics.json`
- `report.md`

此外建议补两类方便简历和复盘的产物：

- `best_vs_baseline_diff.md`
  - 汇总最优配置相对 baseline 的关键提升
- `failure_cases.md`
  - 保存最典型的失败样本，方便后续讲项目时解释为什么需要 GraphRAG / rerank / parent-child chunk

## LangSmith 使用方式

LangSmith 用于：

- 记录 retrieval trace
- 保存最终 answer、citation、graph path
- 对比不同 profile 的链路差异
- 回放失败样本

LangSmith **不是**指标计算器。Recall、MRR、NDCG 仍然由本地离线评测脚本负责。

接入要求：

- 使用你的 LangSmith 账号接入
- 通过本地环境变量或安全配置文件注入 key
- 不把账号密码或 API key 明文写入仓库文档

建议环境变量形式：

```text
LANGSMITH_API_KEY=...
LANGCHAIN_API_KEY=...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Zuno-RAG-Eval
```

如果后续需要记录“当前评测使用的是你的账号”，可以在本地私有说明或 `.env.local` 中标注，不进入公开文档正文。

## 执行顺序

建议严格按这个顺序推进：

1. 确认小样本知识库可稳定建库
2. 生成 30 - 50 条小样本评测问题
3. 跑第一轮 profile 对比
4. 选出最优配置
5. 生成大样本评测问题集
6. 跑 baseline / strong baseline / best profile
7. 产出总报告和简历可用摘要

## 验收标准

任务完成不以“跑通一次”为标准，而以以下结果为标准：

1. 能稳定复现至少三组 profile 的评测结果
2. 五个核心指标全部可计算
3. GraphRAG 的收益边界被单独分析，而不是只看 overall
4. 有一份适合写进简历的简要结果摘要
5. 有一份适合后续继续迭代的失败样本报告

## 简历提炼原则

最后写简历时遵守三条规则：

1. 只写真实跑出来的结果。
2. 不把“GraphRAG 开启了”写成“GraphRAG 一定最好”。
3. 更强调“建立评测闭环”和“基于数据选型”，而不是单点堆技术名词。

更稳的表达方向是：

- 搭建 RAG / GraphRAG 自动化评测链路
- 比较不同检索模式与分段策略
- 基于指标选出最优配置
- 在混合格式知识库上验证检索效果

而不是：

- GraphRAG 一开效果暴涨

后者只有在最终数据真的支持时才能写。
