# Program Closure Checklist

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE11_product-api-sse-ui-and-recovery-cutover

## 功能与质量关闭项

- [x] PHASE01 已冻结 baseline、truth source、PowerShell 命令和 sample case set。
- [x] PHASE02 已建立唯一版本化 AgentRuntimeState/Observation contract。
- [x] PHASE03 所有 Agent 角色模型调用统一经 Model Gateway。
- [x] PHASE04 run/checkpoint/plan/observation/interrupt/evidence/tool execution 可 SQLite 持久化并重启恢复。
- [x] PHASE05 LangGraph 主图 skeleton 可 run/stream/resume/cancel/checkpoint；产品切换仍待 PHASE11。
- [x] PHASE06 Plan-and-Execute 与 ReAct step 在同一图中逐步执行；真实 Tool Control Plane 执行待 PHASE07。
- [x] PHASE07 Tool Control Plane approval/resume/idempotency/trace baseline 完成；产品切换仍待 PHASE11。
- [x] PHASE08 EvidenceLedger 和 corrective retrieval 真实执行多轮；fixed benchmark 仍未 measured。
- [x] PHASE09 Reflection/Replan/Rewrite/Grounded Synthesis 已形成本地 runtime 质量闭环；产品切换和 benchmark 仍待后续 phase。
- [x] PHASE10 四层 Memory 与 Reflexion approved reuse 已被 unified runtime focused tests 证明；产品 API/UI 链路仍待 PHASE11。
- [ ] PHASE11 Completion/Workspace/SSE/UI 切换到统一 runtime，刷新/重启可恢复。
- [ ] PHASE12 真实 PDF SourceSpan vertical slice 通过。
- [ ] PHASE13 sample-8 与 sample-80 paired benchmark 完成，release gate 给出 measured 结论。
- [ ] 旧模拟 runtime 不再处于产品主路径；兼容 facade 有明确删除/保留决策。
- [ ] architecture / production-readiness / topic docs / HTML 已按实际 Current 更新。
- [ ] 所有 phase 状态、current.md、roadmap、references、system.yaml、verifier/tests 已同步。
- [ ] program 已归档到 docs/history/programs/，前台恢复 no-active。

## 禁止的虚假关闭

- contract test 通过不等于 runtime complete。
- deterministic fixture 通过不等于真实 provider complete。
- in-memory snapshot round-trip 不等于 restart recovery。
- replan 对象变化不等于 replan execution。
- Reflexion candidate 创建不等于 future reuse。
- Graph evidence 有 document id 不等于 SourceSpan citation。
- benchmark prepared 不等于 measured。
- HTML/文档完成不等于生产 runtime 完成。
