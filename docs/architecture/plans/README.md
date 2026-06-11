# Architecture Plans

这个目录只放“怎么推进”，不放稳定架构定义。
如果你要理解当前架构本身，优先看 `../specs/`。

## 当前有效的主计划入口

当前真正应该优先阅读的计划文档只有两份：

- [Zuno Refactor Execution Plan](./zuno-refactor-execution-plan.md)
  这是新的 `Phase 1-7` 串行执行真相来源。
- [Current Phase Audit](./current-phase-audit.md)
  这是当前仓库状态的最小阶段判断入口。

## 仍然保留，但不属于当前主阅读路径的计划文档

下面这些文档可以保留作为后续专题计划或未来阶段预备材料，但它们不应覆盖当前 phase 状态判断：

- [Retrieval Governance Upgrade Plan](./retrieval-governance-upgrade-plan.md)
- [RAG Local Eval Scheme](./rag-local-eval-scheme.md)
- [Phase 6 Bundle Prestage](./phase6-bundle-prestage.md)
- [Phase 6 Bundle Ready](./phase6-bundle-ready.md)
- [Phase 7 Final Prestage](./phase7-final-prestage.md)
- [Phase 7 Final Ready](./phase7-final-ready.md)

## 当前推进原则

1. phase 判断必须对应真实仓库状态
2. phase 与 phase 之间严格串行
3. 单个 phase 内任务可以并行，但必须统一验收
4. 每个 phase 结束后都要先跑最小测试，再同步 README 和 `docs/architecture/`
5. 每个 phase 都要形成独立 GitHub 节点，再并回 `main`

## 当前默认顺序

1. `Phase 1` 运行时收口与可运行恢复
2. `Phase 2` 项目文件夹与结构硬治理
3. `Phase 3` 文档与展示面硬收口
4. `Phase 4` 分层架构与运行时边界强化
5. `Phase 5` LangGraph + GraphRAG 主线深化
6. `Phase 6` 评测与证据链固化
7. `Phase 7` 面试前总收口
