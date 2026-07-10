# Current Program Reference

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE03_model-gateway-closure
latest_completed_program: zuno-lean-complete-product-architecture-v1
baseline_commit: 72488a25fde59bc5ef86b2b1c84f25d42cb946ca

`.agent/programs/` 当前已激活 `zuno-unified-agent-runtime-closure-v1`。本轮 program 的近期目标是把 `GeneralAgent`、`StrategySelector + AgentControlRuntime` 和 `SingleControllerDurableRuntime` 收敛为同一条真实、可恢复、可测量的 Single Controller Agent Runtime。

Phase 边界：PHASE01-PHASE13。

当前 phase：

- `.agent/programs/PHASE03_model-gateway-closure.md`

PHASE01 已冻结事实源、现状证据、运行命令、失败语义和 benchmark truth source；没有修改生产 runtime，也没有运行 fixed benchmark measured gate。PHASE02 已建立 unified runtime contracts and state，但没有完成模型网关、持久化、LangGraph 主图或产品切换。PHASE03 开始处理 Model Gateway closure。

## Active Program Files

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/program-decisions.md`
- `.agent/programs/code-architecture-map.md`
- `.agent/programs/powershell-runbook.md`
- `.agent/programs/test-matrix.md`
- `.agent/programs/PHASE01_truth-source-baseline-and-program-activation.md`
- `.agent/programs/PHASE02_unified-runtime-contracts-and-state.md`
- `.agent/programs/PHASE03_model-gateway-closure.md`
- `.agent/programs/PHASE04_durable-store-trace-and-idempotency.md`
- `.agent/programs/PHASE05_unified-langgraph-runtime-skeleton.md`
- `.agent/programs/PHASE06_strategy-plan-and-react-step-execution.md`
- `.agent/programs/PHASE07_tool-control-plane-and-approval-integration.md`
- `.agent/programs/PHASE08_corrective-agentic-graphrag-and-evidence-ledger.md`
- `.agent/programs/PHASE09_reflection-replan-grounded-synthesis.md`
- `.agent/programs/PHASE10_four-layer-memory-and-reflexion-reuse.md`
- `.agent/programs/PHASE11_product-api-sse-ui-and-recovery-cutover.md`
- `.agent/programs/PHASE12_real-pdf-source-span-vertical-slice.md`
- `.agent/programs/PHASE13_paired-benchmark-release-gate-and-program-closure.md`
- `.agent/programs/queued-programs/README.md`

## 最近完成归档

1. `docs/history/programs/zuno-lean-complete-product-architecture-v1/`
   - 状态：completed / archived。
   - 完成：目标架构事实源、HTML 展示、文档入口、renderer、verifier 和 tests 的收缩与同步。
   - 边界：没有修改核心 runtime，没有声称运行质量已经提升。
2. `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`
   - 状态：completed / archived。
   - 完成：evidence-span hardening baseline。
   - 边界：release gate 输出面已完成；fixed EnterpriseRAG measured pass 仍因 local agentic profile run incomplete 而 blocked。
3. `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
   - 状态：completed / archived。
   - 完成：Program 3 Mega launchable enterprise Agentic GraphRAG product baseline。
4. `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
   - 状态：completed / archived。
   - 完成：Product V1 local durable ingestion baseline。
5. `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
   - 状态：completed / archived。
6. `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
   - 状态：completed / archived。
   - 说明：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”。
7. `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
   - 状态：completed / archived。
   - 边界：runtime-first / vertical-slice-first closure evidence 保留在归档中。
8. `docs/history/programs/zuno-master-architecture-implementation-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE12。
9. `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE10。
10. `docs/history/programs/zuno-six-layer-internalization-v1/`
   - 状态：completed / archived。
11. `docs/history/programs/zuno-repo-layout-cleanup-v1/`
   - 状态：completed / archived。

## 历史边界

- Program 3 Mega 的 launchable baseline 结论保持不变：`Launchable enterprise Agentic GraphRAG product baseline completed; production scale external deployments remain replaceable targets.`
- Program 3 Mega 吸收并替代过的 suite / queued 输入仍是历史事实：`zuno-enterprise-agentic-graphrag-production-suite-v1`、`zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1` 和 `zuno-enterprise-knowledge-eval-benchmark-v1`。
- 历史 Program 3 final alias surface closure 已完成，旧 public import path 只通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。
- `zuno-runtime-architecture-upgrade-v1` 和 `zuno-architecture-visuals-v1` 是未来参考 draft，不是 active program。
- evidence-span hardening program 没有把 doc-level recall 写成 strict citation measured pass。
- Basic RAG 和 Static GraphRAG 是评测对照组，不是最终产品模式。
- Codex 多线程工程执行不等于 Zuno 产品 runtime 多 Agent 架构；近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- 每轮只执行 `.agent/programs/current.md` 指向的 current phase。
- 新 program 必须从 PHASE01 开始；不得把已归档 phase 文件复制回前台当作 active truth source。
- runtime-first / vertical-slice-first closure guard 保持有效。
- 新 runtime 行为继续遵守 TDD；只写 contract、schema 或 README 不能关闭 runtime phase。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- completed program 必须归档到 `docs/history/programs/`。
