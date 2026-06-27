# Phase 05：记忆引擎

## 目标

成熟 Context / Memory Engine，但在测试证明前不改变产品声明。

## 范围

- Raw Event Log 追加和回放契约。
- L0 Working Context 与 L1 Recent Interaction Window 策略。
- 基于 Summary Compression 的 L2 Task Summary Memory。
- 基于 Structured Extraction 的 L3 Structured Long-term Memory 候选。
- summary 和 structured memory 保留 `source_event_ids`。
- ContextTrace 记录选择、淘汰和 token budget 决策。

## 不在范围内

- 数据库 schema 变化，除非后续获批 phase 明确打开。
- 产品级 memory UX。
- 把 External Knowledge 当成 Agent Memory。

## 退出标准

- `prepare_context` 可以消费 recent window、summary、structured memory candidates 和 evidence，同时不破坏单一 `GeneralAgent` 路径。
- post-turn memory commit 先保留 raw events，再生成 summary。
- 测试证明 Raw Event Log 没有被 summary memory 替代。
- 文档在代码证明后同步 Current / Foundation / Target 边界。

## 验证

- 聚焦 memory/context 测试。
- `python .agent/scripts/verify_agent_system.py`
- `python .agent/scripts/verify_doc_boundaries.py`
- `python tools/scripts/verify_repo_structure.py`
- `git diff --check`
