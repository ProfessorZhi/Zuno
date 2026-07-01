# PHASE05 Memory Context Engine

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE05_memory-context-engine
status: pending

## 目标

建设 Memory & Context Engine 的最小可运行 baseline：多重记忆、上下文压缩、ContextPack、敏感排除和 ReflexionLesson candidate review path。

## 范围

- Working、Session、Episodic、Semantic、Procedural、Reflexion、Governance memory。
- ContextPack builder：user goal、task state、selected memories、selected evidence、allowed capabilities、safety policy、output contract、budget。
- context compression summary。
- sensitive exclusion 与 memory write gate。
- ReflexionLesson candidate 进入 review path，不直接绕过治理写长期 memory。

## Context Compression 策略

Context compression 不是简单摘要。PHASE05 必须把上下文压缩定义成：

```text
Structured Extraction
+ Hierarchical Summary
+ Evidence-bound Summary
+ Budget-aware ContextPack Packing
```

### Structured Extraction

从历史消息、task event、tool result、retrieval evidence 和 artifact 中提取结构化字段：

- `user_goal`：用户当前目标与约束。
- `decisions`：已经确认的架构、产品、执行或安全决策。
- `constraints`：禁止范围、预算、权限、时间、输出格式。
- `entities`：workspace、knowledge space、document、artifact、tool、skill、person、project。
- `open_issues`：尚未解决的问题、阻塞点、需要澄清事项。
- `tool_results`：工具输出摘要、失败原因、retry / fallback 结果。
- `evidence_refs`：source event、document block、artifact、citation、trace span。
- `safety_notes`：敏感排除、DLP、权限、prompt injection、用户删除或保留规则。

### Hierarchical Summary

压缩结果必须分层，而不是一段无结构长摘要：

- `turn_summary`：本轮对话的目标、输入和直接输出。
- `task_summary`：当前 task 的计划、状态、已完成 step 和剩余 step。
- `session_summary`：当前会话中稳定有效的上下文和决策。
- `workspace_or_project_summary`：跨会话复用的项目级事实，但必须经过 governance。

### Evidence-bound Summary

摘要不能脱离证据：

- 每条 summary 尽量绑定 `source_event_id`、`artifact_id`、`evidence_id`、`trace_id` 或 `citation_ref`。
- 高风险结论必须有 `evidence_refs`；没有引用的结论只能作为 low-confidence context。
- 过期、冲突或被用户撤销的 memory 必须标记 `stale` / `conflict` / `revoked`，不得直接进入 ContextPack。

### Budget-aware Packing

ContextPack 按预算和风险顺序装载：

1. policy / safety notes。
2. user goal。
3. active plan and task state。
4. selected evidence。
5. selected memory。
6. tool and capability state。
7. output contract。

如果预算不足，先裁剪低置信 memory，再裁剪长摘要；不得裁剪 safety policy、active user goal 或 required evidence。

## 目标架构拼接点

本 phase 拼到 Agent Core 的 Memory & Context Engine。它解决的不是“存聊天历史”，而是每次 Agent 执行前构造可控上下文：

- Working / Session memory 给当前任务提供短期状态。
- Episodic / Semantic / Procedural memory 给任务提供长期经验、事实和流程。
- Reflexion memory 保存失败教训的候选和复用条件。
- Governance memory 保存授权、删除、敏感排除和审计边界。
- ContextPack 是 Planning & Control Runtime 的输入，不允许 Planning 直接抓取任意 raw history。

本 phase 的输出必须能被 PHASE09 Strategy Selector 和 PHASE10 Reflexion runtime 消费。

## 并行开发可行性

本 phase 可由 Workstream C 独立推进，适合与 Workstream D/E/G 并行，但依赖 PHASE02 的 ContextPack / ReflexionLesson contract。

可并行：

- ContextPack builder 与 memory selection reason 可并行。
- Sensitive exclusion 可由 Security workstream review。
- Reflexion candidate review path 可和 Planning workstream 约定接口。

不可并行：

- 不得让 Planning 直接依赖 Memory 内部 store。
- 不得让 memory writer 绕过 governance。
- 不得在本 phase 接入生产级外部 memory DB 作为测试依赖。

## 详细执行卡

- 输入依赖：PHASE02 ContextPack / memory contract、现有 GeneralAgent context tests、security sensitivity contract。
- 主要交付物：Working / Session / Episodic / Semantic / Procedural / Reflexion / Governance memory contract，ContextPack builder，structured extraction，hierarchical summary，evidence-bound summary，budget-aware packing，sensitive exclusion，memory write gate。
- 可并行工作包：ContextPack builder、memory type contract、compression policy、ReflexionLesson review path 可拆；长期向量 memory backend 不在本 phase 实现。
- Coordinator 锁点：进入 model prompt 的 ContextPack 字段、sensitive exclusion policy、post_turn_commit 写入边界。
- 下游交接：PHASE09 planner 消费 ContextPack；PHASE10 Reflexion candidate 进入 memory review path；PHASE13 记录 memory_read / memory_write_candidate trace。
- PR / commit 建议：`feat(memory): add context pack engine baseline` 与 `test(memory): cover compression and sensitive exclusion`。

## 禁止范围

- 不要求生产级 vector memory DB。
- 不把敏感文档内容默认写入长期 memory。
- 不绕过 security gate 向 context 注入 memory。

## 验收闸门

- ContextPack builder focused test 通过。
- 上下文过长时 compression test 通过，输出必须同时包含 structured fields 和 hierarchical summary。
- evidence-bound summary test 通过，高风险 summary 必须绑定 source event / artifact / evidence id。
- stale / conflict memory 不进入 ContextPack，且 exclusion reason 可追溯。
- sensitive memory exclusion test 通过。
- sensitive exclusion 后仍保留 reason，不把敏感原文写入 prompt。
- ReflexionLesson candidate review path test 通过，candidate 不直接进入 long-term memory。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
pytest -q tests/memory -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/memory/**`
- `src/backend/zuno/agent/context.py`
- `src/backend/zuno/agent/**`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/memory/**`

## 需要修改的文件

- `src/backend/zuno/memory/**`
- `src/backend/zuno/agent/context.py` or equivalent context builder
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/memory/**`

## 执行拆解

1. 写 ContextPack focused test。
2. 写 compression / selection reason test。
3. 写 sensitive exclusion test。
4. 写 ReflexionLesson candidate review path test。
5. 实现 local in-process baseline。
6. 确认 Planning phase 可消费 ContextPack contract。

## 多 agent 分工

- Workstream C owner。
- Workstream F 只消费 ContextPack contract。
- Workstream E 只审查 sensitive exclusion policy。

## 需要返回的证据

- ContextPack 示例。
- memory selection reason。
- sensitive exclusion evidence。
- ReflexionLesson candidate review evidence。

## 停止条件

- ContextPack 需要大改 Agent public API。
- memory write 会泄露敏感文档内容。
- Reflexion lesson 会绕过 governance 直接进入长期 memory。
