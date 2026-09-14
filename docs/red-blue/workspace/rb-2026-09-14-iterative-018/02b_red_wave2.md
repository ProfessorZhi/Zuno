# Red Wave 2 — rb-2026-09-14-iterative-018

mode: BATCH_WAVES
input_blue_wave1_commit: 14faf4c3061e43bebbec788c7766fde0e7f33c15
question_count: 28

这一波只攻击 Blue Wave 1 自己暴露的薄弱点，不按原 Pressure Suite 顺序补题。

## Tool / routing

### R2-Q001
你说 per-user config lookup 存在，但并发隔离没证明。假设 `GeneralAgent` 实例被两个用户复用，middleware 里的 `user_id` 到底从哪来？如果它是实例字段，你前面的说法还能成立吗？

### R2-Q002
你说 call-time 现查配置会产生长任务配置漂移。你要加 version pin 的话，version 由谁创建、存在哪里、一次 Tool retry 用旧版本还是新版本？

### R2-Q003
两个 MCP Server 暴露同名 Tool，你提出 canonical tool id 要带 server identity。这个 id 进入 LLM schema 后怎么保持可读？display name、routing id、audit id 你会不会拆开？

### R2-Q004
你承认 direct route 可能绕过 Agent policy。那你会把 authorization/config/audit gate 放在 route 之前，还是 Tool execution 之前？为什么？

### R2-Q005
如果 direct route 和 ReAct 最后都调用同一个 Tool，怎样设计才能保证两条路径不各自复制一套安全检查？

### R2-Q006
你说没有完整 ReAct hard max。假设 Tool 连续返回可重试错误，模型每轮都继续调用，谁拥有停止权？停止条件应该属于 Agent prompt、Runtime budget 还是 Tool middleware？

## GraphRAG

### R2-Q007
`GRAPH_PROMOTION_THRESHOLD=6` 是 heuristic。你现在要证明这个 6 不是拍脑袋，最小需要做什么实验？

### R2-Q008
如果 threshold 从 6 调到 4，Recall 上升但 baseline gold 被挤出的概率也上升，你会用什么 objective / constraint 选点？

### R2-Q009
你承认没有 explicit final tie-break。检索结果在相同输入下因为输入顺序变化而抖动，会影响哪几层：eval、cache、citation、debug？你先修哪一个？

### R2-Q010
你说 alias normalization 可能把不同实体误合并。法律场景里两个同名当事人、同名公司、同名法规版本怎么区分？只加 entity type 够不够？

### R2-Q011
如果你把 stable entity id 引进来，实体 ID 是 ingestion 时生成还是 retrieval 时 resolve？知识更新和 merge/split 后旧 ID 怎么处理？

### R2-Q012
你说 graph update → cache/version invalidation 没闭环。一个查询拿到旧 graph path，但新 DocumentVersion 已经生效时，谁应该拒绝这个结果？

### R2-Q013
正式 GraphRAG benchmark 你会怎么分 query class？至少给出 baseline、主要质量指标、latency/cost gate 和 kill condition。

### R2-Q014
你前面说 p95 约 26.6s 对 19.0s，但样本只有 5 条。这个数字在面试里到底该不该主动讲？怎样讲才不误导？

## Context / Memory

### R2-Q015
`MemoryScope` 的 project/thread 都是 optional。调用方漏填时 scope 变宽，这不是类型系统能挡住的。你会在什么层把“哪些字段必须存在”变成 policy？

### R2-Q016
task summary 和 approved structured memory 冲突，你说不能靠 priority 决定真值。那谁有 authority 做仲裁？如果两者都只是上下文材料，模型该看到两个还是只看到一个？

### R2-Q017
你说 InMemory store 没 durable concurrency 语义。如果切 PostgreSQL，你会给 dedupe_key 加什么约束？scope 要不要进入 unique key？

### R2-Q018
两个事务同时从同一组 RawMemoryEvent 生成不同 summary，unique constraint 只能防完全重复，不能决定哪个 summary 正确。你怎么收敛？

### R2-Q019
APPROVED read gate 有 TOCTOU。你提 version/epoch，那 ContextPacket 需要绑定什么版本？在模型调用前谁再验证一次？

### R2-Q020
代码允许直接构造 `review_status=APPROVED` 的 candidate。你要把 approval authority 收紧，最小要改 contract、store 还是 service boundary？

### R2-Q021
用户要求删除一条 Memory，但它已经进入当前 ContextPacket。你的语义是本轮继续执行、立即取消、还是标 stale 后阻止后续副作用？谁做这个决定？

## Agent topology / architecture

### R2-Q022
你说优先 Tool，再 Subgraph，再 Specialist Agent。给一个明确判据：什么时候“独立 context/tool policy”足以让 Subgraph 升级为 Agent？

### R2-Q023
假设法律任务拆成检索 Agent、事实审查 Agent、文书 Agent。三者都发现需要修改案件状态，谁能写正式 Domain state？

### R2-Q024
Supervisor + Specialist 里 Specialist 返回晚到结果，而 Supervisor 已经 replan 到新版本。这个 late result 是丢弃、存档还是重新评估？你靠什么版本关系判断？

### R2-Q025
如果 Specialist 自己有 Memory，它和全局 Memory 的边界是什么？同一个事实被两个 Specialist 各自记住，谁负责 dedupe 和撤销？

### R2-Q026
Single logical controller + parallel workers 是你提的中间方案。它相对真正 Multi-Agent 多了什么能力，少了什么能力？为什么不直接一直停在这里？

### R2-Q027
你要证明 Persistent Multi-Agent 值得存在，会拿什么 baseline 对比？“回答质量更高”不够，至少还要看哪些系统指标？

### R2-Q028
如果最终 benchmark 发现 Generic Host + Zuno Backend 在质量、成本和恢复上都不差于自研 Multi-Agent Runtime，你会删哪几层，哪些 Authority 仍必须留在 Zuno？
