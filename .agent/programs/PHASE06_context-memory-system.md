# PHASE06 Context Memory System

status: active

## 目标

落地 Context / Memory 的 write-manage-read 子系统，让 Agent 不只是读当前对话，而能有可治理的短期、摘要和结构化长期记忆。

## 步骤

- [ ] 定义 Raw Event Log、Working Context、Recent Window、Task Summary、Structured Long-term Memory、Graph Memory candidate。
- [ ] 扩展为九类 memory taxonomy：Raw Event Log、Working Memory、Recent Window、Task Summary、Episodic Memory、Semantic Memory、Procedural Memory、Graph Memory Candidate、Model Context Pack。
- [ ] 定义 Context Pack renderer 和 budget policy。
- [ ] 定义 Memory API：`append_event`、`build_recent_window`、`summarize_task`、`extract_memory_candidates`、`review_memory_candidate`、`retrieve_memory`、`render_context_pack`。
- [ ] 定义 storage mapping：哪些只进 trace/event log，哪些能进入 searchable store，哪些能进入下一轮 context。
- [ ] 定义 post-turn extraction、dedupe/conflict、review、promotion、decay、discard。
- [ ] 增加敏感信息过滤和 memory eval。
- [ ] 写 memory layer tests。

## 输入 / 输出文件

输入：

- `src/backend/zuno/memory/**`
- `src/backend/zuno/agent/**`
- `src/backend/zuno/platform/**` 中现有 event / storage / trace foundation。

输出：

- memory taxonomy contract。
- context pack renderer。
- post-turn memory write path。
- promotion / decay / discard policy。
- memory eval fixtures。

## 依赖与阻塞

- 依赖 PHASE05 runtime state；memory write path 必须绑定 `trace_id` / `task_id`。
- 依赖 PHASE09 的 sensitivity / redaction policy；敏感候选不能默认进入长期记忆。
- PHASE10 eval 必须能区分 memory read span 与 memory write span。

## Memory Eval 要求

- relevance：检索出的记忆与当前 task 是否相关。
- over-retention：临时或低置信内容是否被错误长期保存。
- redaction：PII / 商业机密是否在进入 Context Pack 前处理。
- stale suppression：过期记忆是否被降权或排除。
- conflict detection：新候选与已有记忆冲突时是否进入 review。

## 验收

- Memory read path 和 write path 清晰分离。
- 可证明哪些内容会进入下一轮 context，哪些只是 trace。
- 生产级 Memory DB 未完成前不写成 Current。
- 只有 memory tests 和敏感信息回归测试通过后，才允许把具体 memory 能力写入 Current。

## 验证

```powershell
pytest -q tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_context_orchestrator.py -p no:cacheprovider
```
