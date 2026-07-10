# Knowledge Space Product Configuration

所属运行域：Product & API、Input & Knowledge、Local Infrastructure。

## 定位

Knowledge Space 是用户选择知识库、模型 slot、检索 profile 和解析/index 配置的产品边界。它不是前端 filter，而是后端可恢复、可 trace、可用于 benchmark 的配置事实源。

## 配置对象

- ModelDefinition、ModelSlotBinding。
- KnowledgeSpace、WorkspaceFile。
- RetrievalProfile：top-k、candidate pool、RRF weights、rerank weights、citation threshold。
- ChunkingProfile：chunk size、chunk overlap、parent context size。
- ParserProfile：parser provider、PDF/text support、blocked reason policy。
- EvalProfile：benchmark case set、release thresholds。

## 优先级

```text
DB workspace binding
> environment secret/reference
> YAML default
> test fixture default
```

运行时必须把最终生效配置写入 trace 或 eval report。workspace override 只允许通过后端 DTO 和 policy validation。

## 当前与短期目标

Current：

- model/tool/knowledge DTO、config files、database models 和 retrieval services 已存在。
- 部分参数仍需要从业务流程中抽出，统一进入配置事实源。

Short-term：

- P0 model provider/name/base URL/model slot 统一进入 Model Runtime / Gateway。
- P1 retrieval、chunking、citation threshold、trace retention 和 release thresholds 可复现记录。

Future Optional：

- enterprise policy admin。
- remote config service。
- multi-tenant config inheritance。
