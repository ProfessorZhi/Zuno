# Zuno

Zuno 是一个本地优先、短小精悍但工程完整的 **Lean Complete Agentic GraphRAG Product**。

用户可以配置模型、创建 Workspace、上传资料、解析和索引文档，通过 AgentChat 使用标准检索或深度检索，由 Single Controller Agent 完成规划、混合检索、GraphRAG、证据整理、claim-level citation、回答生成、trace、成本统计和反馈。

## 当前定位

近期目标不是大规模分布式企业平台，而是一条真实可运行、可演示、可评测、可恢复的企业知识库 Agent 产品链路：

```text
配置模型
-> 创建 Workspace
-> 上传文档
-> Parse / Index
-> AgentChat 提问
-> ContextPack
-> RetrievalPlan
-> BM25 + Vector + optional Graph
-> EvidenceBundle
-> Claim-level Citation
-> Grounded Answer / Artifact
-> Trace / Cost / Eval
-> Feedback
-> Restart Recovery
```

## 架构入口

- [产品与运行架构总事实源](./docs/architecture/architecture.md)
- [架构十类图 HTML 展示](./docs/architecture/architecture.html)
- [Production readiness 状态](./docs/architecture/production-readiness.md)
- [文档摄取基础](./docs/architecture/document-ingestion-foundation.md)
- [Agent Core Runtime](./docs/architecture/agent-core-runtime.md)
- [Capability 与 Skill Layer](./docs/architecture/capability-and-skill-layer.md)
- [Agentic Retrieval Planner](./docs/architecture/agentic-retrieval-planner.md)
- [Eval、Observability 与 Cost](./docs/architecture/eval-observability-and-cost.md)
- [Input Layer 与 Document Processing](./docs/architecture/input-layer-and-document-processing.md)
- [Knowledge Space Product Configuration](./docs/architecture/knowledge-space-product-configuration.md)
- [文档入口](./docs/README.md)
- [公开证据入口](./docs/evidence/public-demo.md)
- [历史归档入口](./docs/history/programs/README.md)

## Program 入口

- 当前 program 前台：`.agent/programs/`
- 当前 active program：none
- 当前 phase：none
- 最近完成归档：`docs/history/programs/zuno-real-unified-runtime-cutover-v1/`
- 历史生产完成归档：`docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
- 历史 runtime-first 归档：`docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
- 历史 master architecture 归档：`docs/history/programs/zuno-master-architecture-implementation-v1/`

## 本地验证入口

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

## 六个运行域

1. Product & API
2. Input & Knowledge
3. Agent Core
4. Capability & Tool
5. Governance & Observability
6. Local Infrastructure

后端主路径位于 `src/backend/zuno`，按 Product/API、Agent、Memory、Capability、Knowledge 和 Platform owner 分层维护。

## 当前质量声明

Evidence-span Agentic GraphRAG 的本地实现基线已经存在，但 fixed EnterpriseRAG measured pass 仍未完成。

最近完成的 `zuno-unified-agent-runtime-closure-v1` 已把 unified runtime implementation baseline 归档为 `implementation_complete_measurement_blocked`。PHASE13 sample-8 运行产出 `blocked_not_measured`，原因是本地 embedding profile runner 未配置；sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。

```text
implementation available
measurement blocked
quality not yet proven
```

不得把 doc-level recall、prepared benchmark 或 incomplete run 写成 strict citation / answer correctness 已完成。Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。
