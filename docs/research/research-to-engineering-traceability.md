# Research → Engineering Traceability

> status: research-reference
> canonical_architecture: no

本文件回答一个核心问题：**一项论文、算法、模型、数据集或实验系统怎样才能成为 Zuno 可长期依赖的工程能力？**

## 核心分层

```text
Research Artifact
!= Capability
!= Provider
!= Qualified Provider
!= Formal Business Fact
```

### Research Artifact

论文阶段产出的模型、算法、数据集、Prompt strategy、Retriever、Graph construction、Evidence extraction、Legal fact representation、Evaluation benchmark 或 Workflow method。

它通常证明的是：在明确数据、实验配置和评价指标下，某个局部问题可以被更好地解决。

### Engineering Capability

工程系统需要稳定的是“专业能力承诺”，例如事件抽取、法条推荐、争议识别、法律分析，而不是某个具体论文模型的类名。

Capability 至少需要说明：

- 输入与输出语义；
- 错误 / unsupported 语义；
- 版本；
- 适用任务范围；
- 最低质量条件；
- Provider 可替换条件。

### Provider

Provider 可以是研究模型、规则、LLM、本地服务或外部 API。Provider API 能调用、Schema 能解析，只说明 Conformance 的一部分，不说明专业质量等价。

### Qualified Provider

Provider 进入某个真实任务前需要回答：

- 对哪种 Task Class 经过验证？
- 在哪一版 Dataset / Policy / Model 上成立？
- 哪些安全和数据外发条件允许？
- 质量、延迟、成本是否满足当前阈值？

因此 `Available != Permitted != Qualified`。

### Formal Business Fact

即使 Qualified Provider 正常返回，结果通常仍只是 Candidate。机器结果是否成为 Evidence / Finding / WorkProduct 等正式业务事实，由对应 Domain Authority 决定；论文分数和 Provider success 都不能代替 Formal Admission。

## 典型 Traceability

| Research Problem / Artifact | 论文阶段解决什么 | 进入工程后新增问题 | Zuno 最自然承接 | Relation |
| --- | --- | --- | --- | --- |
| 多源证据链 / 裁判说理 | 证据与法律推理结构 | 材料版本、来源、正式采用、失效、历史可追溯 | 03 + 02 | DIRECT problem / CAPABILITY lineage |
| 事件 / 争议抽取 | 从案件材料识别专业结构 | 稳定语义、Provider 替换、适用范围 | 05 | CAPABILITY_LINEAGE |
| 法条推荐 | 从案件事实发现相关法律依据 | 版本、引用、资格、用户采纳 | 05 + 03 + 02 | CAPABILITY_LINEAGE |
| Fine-grained Fact–Article | 事实与法条之间的细粒度对应 | 真实材料版本、citation lifespan、formal acceptance | 03 + 02 | CAPABILITY / CONCEPTUAL |
| Legal LLM | 一个具体模型实现 | 模型版本、数据政策、成本、替换、任务资格 | 05 + 07 + 09 | PROVIDER / CAPABILITY |
| Legal benchmark | 衡量模型不同法律能力 | 产品 Task Class、真实 Dataset、release gate | 09 | CAPABILITY_LINEAGE |
| Functional testing for Legal AI | 暴露 headline metric 看不到的 failure | 持续 regression、failure taxonomy、release decision | 09 | CONCEPTUAL / CAPABILITY |
| Workflow / process research | 调度、协同、过程建模 | 长任务产品恢复与跨 Owner semantics | 04 | CONCEPTUAL only |

这张表只表示**研究—工程关系假设和已核验问题谱系**，不证明 Current Code 已经集成相应 Research Artifact。

## Research Artifact → Product 的工程断层

当 Research Artifact 被放进真实法律系统，论文里通常没有必要回答的问题会变成必须回答的系统责任：

1. **Input truth**：输入到底是哪一版材料？
2. **Readiness**：OCR / Chunk / Index / Graph 是否已经满足当前任务？
3. **Semantic stability**：新模型和旧模型是否真的履行同一个专业承诺？
4. **Qualification**：Benchmark PASS 是否适用于当前案件类型？
5. **Provenance**：结果基于什么材料、模型、Provider、参数和知识代际？
6. **Authority**：输出只是 Candidate，还是正式业务事实？
7. **Recovery**：Crash、late result、timeout 后怎样恢复？
8. **Security**：权限和外发策略变化以后还能否继续使用该数据/Provider？
9. **Evaluation**：复杂机制是否在真实 Task Class 上值得长期维护？

Zuno 的价值假设应围绕这些 Engineering Gap，而不是围绕“我们也有 Agent / Workflow / RAG”。

## Module lineage 使用规则

不是每个 Module 都必须有论文祖先。

- 02 / 03 / 05 / 09 可以有较强 Research-to-Engineering narrative；
- 04 可能更多是 Workflow / process 的 conceptual lineage + production engineering；
- 06 的 Effect semantics 主要来自分布式系统与真实外部动作约束；
- 08 很多要求来自 production security；
- 01 / 07 更多承担产品边界与 provider integration。

如果某模块主要是工程补足，直接这样写比强行引用论文更可信。

## Current / Target Gate

研究材料只能支持：

- 项目来源；
- 能力候选；
- 设计动机；
- Evaluation 方法；
- Build / Buy 假设。

要升级成 `Current`，必须回到代码、Migration、Test、Trace、Eval 或真实运行 Evidence。
