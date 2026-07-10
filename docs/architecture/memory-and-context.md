# Memory and Context Engineering

所属运行域：Agent Core Runtime Domain、Governance & Observability。

## 定位

Memory 是 Agent 的任务状态、用户事实、历史经验和程序经验，不是企业知识库的复制品。Knowledge 负责企业文档和 evidence source；Memory 可以引用 Knowledge 的 citation/evidence id，但不能把整个知识库搬进长期记忆。

ContextPack 是 Memory、Knowledge、Tool observation、PlanState 和输出约束的预算化读取视图，不是第五层 Memory。换成英文 contract 说法：ContextPack read view, not another memory layer。

## 四层 Memory

| 层级 | 定义 | 典型内容 | 生命周期 | 读取方式 |
| --- | --- | --- | --- | --- |
| Sensory Memory | 当前 Agent run 可感知的原始输入和 Observation | 当前用户输入、上传引用、raw tool observation、当前检索 observation | turn/task | 即时读取，任务结束后归档或丢弃 |
| Short-term Memory | 当前任务和会话工作台 | working memory、recent message window、PlanState、step observations、task summary、checkpoint state | task/session | 每一步直接读取或从 checkpoint 恢复 |
| Long-term Memory | 跨任务可检索经验与知识 | Episodic、Semantic、Procedural、approved Reflexion lessons | durable | 语义/混合检索，受 review 和 scope 控制 |
| Entity Memory | 结构化实体和关系事实 | 用户偏好、项目/workspace facts、named entities、relationships、effective time | durable | 精确查询或图查询，必须支持 supersede/privacy delete |

Long-term Memory 内部类型：

- Episodic Memory：一次完整任务经历、时间、上下文、结果和失败。
- Semantic Memory：稳定事实、规律和从多次经历提炼的知识。
- Procedural Memory：SOP、策略偏好、approved Reflexion lesson 和可复用做法。

## 边界

```text
Input != Sensory Memory
Knowledge != Long-term Agent Memory
ContextPack != 第五层 Memory
```

- Input 层负责 `upload -> parse -> Document IR -> index` 的文档生命周期。
- Sensory Memory 只保存当前 turn/task 可感知的输入和 Observation。
- Knowledge 是企业资料与证据事实源。
- Memory 是用户、任务、经验、偏好、程序知识和跨任务学习。

## 生命周期

```text
capture
-> classify
-> redact
-> extract
-> importance score
-> deduplicate
-> conflict check
-> candidate
-> governance review
-> store
-> retrieve
-> rank
-> ContextPack
-> use trace
-> decay / consolidate / supersede / revoke / delete
```

Memory 写入不能直接把原始模型思考链、完整工具日志或敏感 payload 推入长期记忆。Reflexion lesson 必须先进入 candidate/review，再按 sensitivity、scope、quality 和 applicability 决定是否进入 Episodic/Procedural Memory。

## Memory 类型矩阵

| 类型 | 写入来源 | 读取时机 | 存储方式 | 治理 | 生命周期 |
| --- | --- | --- | --- | --- | --- |
| Sensory | 当前输入、Tool/检索结果 | 当前 step | graph/task state | redaction | turn/task |
| Working | Agent execution state | 每一步 | checkpoint | token budget | task |
| Session | messages、task events | context build | SQLite/event log | retention policy | session |
| Episodic | 完整任务经历 | 相似任务 | searchable store | review | decay/consolidate |
| Semantic | 稳定事实和规律 | task start/context build | structured + vector | conflict/revoke | durable |
| Procedural | SOP、Reflexion lesson | strategy/planning | searchable store | approval | durable/decay |
| Entity | 用户、项目和关系事实 | context build/精确查询 | relational/graph | effective time/privacy delete | durable |

## 主动检索与按需检索

Task start 主动检索：

- user preferences；
- workspace/project facts；
- approved procedural memory；
- 与当前任务类型相似的 high-confidence lesson。

During execution 按需检索：

- Replan 或 Reflection 要求额外经验；
- Tool failure 与历史失败相似；
- 用户提到已知项目/实体；
- ContextPack 预算允许补充 episodic/semantic memory。

每次 Memory retrieval 必须记录 query、scope、candidate score、selected/excluded reason、token cost、freshness、sensitivity 和最终 ContextPack position。

## ContextPack 装配顺序

```text
1. system/security policy
2. current user goal
3. current PlanState and critical observations
4. entity facts and user/workspace preferences
5. approved procedural memory
6. recent session window / task summary
7. selected Knowledge evidence
8. normalized tool observations
9. output contract and remaining budget
```

ContextItem contract：

```yaml
context_item:
  item_id: string
  source_type: policy | request | plan | memory | knowledge | tool
  source_ref: string
  content_ref: string
  priority: int
  token_cost: int
  sensitivity: string
  freshness: string
  included_reason: string
  excluded_reason: string | null
```

## Context 压缩

按顺序使用：

1. sliding window；
2. task summary；
3. tool result normalization；
4. evidence deduplication；
5. 大 payload 写入 object store，仅保留引用；
6. 低频但重要内容卸载到长期 Memory；
7. 重新检索而不是永久塞入 context。

## Consolidation 与删除

- 轻量 consolidation：每个任务后去重、更新、冲突检查。
- 深度 consolidation：周期性 Episodic -> Semantic 抽象提炼。
- 新事实覆盖旧事实时保留版本、`effective_from` 和 `effective_to`。
- Privacy delete 必须删除或失效所有相关索引和派生项。
- Reflexion lesson 必须可撤销、衰减和重新评估。

## 当前与短期目标

Current：

- `MemoryEngine`、raw event、task summary、candidate extraction、review、decay、consolidation、semantic search、privacy delete、ContextPack rendering 和 Reflexion candidate baseline 已存在。
- GeneralAgent 已有 MemoryEngine/ContextPack 接入点和相关 focused tests。
- PHASE10 已把 MemoryEngine 接入 unified runtime：`build_context` 在注入 `memory_engine` 时执行 pre-turn memory read，ContextPack 记录 selected memory refs、include/exclude trace 和 `memory_influenced_strategy`；`post_turn_commit` 写 raw event / task summary，并在 abstain/failed/blocked 路径生成 pending Reflexion candidate。
- Approved procedural / Reflexion memory 已能影响后续 Strategy/Planning：`RuntimeStrategySelector` 会在 reason 和 trace 中记录 `memory_influenced_strategy`。
- Reflexion candidate metadata 显式记录 `hidden_cot: False`，pending candidate 不进入未来 ContextPack。
- `EntityMemoryStore` 已提供本地 scope + entity + attribute authoritative key 和 supersede trace baseline。

Partial / closure gap：

- Completion / Workspace / SSE / UI 产品链路尚未切换到 unified runtime，属于 PHASE11。
- Entity Memory 的跨索引 privacy delete 和生产级关系查询仍是目标 contract。
- fixed paired benchmark 未 measured，Memory reuse 不能写成线上质量提升已证明。

Short-term：

- P1 四层 Memory 和 ContextPack 在 AgentChat trace 中可观测。
- P1 Reflexion lesson candidate 带 evidence/source trace 进入 review。
- P1 approved procedural memory 能影响后续 Strategy/Planning。

## 质量指标

- retrieval relevance；
- precision@k；
- useful memory rate；
- stale/conflict rate；
- privacy leak rate；
- promotion acceptance rate；
- Reflexion reuse rate；
- repeated failure reduction；
- ContextPack token efficiency。
