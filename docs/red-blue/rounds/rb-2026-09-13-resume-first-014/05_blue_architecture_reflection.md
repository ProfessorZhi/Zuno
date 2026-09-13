# Blue Architecture Reflection — rb-2026-09-13-resume-first-014

formal_input_head: 6e7ab920c41687177ab86c1fe38574b7ac868c17
zuno_base_sha: 10869d9176d2ef34b46577478bba62d9e254158a

## Decision

**Architecture Revision: NO**

Round #014 暴露的主要断点不在 Zuno 九责任域的 Owner / Authority / State / Recovery / Security / Build-Buy 因果。Red 对这部分反而给出 STRONG_PASS：简单 RAG baseline、材料版本、机器候选与正式成果、checkpoint 与业务提交、unknown external effect、持续授权、Generic Host 复用和复杂度删除条件都能从真实 failure condition 推导。

真正断层发生在另一层：**模拟简历已经把历史个人实现写到了算法、函数、route 和 test artifact 的具体名字，但 canonical project/provenance 主要只恢复到 commit-level summary，尚未把这些任务整理成能直接支撑 implementation interview 的 source-level engineering story。**

所以本轮若直接修改 Architecture，会把历史取证问题误判成架构问题。

## Finding 1 — PF-031 GraphRAG implementation story

red_signal:
- Red Evaluation 将 GraphRAG 判为 FAIL / CRITICAL resume risk。
- 候选人不能解释 `limit=5` runner 语义、metric implementation、fusion 规则、seed expansion、alias normalization、path-aware ranking 和 fallback semantics。

source_check:
- PF-031 已经能证明用户 GitHub 账号对应一条连续历史工程链：先观察 sampled regression，再连续实现四类修复，并有同日 rerun。
- PF-031 同时明确禁止把它扩成正式 benchmark、普遍优于 baseline、客户问题根因或每个 commit 的独立因果收益。
- 当前 `docs/project/reference.md` 仍把“Exact personal task PR/interface/SQL/bug/test/result closure”统一写成 Unknown；它尚未吸收 PF-029–PF-032 已恢复出的更细个人任务事实。

classification:
**DOC_GAP + OWNERSHIP_GAP + EVIDENCE_GAP**

conditional classification:
**SIMULATED_RESUME_GAP** only if source recovery cannot support the algorithm names currently exposed on the resume.

decision_impact:
HIGH. 这是当前最可能让面试官否定个人实现 ownership 的断点。

recommended_owner:
Project Documentation Owner + Project Fact Provenance Owner.

next_action:
先从 PF-031 对应历史 commits / tests / eval runner 恢复 source-level story，不改 Architecture。至少需要固定：

```text
problem / failing query
→ baseline/local candidate list
→ metric and runner semantics
→ fusion implementation
→ seed expansion implementation
→ alias normalization implementation
→ path ranking implementation
→ committed tests / rerun
→ what was not measured
```

如果历史 source 能证明这些实现，更新 `project-fact-provenance.md` 的细节和 `docs/project/reference.md` 的 Personal Engineering Story；如果不能，下一轮 Resume Builder 缩小 GraphRAG bullet。

retest_needed: YES

## Finding 2 — PF-032 Tool / MCP story

red_signal:
- Tool/MCP 整体 PARTIAL，implementation depth FAIL。
- 面试官无法从回答中确认 concrete Tool binding lifecycle、tool→server mapping、用户配置隔离、direct-route matcher、两个 bug 的最小复现以及 regression assertions。

source_check:
- PF-032 已证明 4/15 `GeneralAgent` Tool/MCP strategy 与 4/28 Workspace route hardening 是用户账号的具体历史修改。
- Provenance 已有 before/after 摘要和 test artifact 名，但没有把函数、mapping、route predicate、test assertion 和原始 rationale 形成 interview-ready engineering reference。
- 后续 Effect / Approval / Idempotency / Reconcile Target 不允许反写到 4 月历史。

classification:
**DOC_GAP + OWNERSHIP_GAP**

secondary:
**EVIDENCE_GAP** for original Issue/reviewer/historical CI/real Tool trace.

decision_impact:
HIGH. Resume 已经具体到 middleware、direct route、bug 修复和 test artifact，因此实现深挖是合理压力。

recommended_owner:
Project Documentation Owner + Project Fact Provenance Owner.

next_action:
从 `77346758...`、`0b5fb350...` 和对应 tests 恢复：

```text
before/after call graph
concrete tool binding lifecycle
tool→server mapping and config injection boundary
direct-route predicate / fallback boundary
custom MCP recursion minimal reproduction
Gaode argument parsing before/after
critical positive/negative assertions
known concurrency / side-effect limits
```

这里不需要新增 Tool Runtime 架构对象；需要的是历史实现说明。

retest_needed: YES

## Finding 3 — PF-029/PF-030 Context / Memory story

