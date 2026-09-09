# Findings — rb-2026-09-09-resume-claims-001

Round result: `CLOSED_WITH_FINDINGS`  
Highest severity: `S0`

本页只保留会改变后续决策的去重结果。Round 本身不修改 Resume、Project、Architecture、Evidence 或 Ownership Truth。

## F1 — Resume 把方向级参与扩大成多项个人设计 / 实现

Severity: `S0`  
Type: `RESUME_CLAIM_RISK`, `OWNERSHIP_GAP`, `EVIDENCE_GAP`

### Finding

当前 Resume 的 Zuno 条目连续使用“设计”“实现”等个人强动词覆盖领域模型、统一控制器、动态 GraphRAG、三层记忆、工具审批 / 幂等 / 中断恢复和评测等多个方向。Canonical Project 当前只能稳定支持部分 Agent 开发、Memory 第一批重要工作、OpenViking 接入、Tool Calling Strategy、数据库查看 / 调试等方向级个人参与；项目在本人加入前已经存在。

### Decision impact

Resume 不能继续把整条 Target / Team capability 作为个人已完成事实。需要二选一：

1. 将未证明的强动词降级为团队 / 平台能力或“参与 / 负责其中某一部分”；
2. 为需要保留的个人强 Claim 恢复任务级 Evidence：需求、PR / commit、关键代码、Bug、测试、Review、结果与个人责任边界。

### Source support

- Resume snapshot：Zuno 项目条目的个人强 Claim。
- `docs/project/README.md`：项目非 Greenfield；当前个人 Ownership 只到方向级。
- `docs/evidence/`：Target / 文档存在不自动成为个人实现 Evidence。

### Evidence needed

至少恢复 1–2 个可完整说明的个人任务闭环，优先从 Agent、Memory / OpenViking、Tool Calling 或数据库调试中选择。

### Retest scenario

Resume 修订或 Evidence 恢复后，随机抽取一个强动词，要求候选人在 90 秒内说清“原需求 → 本人决策 → 关键实现 → 故障 / 权衡 → 测试 / 结果 → 团队边界”。

## F2 — Resume 的“企业知识库 Agent 平台”定位缺少项目历史依据

Severity: `S0`  
Type: `RESUME_CLAIM_RISK`, `PROJECT_REALITY_GAP`

### Finding

Resume 将 Zuno 描述为“企业知识库 Agent 平台”，而 Canonical Project 的已确认背景是 LIPLAB 智慧司法研究与工程化、天津法院智慧平台相关场景及长期法律工作。当前 History 没有恢复“法律项目后来正式泛化为企业知识库平台”的需求、版本或产品定位证据。

### Decision impact

不能在面试中临时解释成“后来做了企业泛化”。Resume 项目身份需要与 Canonical Project Truth 对齐；如果确有历史泛化，则先恢复对应 History / Evidence，再决定是否保留企业化表述。

### Source support

- Resume snapshot：项目名与项目简介使用“企业知识库 Agent 平台”。
- `docs/project/README.md`：智慧司法 / 天津法院相关背景、历史与 Target 分离。
- `docs/governance/project-fact-provenance.md`：未证明历史保持 Unknown。

### Evidence needed

历史需求、产品说明、版本提交、Demo / Pilot 材料或其他能够证明产品定位发生过泛化的来源。

### Retest scenario

面试官只看 Resume，先问“这个企业平台的客户和真实业务是什么”，再追问其与天津法院 / LIPLAB 的关系。回答不得依赖临时创造的产品演进故事。

## F3 — 评测执行路径存在，但 Resume 把 plumbing 写得接近已验证覆盖面

Severity: `S1/S2`  
Type: `EVIDENCE_GAP`, `MEASUREMENT_GAP`, `RESUME_CLAIM_RISK`

### Finding

Current 可以证明评测执行路径、selected canonical tests 与 evaluator modes 存在；正式 benchmark 仍为 `MEASUREMENT_BLOCKED / BLOCKED_NOT_MEASURED`，质量与 Production Readiness 未建立。Resume 的“固定评测链路”可以描述工具 / 执行入口，但“覆盖证据召回、完整证据链命中与无据拒答”容易被理解成这些质量维度已经具有正式数据和结果。

### Decision impact

在正式 benchmark 之前，Resume 应将“评测基础设施 / 执行入口”与“已经验证的质量覆盖 / 指标结果”分开。GraphRAG、无据拒答和复杂检索的收益不能写成已证明优势。

### Source support

- `docs/evidence/current-eval-baseline.md`：`MEASUREMENT_BLOCKED`。
- `docs/evidence/current-test-baseline.md`：selected tests 存在；benchmark、quality、production readiness 未建立。
- `docs/decisions/0006-evidence-driven-agentic-graphrag.md`：相关能力与测量方式属于 Target / accepted design，不能替代 Current benchmark。

### Evidence needed

冻结 DatasetVersion、sample count、metric、baseline、commit SHA 与正式结果；GraphRAG 等复杂机制还需要 ablation / complexity kill test。

### Retest scenario

要求候选人分别回答：

- 今天已经实现了什么评测 plumbing？
- 今天真正测出了什么？
- 哪些仍然 Blocked？
- 如果没有质量收益，哪些复杂机制应该删除？

四问中任何一问不得用 Target 设计替代 Current Evidence。

## Round-level conclusion

本轮没有发现需要修改当前 Project / Architecture / Module Part A 的新 `NARRATIVE_GAP` 或 `ARCHITECTURE_GAP`。相反，新版 Human docs 能够让 Blue 在面对强追问时明确退回 Generic Host baseline、拒绝夸大个人 Ownership、拒绝编造产品泛化历史，并保持 Current / Target 分层。

当前最高优先级从“继续润色 Zuno 文档”转为：

```text
Resume alignment
→ recover personal task-level evidence
→ formal evaluation / measurement evidence
→ re-run with different wording
```
