# Architecture Plans

这个目录只放“怎么推进”的文档，不放稳定架构定义。
如果你想理解当前架构本身，优先看 `../specs/`。只有当你想知道“下一个阶段先做什么、按什么顺序推进”时，再看这里。

## 当前仍然有效的计划文档

- [Zuno Refactor Execution Plan](./zuno-refactor-execution-plan.md)
  当前以新的 `Phase 1-7` 线性体系为准。新的串行记账现已真实完成 `Phase 1`，默认串行进入 `Phase 2`。
- [Current Phase Audit](./current-phase-audit.md)
  当前阶段判断的稳定入口。这里不重复写长期架构 spec，只负责说明“现在在哪个 phase、为什么这样判断、下一步默认做什么”。
- [Retrieval Governance Upgrade Plan](./retrieval-governance-upgrade-plan.md)
- [RAG Local Eval Scheme](./rag-local-eval-scheme.md)
- [Phase 6 Bundle Prestage](./phase6-bundle-prestage.md)
- [Phase 6 Bundle Ready](./phase6-bundle-ready.md)
- [Phase 7 Final Prestage](./phase7-final-prestage.md)
- [Phase 7 Final Ready](./phase7-final-ready.md)

## 当前推进原则

这里的计划文档默认遵守四条规则：

1. phase 判断必须对应真实代码和文档状态。
2. phase 与 phase 之间线性推进，单个 phase 内部任务可以并行。
3. 每个 phase 完成后都要先做一次简化验证，再形成一次清晰的 GitHub 节点。
4. 每次大更新后都要回看 `docs/architecture/`，删除已解决问题，更新当前阶段判断。

## 当前阶段主线

后续默认按这条顺序推进：

1. `Phase 1` 运行时收口与可运行恢复
2. `Phase 2` 项目文件夹与结构硬治理
3. `Phase 3` 文档与展示面硬收口
4. `Phase 4` 分层架构与运行时边界强化
5. `Phase 5` LangGraph + GraphRAG 主线深化
6. `Phase 6` 评测与证据链固化
7. `Phase 7` 面试前总收口