red_signal:
- Context/Memory 为 PARTIAL，implementation depth FAIL。
- 候选人能说 readback hardening，却无法复现 typed contract 字段、scope dimensions、enforcement layer、`prepare_context()` / `ContextOrchestrator` 接口、arbitration 和关键 tests。

source_check:
- PF-030 已证明 V2 chain：Target plan → typed Context contract → scoped Memory foundation → minimum Agent integration → minimal ContextOrchestrator。
- PF-029 已证明 PR #8 对 same-scope task summary、仅 APPROVED structured memory、policy/source trace、review/provenance contract 的 hardening，并记录 focused tests `32 passed`。
- Provenance 明确这不等于完整 production Memory DB、长期 retrieval/consolidation 或完整审核生命周期。

classification:
**DOC_GAP + OWNERSHIP_GAP**

secondary:
**EVIDENCE_GAP** for original business trigger, review discussion and real runtime result.

decision_impact:
HIGH but below PF-031. “参与”降低了 Resume risk，但当前 bullet 的对象名仍要求 implementation recall。

recommended_owner:
Project Documentation Owner + Project Fact Provenance Owner.

next_action:
恢复并记录：

```text
Context / Memory contract field groups
MemoryScope dimensions and matching
prepare_context() input/output and read order
ContextOrchestrator exact responsibility
post-turn write boundary
APPROVED read gate location
source-id trace granularity
2–3 strongest positive tests
2–3 strongest negative tests
what PR #8 deliberately did not implement
```

不应为了回答面试问题，把 Target Memory Authority / stale invalidation 反写成 PR #8 Current。

retest_needed: YES

## Finding 4 — Pilot / real-user / collaboration provenance

red_signal:
- 项目真实性总体 PASS，但 Pilot environment、法院侧测试 shape、reviewer、真实 user workflow、Coding Agent contribution 无法下钻。

source_check:
- PF-015–PF-019 证明 Demo / court-side testing / Pilot Validation 历史存在。
- PF-020–PF-022 明确 Production、性能数字和完整历史环境没有证据。
- PF-006 只有约 7–8 人的可恢复规模，没有完整组织图。

classification:
**EVIDENCE_GAP + OWNERSHIP_GAP**

architecture_impact:
NONE.

next_action:
若还能恢复会议材料、环境截图、Issue/Review、真实 bad case、Pilot 记录，再升级项目故事；恢复不到就继续保持 Unknown，不为面试完整性编历史。

retest_needed: OPTIONAL after evidence recovery.

## Finding 5 — Architecture / Build-Buy / failure semantics

red_signal:
- Red Evaluation: STRONG_PASS。
- 简单 baseline、复杂度出现条件、external effect、continuous authorization、logical module != service、measurement/delete condition 均能回答。

source_check:
- `docs/architecture/architecture.md` 本身明确是 Target，不声称全部 Current。
- 文档从材料版本、候选/正式结果、长任务、Provider、持续授权、外部副作用和复杂度收益推导责任域，并明确优先复用 Generic Agent Harness。
- Current Evidence 仍严格限制 production/quality/recovery claims。

classification:
**NO_ZUNO_CHANGE**

architecture_impact:
NONE for this round.

next_action:
不要因为实现面试答不深而增加新 Module、Receipt、Provider 或状态机。当前问题要回历史 source / project reference 解决。

retest_needed: NO architecture retest until project implementation docs change.

## Finding 6 — Fundamentals

red_signal:
- TCP/HTTP timeout、idempotency、async cancellation、PostgreSQL isolation、Build/Buy 均 PASS。

classification:
**NO_ZUNO_CHANGE**

note:
这部分应继续从项目自然下钻，不需要在 Zuno canonical architecture 里增加八股解释。

## Why this is not an Architecture Gap

若一个设计的 Owner / Authority / Recovery 本身不成立，Architecture 应修改。例如：Formal Admission 无法给出正式事实 owner，或者 timeout recovery 仍要求 blind retry，那属于架构失败。

本轮发生的是另一种情况：Architecture 可以解释“应该怎样”，而历史个人实现 Claim 无法回答“当时这个函数、算法、参数和 test 到底怎样”。增加更多 Target 设计只会扩大二者差距。

当前合理顺序是：

```text
Round #014 finding
→ recover historical source-level implementation evidence
→ update Project Reference / Fact Provenance
→ decide resume claim strength
→ new resume-first Round
```

而不是：

```text
implementation interview answer weak
→ add more architecture
```

## Recommended bounded follow-up tasks

Priority 0:
- PF-031 GraphRAG source-level recovery.

Priority 1:
- PF-032 Tool/MCP source-level recovery.
- PF-029/PF-030 Context/Memory source-level recovery.

Priority 2:
- Pilot / review / real-user provenance recovery when materials exist.

Architecture revision priority from Round #014:
**NONE.**

## Retest gate

下一轮只有在至少一个 P0/P1 implementation story 被恢复并进入 canonical Project documentation 后才有信息增益。否则重新问 100 题只会再次得到相同的“架构强、历史实现细节弱”。
