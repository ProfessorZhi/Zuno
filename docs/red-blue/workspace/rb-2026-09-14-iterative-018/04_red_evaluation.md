# Red Evaluation — rb-2026-09-14-iterative-018

mode: BATCH_WAVES
observable_inputs:
- frozen simulated resume
- Red Wave 1 plan / pressure suite
- Blue Wave 1 batch answers
- Red Wave 2 questions generated from Wave 1
- Blue Wave 2 batch answers

Red Evaluation does not use Zuno canonical docs as an answer key.

## Overall verdict: PASS

候选人已经能把简历里的主要 Claim 落到具体工程机制，而且第二波追问没有把关键 Claim 打穿。最强的地方是 GraphRAG：能解释 regression 是怎么被发现的、ranking state 如何变化、baseline-preserving 到底 preserve 什么，也主动承认样本和 ablation 边界。Tool/MCP 与 Memory 也不再停在框架名，而是能进入 config injection、route bad case、scope、review gate、Context packet 等实现层。

没有给 STRONG_PASS 的主要原因不是“答错”，而是项目结果层仍然偏研发证据：真实 Pilot 规模、业务质量结果、生产运行数据基本没有恢复；Tool 并发隔离、Memory durable concurrency / revocation、GraphRAG 正式 benchmark 等也被候选人自己明确标为未证明。作为一面候选人这反而增加可信度，但会让面试官继续判断这些 Claim 到底是成熟系统经验还是高质量研发/架构经验。

## Thread A — Tool / MCP strategy

verdict: PASS
ownership: 4/4
business_causality: 3/4
implementation_depth: 4/4
build_buy: 4/4
failure_recovery: 3/4
evidence: 3/4
fundamentals: 4/4
communication: 3/4

strongest_exchange: 能从 MCPAgent-as-Tool 的旧链路讲到 concrete Tool binding、call-time user config、再承认两用户并发隔离没有测试证明。第二波还能进一步给出 stateless middleware / ExecutionContext 的改进方向，而没有把 Target 冒充历史实现。

weakest_exchange: 原始业务触发与真实线上收益没有恢复；Tool discovery freshness、同名 Tool namespace 和完整 direct-route security equivalence 都只能讲设计方向。

resume_claim_risk: LOW-MEDIUM。当前 Resume Claim 本身有实现支撑，但不要增加“生产稳定性”“显著降低 latency/token”一类结果。

## Thread B — Workspace direct route / ReAct

verdict: PASS
ownership: 4/4
business_causality: 3/4
implementation_depth: 4/4
failure_recovery: 3/4
evidence: 4/4
communication: 4/4

strongest_exchange: custom MCP 递归与天气 city extraction 都能讲清 before/after 和 regression behavior。

weakest_exchange: direct route 与 ReAct 的安全检查是否真正共用一条执行边界没有当前证明；ReAct hard stop 也未建立。

resume_claim_risk: LOW。不要把具体 hardening 提升成完整 Routing Engine。

## Thread C — GraphRAG fusion / regression

verdict: STRONG_PASS
ownership: 4/4
business_causality: 4/4
implementation_depth: 4/4
build_buy: 4/4
failure_recovery: 3/4
evidence: 4/4
fundamentals: 4/4
communication: 4/4

strongest_exchange: 能清楚区分 recall failure 与 Top-K ranking regression，进一步解释 candidate group、baseline rank、graph signal、promotion threshold，并主动指出 threshold 是 heuristic、同一 5-query dev set 不是 holdout、连续 commit 没有 ablation 因果。

weakest_exchange: 正式 benchmark / threshold calibration / entity identity / version invalidation 尚未形成成熟闭环。

resume_claim_risk: LOW，只要继续保留 `development smoke / 恢复到 baseline 水平` 的范围限定。

## Thread D — Multi-hop GraphRAG

verdict: PASS
ownership: 4/4
implementation_depth: 4/4
evidence: 3/4
fundamentals: 4/4

strongest_exchange: seed source、candidate context、alias normalization 风险、path score 构成和长路径问题都能解释，不把轻量 alias normalization 说成真正 entity resolution。

weakest_exchange: graph/index freshness、实体 stable id 与 merge/split 版本语义目前主要是下一步设计，而不是已验证能力。

## Thread E/F — Context / Memory

verdict: PASS
ownership: 4/4
business_causality: 4/4
implementation_depth: 4/4
failure_recovery: 3/4
evidence: 3/4
fundamentals: 4/4
communication: 3/4

strongest_exchange: 能给出 `MemoryScope` 字段，说明 scope 只是 data contract、caller/policy 仍可能把可选字段漏掉；也能解释 PENDING/APPROVED、review decision、source_event_ids、ContextOrchestrator token selection，以及 read-time gate 的 TOCTOU 问题。

weakest_exchange: durable store concurrency、review authority、privacy deletion / revocation 对运行中 ContextPacket 的语义仍然没有 Current 实现闭环。候选人第二波给出的 version/epoch、review ledger 是设计答案，不是项目已实现成果。

resume_claim_risk: LOW-MEDIUM。当前两条 Memory bullet 可以保留，但面试中必须继续主动区分 foundation/readback hardening 与成熟 Memory Platform。

## Thread G — Agent topology / Multi-Agent / Build-Buy

verdict: PASS
business_causality: 4/4
implementation_depth: 3/4
build_buy: 4/4
failure_recovery: 4/4
fundamentals: 4/4
communication: 4/4

strongest_exchange: 没有把 Multi-Agent 当高级答案，而是给出 Tool → Subgraph → Specialist Agent 的升级条件；能解释 Single logical controller + parallel workers 的中间态，并把 Domain authority、Memory owner、late result/version binding 与 Agent topology 解耦。

weakest_exchange: 这部分大多是架构推演，而不是已有 Multi-Agent implementation experience。面试官若岗位强要求生产 Multi-Agent，需要继续确认候选人是否真的做过这一类 runtime。

resume_claim_risk: 当前 Resume 没写 Multi-Agent，因此无直接夸大风险。后续只有实际设计/实现/验证形成证据后才适合写进简历。

## Thread H — Ownership / Evidence / Pilot

verdict: PASS
ownership: 4/4
evidence: 4/4
communication: 4/4

候选人主动说明项目不是从零搭、Pilot 不等于 Production、5-query smoke 不等于 benchmark，也区分历史实现和今天的 Target 架构。这种边界不会让面试官觉得“弱”，反而比包装数据更可信。

主要短板是 Court/Pilot 的可验证规模和业务结果仍然很薄。

## Red hire signal

对于 Agent / AI 应用工程一面：`PASS`。

候选人现在最有说服力的画像是：做过具体 Agent Tool/MCP 改造、能深入定位检索 ranking regression、做过 Context/Memory contract/readback hardening，并且对复杂度、Evidence 和 Authority 有较强工程判断。

还不能从本轮回答推出：生产级 Multi-Agent Runtime owner、成熟分布式 Tool Effect owner、生产级 Memory platform owner、正式 GraphRAG benchmark owner 或 Production/SLA 经验。
