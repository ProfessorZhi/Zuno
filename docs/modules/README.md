# 模块设计入口

status: `MODULE_BOUNDARY_NOT_FROZEN`

本目录预留给总体架构 Freeze Review 之后的逻辑模块设计。当前总体架构已经形成 `10-MODULE CANDIDATE`，但这不是旧 11 模块目录的机械恢复，也不表示模块数量、服务数量或部署数量已经冻结。

## 当前边界

```text
FINAL_MODULE_COUNT = NOT_FROZEN
MODULE_BOUNDARIES = UNDER_FREEZE_REVIEW
MODULE_DOCUMENTS = NONE
MODULE_DECOMPOSITION_GATE = NOT_OPEN
```

当前只维护本 README。模块文档必须在 Overall Architecture Freeze Red / Blue 攻击候选边界、形成 accepted module map 并明确打开 `MODULE_DECOMPOSITION_GATE` 后，经明确决策再建立。

## 10-MODULE CANDIDATE

1. `Product Surface & Agent Portfolio`：用户、法院系统、Generic Host 与 Agent Portfolio 的入口和产品表面；
2. `Legal Domain & Work Product`：Matter、Canonical Legal State、Human Decision 和 WorkProduct；
3. `Knowledge & Evidence`：Ingestion、Knowledge View、Readiness、Retrieval、Evidence 和 Citation；
4. `Agent Runtime & Multi-Agent Orchestration`：Single Controller、Plan、Step、受控 Specialist Agent、Join 和 Recovery；
5. `Capability / Skill & Tool Runtime`：专业 Capability Provider 与受控 Tool / External Effect；
6. `Model Gateway`：模型角色、Provider、Routing、Budget、Fallback 和 Usage Receipt；
7. `Memory & Context`：可复用上下文、Memory 生命周期和 Provider Integration；
8. `Security & Governance`：Identity、Policy、Authorization、Approval、Secret、Audit 和 Security Gate；
9. `Observability & Evaluation`：OTel-compatible Telemetry、Decision Trace、Redaction、Eval 和 Release Gate；
10. `Infrastructure & Persistence`：Persistence、Checkpoint、Object / Index Store、Queue、Worker、Deployment 和 DR。

这 10 个名称只表达候选责任域，不创建 10 个 Service，也不代表每个候选都一定需要独立文档。下一步是：

```text
Overall Architecture Freeze Red / Blue
  → attack candidate boundaries
  → accepted module map
  → freeze module count
  → open MODULE_DECOMPOSITION_GATE
  → create detailed module documents
```

## 模块文档必须回答

- 模块拥有哪类状态和事实；
- 输入、输出和跨模块 Contract 是什么；
- 正常流程、失败、重试、恢复和对账如何闭环；
- 为什么需要独立模块，而不是已有 Library、Worker 或 Provider；
- 如何由代码、测试、Trace、Eval 或运行证据证明；
- 何时可以合并、替换、外置或删除。

总体跨层关系仍由 [`../architecture/architecture.md`](../architecture/architecture.md) 负责；模块文档不得在这里创建第二套全局架构事实。模块的 Current / Gap 对照必须引用 [`../project/development-process.md`](../project/development-process.md) 和 [`../evidence/`](../evidence/README.md)，不得把 Target 当作 Current。
