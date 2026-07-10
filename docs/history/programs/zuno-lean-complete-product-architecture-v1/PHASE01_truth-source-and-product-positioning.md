# PHASE01 truth-source-and-product-positioning

status: completed
program: zuno-lean-complete-product-architecture-v1

## 目标

打开 active program，并固定本轮架构重写的真实边界：

- 收缩近期目标规模，不降低架构文档精度。
- `architecture.md` 保持详细、规范、可实施，是后续 Program / Phase 拆分的事实源。
- `architecture.html` 收缩为四张展示图，不复制 Markdown 全部技术细节。
- 不修改核心 runtime。

## 旧问题

- 前台架构被 4+1 / View & Beyond 十图组织方式主导。
- 11 层和 Production Scale 叙事过重，干扰短期可闭环产品目标。
- renderer、verifier 和 tests 把十图结构写成硬约束。
- 历史 program 和未来企业平台能力容易被误读为 Current。

## 新定位

```text
Zuno = Lean Complete Agentic GraphRAG Product
```

本轮以一条真实产品链路作为主叙事：

```text
Model Configuration
-> Workspace
-> Source Object
-> Parse Job
-> Document IR
-> Block / Citation Chunk
-> Index Manifest
-> BM25 / Vector / Graph Index
-> AgentChat Request
-> ContextPack
-> Strategy Selection
-> RetrievalPlan
-> Hybrid Retrieval
-> Graph Expansion
-> Fusion / Rerank
-> EvidenceBundle
-> Claim Extraction
-> Citation Binding
-> Grounded Synthesis
-> Reflection / Replan
-> Final Answer / Artifact
-> Trace / Eval / Cost
-> Feedback
-> Post-turn Memory Commit
```

## 六个运行域

1. Product & API
2. Input & Knowledge
3. Agent Core
4. Capability & Tool
5. Governance & Observability
6. Local Infrastructure

## 四张展示图

1. Lean System Overview
2. Golden Path Runtime
3. Agentic GraphRAG and Agent Loop
4. Local Deployment and State

## PHASE01 验收

- [x] active program 已打开。
- [x] roadmap 和 closure checklist 已记录新边界。
- [x] 不把收缩误写成删除实施细节。
- [x] 未修改 runtime。
