# Zuno 目标运行时 V2 实施路线图

## 目标

在已经完成的 target architecture migration closure 之后，用小步、可验证的 phase 落地目标运行时架构。

本程序必须保持以下边界：

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

Phase 00-04 的详细文件和证据已归档到：

- `docs/history/programs/zuno-target-runtime-v2/`

## 后续执行 Phase

### Phase 05：记忆引擎

目标：成熟 Context / Memory Engine，但在测试证明前不改变产品声明。

范围：

- Raw Event Log 追加和回放契约。
- L0 Working Context 与 L1 Recent Interaction Window 策略。
- 基于 Summary Compression 的 L2 Task Summary Memory。
- 基于 Structured Extraction 的 L3 Structured Long-term Memory 候选。
- summary 和 structured memory 保留 `source_event_ids`。
- ContextTrace 记录选择、淘汰和 token budget 决策。

不在范围内：

- 数据库 schema 变化，除非后续获批 phase 明确打开。
- 产品级 memory UX。
- 把 External Knowledge 当成 Agent Memory。

退出标准：

- `prepare_context` 可以消费 recent window、summary、structured memory candidates 和 evidence，同时不破坏单一 `GeneralAgent` 路径。
- post-turn memory commit 先保留 raw events，再生成 summary。
- 测试证明 Raw Event Log 没有被 summary memory 替代。
- 文档在代码证明后同步 Current / Foundation / Target 边界。

验证：

- 聚焦 memory/context 测试。
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `python tools/scripts/verify_repo_structure.py`
- `git diff --check`

### Phase 06：能力与工具检索

目标：引入可检索 ToolCard 层，减少一次性注入所有工具 schema 的做法。

范围：

- ToolCard registry contract。
- Knowledge、Action Tool、MCP、Skill 的统一 capability metadata。
- capability selector 基于 task/context 做 keyword、permission、health、cost 过滤。
- GeneralAgent trace 记录 requested / selected / rejected capabilities。

不在范围内：

- 新建 MCP server。
- 新增外部工具市场。
- 自动安装用户未授权工具。

退出标准：

- Agent 可以按需选择 capability，而不是默认加载全部工具 schema。
- 工具选择结果进入 trace。
- 权限、健康状态和成本过滤有测试覆盖。

验证：

- 聚焦 capability registry / selector 测试。
- 受影响 Agent runtime 测试。
- Agent/doc 边界验证。

### Phase 07：知识检索与融合

目标：围绕现有 KnowledgeQueryService 和 GraphRAGQueryService 落地目标检索融合路径。

范围：

- query method requested / resolved trace。
- Basic、Local、Global、DRIFT 路由边界。
- Native BM25、dense vector、graph local、community global 的候选融合。
- RRF、dedup、optional rerank、evidence check、citation coverage。
- GraphRAGProjectSnapshot 继续是内部查询配置，不变成 Agent memory。

不在范围内：

- 重新引入 Domain Pack 作为主线。
- 新建第二套聊天 runtime。
- 大规模重新跑正式 eval，除非该 phase 明确要求。

退出标准：

- query method resolution 可追踪。
- GraphRAG 是被选择的 Knowledge Capability，不是第二套聊天运行时。
- evidence bundle、citation coverage、index/community/prompt versions 进入 trace。

验证：

- 聚焦 retrieval/fusion 测试。
- 需要时运行 stackless 或 eval smoke。
- 文档边界验证。

### Phase 08：GeneralAgent LangGraph 运行时

目标：显式化 runtime graph，同时保持单一 `GeneralAgent` 聊天主线。

范围：

- `prepare_context -> agent_loop -> post_turn_commit` 的显式状态图。
- checkpoint、interrupt、resume、stream 兼容性。
- LangChain message / model / tool / structured output 抽象继续通过 Agent runtime 进入。
- LangGraph 管状态循环，不负责业务知识检索策略。

不在范围内：

- 默认多 Agent supervisor。
- 第二套 GraphRAG chat runtime。
- 产品级自动任务编排。

退出标准：

- 单次聊天路径只进入一个 GeneralAgent runtime。
- state、checkpoint、interrupt、resume、stream 有聚焦测试。
- Context/Memory、Capability、Knowledge trace 在 runtime graph 内可见。

验证：

- 聚焦 GeneralAgent runtime 测试。
- 受影响 API/SSE 测试。
- Agent/doc 边界验证。

### Phase 09：产品边界、Trace 与 Eval 收口

目标：用用户可理解的产品边界、trace evidence 和文档归档关闭 V2 实施。

范围：

- API 和前端展示 memory/capability/evidence 状态的边界。
- trace JSONL 字段完整性。
- eval baseline 是否需要更新由 evidence gate 决定。
- 前台文档只保留 Current、Target、Roadmap、Evidence、Terminology。
- 旧计划、旧 evidence、截图和临时产物归档或排除出前台。

不在范围内：

- 完整前端重设计。
- 生产级动态 capability 市场。
- 把 Future 方向提升为 Current。

退出标准：

- 产品/API 文档明确区分 Current、Foundation、Target、Future 和 History。
- `.agent/` 保持精简：可执行 workflow、target design、references、scripts、templates 和归档指针。
- `docs/` 保持精简：正式文档、证据、术语和 history index。
- 完成 trace/eval closure evidence。

验证：

- 完整 Agent/doc/repo hygiene 验证。
- 受影响 API/frontend contract 测试。
- 必要时运行 eval closure 命令。

## 停止条件

- 不要跳过 phase。
- 不要在未授权 phase 修改 runtime、frontend、Docker、DB、eval runner 或依赖。
- 不要恢复 root `domain-packs/`、Domain Pack frontend pages 或旧 DomainQAGraph。
- 不要在代码和测试证明前把 Target 写成 Current。

## 参考

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
- `.agent/programs/zuno-target-runtime-v2/current-phase.md`
- `.agent/programs/zuno-target-runtime-v2/closure-checklist.md`

完成证据移动到 history；active program 文档保持小而清晰。
