# Zuno 目标运行时 V2 执行计划

## 目标

在已经完成的 target architecture migration closure 之后，用小步、可验证的 phase 落地目标运行时架构。

本目录就是当前执行计划包。所有 phase 文件平铺在 `.agent/programs/`，不再嵌套到 program 子目录。

## 边界

- Current：代码和测试已经证明的当前事实。
- Foundation：已有最小可调用切片，但产品行为还不成熟。
- Target：下一阶段要实现的架构。
- Future：本程序之外的未来方向。
- History：已经归档的证据和被替换计划。

## 已完成基础切片

| Phase | 状态 | 结果 |
| --- | --- | --- |
| 00 | Complete | 写入前重新验证当前状态。 |
| 01 | Complete | 打开当前可执行程序并更新指针。 |
| 02 | Complete | 增加模块边界审计和迁移闸门。 |
| 03 | Complete | 完成第一个低风险后端边界移动。 |
| 04 | Complete | 增加最小可调用 Context Orchestrator runtime。 |

Phase 00-04 的详细文件和证据已归档到 `docs/history/programs/zuno-target-runtime-v2/`。

## 后续执行 Phase

1. [Phase 05：记忆引擎](phase-05-memory-engine.md)
2. [Phase 06：能力与工具检索](phase-06-capability-tool-retrieval.md)
3. [Phase 07：GraphRAG LLM 实体抽取与知识检索融合](phase-07-graphrag-llm-entity-extraction.md)
4. [Phase 08：GeneralAgent LangGraph 运行时](phase-08-langgraph-runtime.md)
5. [Phase 09：产品边界、Trace 与 Eval 收口](phase-09-product-trace-eval-closure.md)

## 停止条件

- 不要跳过 phase。
- 不要在未授权 phase 修改 runtime、frontend、Docker、DB、eval runner 或依赖。
- 不要恢复 root `domain-packs/`、Domain Pack frontend pages 或旧 DomainQAGraph。
- 不要在代码和测试证明前把 Target 写成 Current。
- 如果执行计划被替换，旧计划从 `.agent/programs/` 当前前台移除；需要保留的证据归档到 `docs/history/programs/`。

## 参考

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- [closure-checklist.md](closure-checklist.md)
