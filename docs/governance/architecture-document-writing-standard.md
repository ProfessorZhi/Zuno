# Zuno 架构文档写作标准

updated: 2026-08-13
status: active-document-governance
scope: `docs/project/architecture/` 与 `docs/project/<topic>/`

## 0. 这份标准解决什么问题

本标准只规定文档如何表达，不新增领域 Contract，也不把 Target、Hypothesis 或 Future 写成 Current。架构文档从问题和业务场景出发，再说明边界、Owner、状态、失败和验证。

```text
问题与场景
→ Product / Domain 边界
→ Logical Capability
→ Physical Service / Worker
→ Data Ownership
→ Security / Failure / Recovery
→ Current / Target / Hypothesis / Future / History
→ Verification and Reversal Criteria
```

## 1. Canonical taxonomy 与事实源

正式架构事实按问题路由到唯一专题文档：

| 目录 | Canonical Question |
| --- | --- |
| `product/` | 用户任务、产品表面和外部 Host 是什么？ |
| `domain/` | 法律业务世界的事实、版本和生命周期是什么？ |
| `agents/` | Agent 如何计划、协作、恢复和使用能力？ |
| `knowledge/` | 信息如何摄取、检索、引用和形成证据？ |
| `services/` | 哪些逻辑能力形成独立部署边界？ |
| `data/` | 谁拥有数据，分布式失败如何对账？ |
| `security/` | 谁可以做什么，如何产生可验证安全证据？ |
| `eval/` | 如何证明质量、效率和复杂度收益？ |
| `deployment/` | 服务如何运行、扩缩容和隔离？ |

`docs/project/architecture/architecture.md` 只回答跨层集成；`architecture-views.md` 与 `architecture.html` 是展示配对；`docs/project/modules/` 只保存上一阶段 11 模块的 Superseded 迁移材料。

## 2. 每份 Canonical 专题文档的最小协议

每个专题必须在头部声明：

```yaml
status: normative-target | current-fact | hypothesis | history
architecture_state: ACCEPTED_TARGET | PROPOSED | UNDER_ATTACK | REJECTED | DEFERRED
canonical_question: ...
owner: ...
replaces: ...
```

`architecture_state` 与 `status` 正交：`ACCEPTED_TARGET` 只表示用户已经接受该设计作为
下一阶段 Canonical Target，不表示代码已实现、验证、测量或具备生产资格。实现、证据和外部
资格仍分别由 `Current / Target / Gap`、ADR、Program 和 `docs/status/` 记录。

正文至少回答：

- 为什么存在，典型业务案例是什么；
- Responsibilities / Non-responsibilities 和唯一 Owner；
- Current 证据、Target 设计、Hypothesis、Gap 与 Future；
- 正常路径、失败路径、重试、恢复、幂等和人工介入；
- Security、Audit、Observability、Test/Evidence 和替换条件；
- 与相邻专题的依赖，而不是复制它们的 Canonical State。

专题可以采用 Part A/Part B，也可以按问题分节；Part A 与规范内容必须在同一文件中，不能创建 `*-human.md`、`*-spec.md` 或 `.agent` 镜像。

## 3. Logical 与 Physical 的写作边界

```text
Product / Domain
    ≠ Logical Capability
Logical Capability
    ≠ Physical Service
Physical Service
    ≠ Process / Container / Team
```

每个服务候选必须回答 `Why service? Why not library? Why not worker? Who owns the state? How does it recover?`。用户规模不是单独拆服务的理由；只有 Independent Scaling、Failure Isolation、Security Isolation、Independent Deployment、Distinct Availability 或 Data Ownership 等证据才允许拆分。

FastAPI 是 Application/HTTP Interface；LangGraph 只属于 Agent Runtime orchestration。PostgreSQL Canonical Domain State 与 Runtime Checkpoint 必须分别归属并设计 Recovery Reconciliation。

## 4. 状态与证据规则

- `Current` 必须由代码、Migration、测试、Trace、Eval 或真实运行证据证明；类名、Mock、目录和 Target 文档不算实现证据。
- `Target` 是已经接受的设计目标，不是已经部署的事实。
- `Hypothesis` 必须给出 Benchmark、Spike、User Validation 或 Security Evidence 的关闭方式。
- `History` 只解释被替换的结构，不得与新 taxonomy 并列为 Canonical Truth。
- 不同文档不得各自定义同一 Fact、State Machine、Service Owner 或指标含义；需要引用唯一 Owner。

## 5. 图源、入口和验证

`docs/project/architecture/` 只能有四个文件。图形语义变化时同步更新 `architecture-views.md` 与 `architecture.html`，并运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
```

图只用于解释关系，不取代文字 Canonical Owner；HTML 不得创造图源不存在的新事实。`docs/verification/` 是 QA/验证语料，不是架构事实源。

## 6. 评审完成条件

每轮 Red / Blue 必须经过：

```text
Red Attack → Blue Response → Counter Attack
→ Architecture Decision → ADR
→ Canonical Doc Update → Red Retest
```

没有满足证据门的复杂度进入 `DEFER` 或 `HYPOTHESIS`；验证器只能检查确定性结构，不能把文档存在误报成 Runtime、质量或 Production Ready。
