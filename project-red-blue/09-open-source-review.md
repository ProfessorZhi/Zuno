# 开源与现成方案评估

## 目的

本文件防止“自研”成为没有比较的默认答案。每个能力都必须在 Adopt、Extend、Build、Defer 四种选择之间比较；本文件当前只建立评估入口，不预先宣布竞品结论。

## 四种选择

| 选择 | 含义 |
|---|---|
| `ADOPT` | 直接采用并围绕它集成 |
| `EXTEND` | 采用基础能力，补齐 Zuno 的差异部分 |
| `BUILD` | 现有方案无法满足关键 Contract，自己实现 |
| `DEFER` | 当前用户价值或证据不足，暂不做 |

## 待评估矩阵

| 能力 | 候选 | 当前状态 |
|---|---|---|
| Memory backend | OpenViking / Mem0 / Graphiti / Cognee | `TO_REVIEW` |
| Agent workflow | LangGraph / Dify / 自建 | `TO_REVIEW` |
| GraphRAG | Microsoft GraphRAG / LightRAG / LlamaIndex / 自建 | `TO_REVIEW` |
| Retrieval | OpenSearch / Milvus / pgvector / 自建 | `TO_REVIEW` |

## 固定问题

1. 现成方案解决了哪个明确问题？
2. 它的权限、版本、数据隔离、可观测性和失败语义是否满足 Contract？
3. 如果扩展，真正的 Delta 是什么，维护边界由谁负责？
4. 迁移、升级、许可证、供应商锁定和数据出口成本是什么？
5. 今天从零开始，仍会 Build 吗？如果会，为什么；如果不会，应该采用什么？
6. 当前规模和团队是否值得承担自研成本？

任何“比 WorkBuddy 强”“开源方案不适合企业”等结论都必须进入待验证状态，不能用品牌印象替代技术和业务证据。
