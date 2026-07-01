# PHASE12 End To End Product Runtime

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE12_end-to-end-product-runtime
status: pending

## 目标

跑通 launchable product baseline 的完整 E2E：file upload/register -> ingest async/local worker -> parse/document/index persistence -> standard/deep retrieval -> Agent planning -> skill selection -> evidence/citation -> reflection/replan -> artifact -> trace/eval/cost -> feedback -> restart rehydrate。

## 范围

- 标准检索单文档事实场景。
- 深度检索跨文档分析场景。
- deep_without_graph fallback 场景。
- blocked OCR / VLM 不 fake index 场景。
- retrieval_empty 或 citation_coverage_low 触发 dynamic replan 场景。
- ReflexionLesson candidate 生成场景。

## 用户可感知 E2E Evidence

E2E 不能只 assert 后端字段。每个 product scenario 必须生成可分享的 scenario summary / trace summary fixture，至少包含：

- `user_question`：用户原始问题。
- `selected_knowledge_spaces`：选中的知识库。
- `retrieval_profiles`：每个知识库的标准检索 / 深度检索。
- `selected_skill`：自动选择或 pinned 的 Skill。
- `plan_summary`：用户可理解的计划摘要。
- `retrieval_decision`：requested_profile、effective_profile、fallback_reason、retrievers_used。
- `reflection_verdict`：证据是否足够、citation coverage 是否达标、是否需要 re-query。
- `replan_event`：触发原因、被替换的 step、后续轨迹变化。
- `artifact_content_excerpt`：产物片段，不泄露私有全文。
- `citations`：可追溯 citation refs。
- `metrics_summary`：latency、cost、token、evidence_count、citation_coverage。
- `feedback_result`：反馈是否写入 durable/task/eval surface。
- `restart_rehydrate_result`：重启后 task/artifact/feedback/cited answer 是否仍可恢复。

这些 evidence 是 PHASE13 benchmark 和 PHASE15 closure summary 的输入，不允许只保存在临时测试日志里。

## 目标架构拼接点

本 phase 是所有层拼成产品基线的证明：

```text
AgentChat / Workspace API
  -> Input / Async Infrastructure
  -> Knowledge / Retrieval / GraphRAG Profile
  -> Memory & Context Engine
  -> Capability / Skill / Tool / MCP
  -> Security / Governance
  -> Model Gateway / Cost
  -> Planning & Control Runtime
  -> Eval / Trace / Cost
  -> Artifact / Feedback / Restart Recovery
```

E2E 不是新增一套 demo path，而是复用真实 local implementation、真实 durable store、真实 task runtime、真实 retrieval / planning / trace contract。这个 phase 决定能否说 product baseline completed。

## 并行开发可行性

本 phase 必须由 Coordinator 集成。各 workstream 可以并行修自己层的失败，但 E2E test ownership 不能分散。

可并行：

- Workstream A 修 ingest / worker / persistence failure。
- Workstream B 修 retrieval / citation failure。
- Workstream F 修 planning / replan failure。
- Workstream G 修 trace / eval metric failure。

不可并行：

- 多个 agent 同时改同一个 E2E scenario 的 expected output。
- 用 mock-only path 替代真实 local runtime path。
- 以删除断言方式“修复”E2E。

## 详细执行卡

- 输入依赖：PHASE03 ingestion workers、PHASE04 retrieval profiles、PHASE05 ContextPack、PHASE06 Skill registry、PHASE07 gates、PHASE08 metrics、PHASE09/10 planner runtime、PHASE11 API contract。
- 主要交付物：完整 E2E scenario tests、shareable scenario summary / trace summary fixture、restart rehydrate proof、standard/deep/deep_without_graph coverage、blocked OCR no fake index、dynamic replan proof、ReflexionLesson candidate proof。
- 可并行工作包：test fixtures、scenario data、trace assertions 可并行准备；最终 E2E runner 和 runtime wiring 必须单 owner 收口。
- Coordinator 锁点：跨模块失败根因判断、是否关闭 phase、是否允许 fallback 作为 completion evidence。
- 下游交接：PHASE13 消费 E2E trace/eval/cost artifacts；PHASE14 把 E2E 链路写入 architecture；PHASE15 归档 closure evidence。
- PR / commit 建议：`test(e2e): add launchable agentic graphrag product baseline scenario`，不要混入大规模 runtime 重构。

## 禁止范围

- 不把 isolated unit tests 当作 E2E closure。
- 不用 fake success 掩盖 blocked OCR / VLM、missing index 或 citation missing。
- 不让 E2E 依赖真实外部服务。

## 验收闸门

- E2E scenario 在 local implementation 下可运行。
- E2E 输出包含用户问题、知识库、profile、selected skill、plan summary、retrieval decision、reflection verdict、replan event、artifact excerpt、citations、metrics summary、feedback result 和 restart rehydrate result。
- E2E 生成 shareable scenario summary / trace summary fixture，不能只 assert internal fields。
- restart rehydrate 后仍能查询 artifact / feedback / cited answer。
- trace / eval / cost fields 存在。
- replan 与 reflexion candidate 至少各出现一次。

## 验证命令

```powershell
git diff --check
pytest -q tests/evals/test_agentic_graphrag_product_baseline.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
```

## 需要先读取

- `tests/api/test_workspace_durable_ingest_runtime.py`
- `tests/api/test_workspace_task_runtime.py`
- `tests/agent/**`
- `tests/knowledge/**`
- `tests/evals/**`
- relevant runtime services touched by PHASE03-PHASE11

## 需要修改的文件

- `tests/evals/test_agentic_graphrag_product_baseline.py`
- focused integration tests under `tests/api/**`, `tests/agent/**`, `tests/knowledge/**`
- runtime integration files only as required by failing E2E tests

## 执行拆解

1. 写 E2E scenario test skeleton with real service/runtime calls。
2. 跑测试确认缺口。
3. 补最小 integration wiring。
4. 覆盖 standard / deep / fallback / blocked / replan / reflexion scenarios。
5. 测 restart rehydrate。
6. 记录 trace / eval / cost evidence。

## 多 agent 分工

- Coordinator owner。
- Workstream A-H 修各自失败根因。
- Coordinator 统一跑 E2E 和防止 workstream 互相覆盖。

## 需要返回的证据

- E2E test names。
- scenario trace。
- restart rehydrate evidence。
- blocked OCR / VLM no fake index evidence。
- dynamic replan and ReflexionLesson evidence。

## 停止条件

- E2E 无法在 local implementation 下运行，且失败不是小修能解决。
- 需要真实外部服务才能继续。
- citation lineage 或 ACL filter 在 E2E 中断链。
