# Red Final Evaluation — rb-2026-09-15-formal-019

status: `COMPLETE`
overall_verdict: `PASS`
canonical_docs_read: `false`
blue_architecture_notes_read: `false`

Red Final 只依据 Frozen Resume、两轮 Red 问题、两轮 Blue 候选回答与 pinned Attack Skill 做盲评。

## 总结

这名候选人的工程可信度已经建立，主要原因不是术语多，而是两轮回答在 Ownership、时间线、实现细节和证据边界上保持一致。面对高压追问时，候选人多次主动承认“历史没做到”“没有 benchmark”“这是今天的设计建议”，没有把 Target Architecture 反写成个人历史贡献。

我会给 `PASS`，而不是 `STRONG_PASS`。阻止更高评级的主要因素是项目结果与复杂能力的外部证据仍偏弱：GraphRAG 只有 5-query development smoke，direct route 没有效益 benchmark，Memory 没有质量 A/B，法院侧测试的个人参与深度也没有建立。

## Claim authenticity

### 高可信

- **Tool/MCP 重构与 hardening**：能稳定解释 nested Agent-as-Tool 到 concrete Tool binding、call-time config injection、tool→server map、custom MCP recursion 与天气参数抽取；Blue1/Blue2 机制一致。
- **GraphRAG regression-fix story**：能清楚区分 ranking displacement 与 recall absence，并解释 baseline-preserving fusion、candidate group、baseline rank、graph signal、dedupe、seed/alias/path 等实现细节。
- **Context/Memory V2 foundation**：能稳定说明 scope、candidate/review、prepare_context、ContextOrchestrator，并持续强调它不是 production-grade Memory engine。

### 中可信 / 边界明确

- **法院侧测试 / Pilot Validation**：作为团队项目阶段可信，但候选人没有证明自己承担了现场部署、日志分析或正式验收。
- **Agent 必要性**：设计判断合理，但没有历史反事实 case 证明固定 Workflow 已经失败，所以不能把“必须 Agent”作为已验证结论。

### 未建立

- direct route 的稳定 latency/cost/reliability 收益；
- GraphRAG 对大样本或真实法律任务的普遍收益；
- long-term structured Memory 对任务质量的稳定收益；
- Multi-Agent 相对 Tool/Subgraph/worker 的收益。

没有触发 `CLAIM_IMPLEMENTATION_NOT_ESTABLISHED` 或 `CLAIM_CREDIBILITY_NOT_ESTABLISHED`。

## Ownership consistency

Ownership 表现是本轮明显强项。

候选人持续区分：

- 项目原本已有代码、前端、Agent、Memory；
- 自己能认领的 Tool/MCP、GraphRAG、Context/Memory V2 slices；
- 团队项目状态；
- 后来才出现的 Tool Effect / Security / Runtime Target 语义。

没有发现为了回答追问而扩大个人 Ownership 的行为。

## Implementation depth

### Tool / MCP

实现深度通过。候选人能下沉到实例级 user_id、call-time config、schema snapshot、同名 Tool collision、structured error、timeout/outcome unknown、幂等与远端 Provider 能力边界。

不足是 4 月历史实现本身没有副作用闭环；候选人正确承认这一点，因此这是历史能力边界，不是回答失败。

### GraphRAG

实现深度通过，而且是最强主线。候选人能解释：

- why regression；
- sort key；
- threshold=6/9 的 heuristic 性质；
- min-rank 的保护偏好；
- score scale 问题；
- missing chunk id 的 dedupe gap；
- seed amplification；
- alias collision；
- query gating 与 kill gate。

真正短板是 Evidence，而不是实现描述。

### Memory / Context

contract-level 深度通过，但 production semantics 尚未建立。候选人能识别 scope equality ≠ authorization、APPROVED bypass、reviewer authority、revocation TOCTOU、dedupe/CAS、conflict/supersession、expiry/delete、async rematerialization 等问题。

这说明候选人理解问题，但不能据此宣称历史系统已经解决这些问题。

## Fundamentals

通过。

能够把项目自然下沉到：

- HTTP timeout ≠ remote not executed；
- at-least-once / idempotency / reconciliation；
- ContextVar vs thread-local；
- READ COMMITTED / lost update / optimistic lock；
- coroutine cancellation ≠ remote request cancellation；
- Recall@K vs MRR；
- Vector vs BM25；
- checkpoint ≠ external effect truth。

没有发现只会背 Agent 框架、不懂后端/分布式基础的明显问题。

## Build / Buy / Delete judgment

表现较强。

候选人没有把自研视为能力证明，反复接受以下结论：

- MCP Host/Provider 可买；
- direct route 无收益可删；
- GraphRAG 无 holdout 增益可删或 gate；
- structured long-term Memory 无 A/B 可默认关闭；
- Multi-Agent 必须晚于 Tool/Subgraph/worker；
- Generic Host / Single Agent + Legal Backend 是合理 baseline。

这符合资深工程师思维，而不是技术堆栈展示。

## Blue1 → Blue2 变化

Blue2 没有通过改变历史事实来“修答案”。主要改进是把 Blue1 已承认的薄弱点继续落到明确设计边界：

- instance-bound user identity → request-local identity / versioned attempt；
- call-time config drift → Config/Credential version；
- Tool schema drift → immutable capability snapshot + replan；
- graph heuristic → ablation / sensitivity / deletion；
- scope equality → Security-owned scope authorization；
- approved memory → review transition + revocation/version；
- checkpoint → reconcile durable Domain/Effect truth。

这是有效的技术深化，不是话术补洞。

## Resume recommendations

### 保留

1. Tool/MCP concrete binding + user config injection。
2. GraphRAG ranking regression + baseline-preserving fusion。
3. scoped Context/Memory V2 + approved readback / provenance。

### 建议合并或降级

- **Workspace direct route** 不建议继续作为独立强 bullet。它有真实实现，但价值证据弱，适合并回 Tool/MCP hardening。
- GraphRAG 的 seed/alias/path 三项可以留在同一条“后续优化”里，但不要暗示每项都独立提升指标。
- 项目简介可保留“经历法院侧测试 / Pilot Validation”，但避免让句法暗示候选人本人完成现场 Pilot Owner 工作。

### 不应新增

- Production / SLA；
- GraphRAG 普遍提升；
- Memory 提升任务质量；
- Multi-Agent 架构 Owner；
- 4 月已经具有 Approval/Idempotency/Reconcile。

## 最终面试画像

候选人更像一个**工程边界意识较强、能做 Agent/RAG/Tool/Memory 具体实现并理解后端基础的 AI 应用工程师**，而不是“从零拥有完整 Agent 平台架构”的架构 Owner。

如果岗位是 Agent / LLM Application Engineer，我会继续推进后续面试；下一轮重点不再重复考对象名，而会看：

1. 能否拿出更真实的业务 bad case / benchmark；
2. 是否能把复杂设计落成最小实现与测试；
3. 在实际 coding/system design 中是否仍保持这种 Build/Buy 和 Authority 判断。
