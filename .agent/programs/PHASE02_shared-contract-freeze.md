# PHASE02 Shared Contract Freeze

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE02_shared-contract-freeze
status: pending

## 目标

在并行实现前冻结共享契约，避免多个 workstream 同时改 `AgentRun`、`ContextPack`、`RetrievalProfile`、`CapabilityCard`、`PlanStep`、trace / cost metric 等核心对象造成冲突。

## 范围

- 定义或确认 `AgentRun`、`ContextPack`、`RetrievalProfile`、`RetrievalDecision`、`EvidenceBundle`、`CitationLineage`。
- 定义或确认 `CapabilityCard`、`SkillCard`、`ToolCard`、MCP capability、output contract、eval rubric。
- 定义或确认 `PlanStep`、`PlanState`、`StrategySelectorOutput`、`ReflectionVerdict`、`ReplanDecision`、`ReflexionLesson`。
- 定义或确认 `TraceMetric`、`CostMetric`、model call metric 和 release baseline metric。

## 目标架构拼接点

本 phase 是所有层之间的“接口冻结层”。最终目标架构能拼起来，靠的是这些 contract 让各层只依赖稳定语义，而不是互相读内部实现：

- Knowledge 输出 `EvidenceBundle` 和 `CitationLineage` 给 Planning / Reflection / Output Gate。
- Memory 输出 `ContextPack` 给 Planning。
- Capability 输出 `SkillCard`、`ToolCard` 和 allowed capability summary 给 Planning。
- Security 输出 gate verdict 给 Planning 和 Tool runtime。
- Model Gateway 输出 cost / latency / token metrics 给 Eval。
- Planning 输出 plan / replan / reflexion events 给 Trace / Eval。

PHASE02 完成后，后续 workstream 不允许随意发明第二套 plan、evidence、skill 或 trace 字段。

## 并行开发可行性

本 phase 主要串行，最多允许只读 review 并行。原因是 contract 文件属于高耦合共享面。

可并行：

- Workstream B/C/D/E/F/G 各自提出字段需求。
- Coordinator 汇总字段，做最小公共 contract。

不可并行：

- 多个 agent 同时编辑同一个 contract 文件。
- 在 runtime 实现中临时新增未登记字段。
- 跳过 PHASE02 直接实现 PHASE03-PHASE13。

## 详细执行卡

- 输入依赖：PHASE01 owner map、现有 DTO / storage / agent / knowledge contracts、workspace API schema、trace/eval 字段现状。
- 主要交付物：共享 contract 文件、contract tests、兼容说明、后续 workstream 不得擅自改动的冻结字段清单。
- 可并行工作包：只读 review 可并行；实际 contract 文件只能单 owner 编辑。各 workstream 可以提交 contract request，但不能直接改共享 schema。
- Coordinator 锁点：AgentRun、ContextPack、RetrievalProfile、EvidenceBundle、SkillCard、PlanState、TraceMetric、Workspace API DTO。
- 下游交接：PHASE03 需要 ingestion/status contracts；PHASE04 需要 retrieval/evidence contracts；PHASE05 需要 ContextPack；PHASE06 需要 Capability/SkillCard；PHASE09 需要 Plan/Replan/Reflection contracts。
- PR / commit 建议：`feat(contracts): freeze agentic graphrag shared runtime contracts`，必须先过 contract tests 再允许并行实现。

## 禁止范围

- 不在本 phase 大改 `GeneralAgent` 主循环。
- 不让各 workstream 自行新增不兼容 contract 字段。
- 不把 contract-only 写成 runtime completion。

## 验收闸门

- 共享契约文件位置明确，字段命名稳定。
- focused contract tests 覆盖序列化、默认值、枚举值和 backward-compatible parse。
- 后续 workstream 修改 shared contract 必须经 Coordinator 审查。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent tests/knowledge tests/evals -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 需要先读取

- `src/backend/zuno/agent/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/platform/observability/**`
- `tests/agent/**`
- `tests/knowledge/**`
- `tests/evals/**`

## 需要修改的文件

- `src/backend/zuno/agent/contracts.py` or existing equivalent
- `src/backend/zuno/agent/planning/contracts.py` if introduced
- `src/backend/zuno/capability/contracts.py`
- `src/backend/zuno/knowledge/retrieval/contracts.py` or existing equivalent
- `src/backend/zuno/platform/observability/contracts.py` or existing equivalent
- focused contract tests

## 执行拆解

1. 盘点现有 contract 和 DTO，避免重复定义。
2. 写 failing contract tests。
3. 增补最小 dataclass / pydantic / protocol contract。
4. 跑 focused tests。
5. 生成 shared contract map，供 PHASE03-PHASE13 使用。

## 多 agent 分工

- Coordinator owner。
- Workstream B/C/D/F/G 可只读 review 字段是否满足后续实现。
- 不允许多个 agent 同时编辑 shared contract 文件。

## 需要返回的证据

- contract file list。
- focused tests。
- 字段兼容性说明。
- 哪些 contract 被标为 frozen。

## 停止条件

- 发现现有 API contract 与计划字段冲突且不能兼容。
- 需要 DB migration 或 frontend breaking change 才能冻结 contract。
- 多个 workstream 对同一字段含义无法收敛。
