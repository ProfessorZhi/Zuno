# Program Closure Checklist

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE06_strategy-plan-and-react-step-execution

## 功能与质量关闭项

- [x] PHASE01 已冻结 baseline、truth source、PowerShell 命令和 sample case set。
- [x] PHASE02 已建立唯一版本化 AgentRuntimeState/Observation contract。
- [x] PHASE03 所有 Agent 角色模型调用统一经 Model Gateway。
- [x] PHASE04 run/checkpoint/plan/observation/interrupt/evidence/tool execution 可 SQLite 持久化并重启恢复。
- [x] PHASE05 LangGraph 主图 skeleton 可 run/stream/resume/cancel/checkpoint；产品切换仍待 PHASE11。
- [ ] PHASE06 Plan-and-Execute 与 ReAct step 在同一图中真实执行。
- [ ] PHASE07 Tool Control Plane approval/timeout/idempotency/trace 闭环完成。
- [ ] PHASE08 EvidenceLedger 和 corrective retrieval 真实执行多轮。
- [ ] PHASE09 Reflection/Replan/Rewrite/Grounded Synthesis 形成质量闭环。
- [ ] PHASE10 四层 Memory 与 Reflexion approved reuse 被产品链路证明。
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
