# ADR-0011：Canonical Architecture Document Taxonomy

- 状态：`accepted-target`
- 日期：2026-08-13
- 基线：`0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
- 关联：`project-red-blue/sessions/RB-ARCH-REFRAME-V1/`

## Context

`11 Logical Modules + 1 Architecture` 将 Product、Domain、Capability、Service、Data、Deployment 和 Team 阅读层混在编号模块中。它适合作为上一阶段的组织方式，但在 Python-only Microservice、Multi-Agent 和独立 Worker 目标下，会诱导三种错误：模块等于服务、模块等于目录、模块等于 Owner。

## Decision

新的 Canonical Taxonomy 按问题而不是编号组织：

```text
docs/project/
├─ facts/                         What actually happened?
├─ architecture/                 How do the layers fit? (four files only)
├─ product/product-architecture.md
├─ domain/legal-domain-model.md
├─ domain/domain-state-lifecycle.md
├─ agents/agent-platform.md
├─ agents/multi-agent-runtime.md
├─ knowledge/knowledge-evidence-architecture.md
├─ services/service-architecture.md
├─ data/data-ownership-and-recovery.md
├─ security/security-architecture.md
├─ eval/legal-eval-and-benchmark.md
└─ deployment/microservice-deployment.md
```

每份 Canonical Document 必须声明：Canonical Question、Owner、Canonical Facts、输入/输出、依赖、替代关系、Current/Target/Gap/Future、验证入口。文档只引用其他 Owner 的事实，不复制状态机、对象或服务清单。

| 文档 | Canonical Question | Owner |
|---|---|---|
| Product | 用户工作、入口、Review 和 WorkProduct 是什么？ | Product/Domain Surface |
| Domain | 法律业务世界的对象、身份、版本和 mutation authority 是什么？ | Platform Domain |
| Agents | Agent 怎样计划、执行、组合和协作？ | Agent Runtime |
| Knowledge | 文档怎样变成可引用证据？ | Knowledge |
| Services | Logical capability 怎样形成独立部署边界？ | Service Architecture |
| Data | 事实在哪里、谁拥有、如何一致和恢复？ | Data/Infrastructure |
| Security | 谁可以做什么，如何隔离和审计？ | Security Decision Owner |
| Eval | 怎样证明质量、效率和安全？ | Eval/Observability |
| Deployment | 服务怎样运行、扩缩容、升级和故障隔离？ | Deployment/SRE |

`docs/project/architecture/` 继续严格只保留 `README.md`、`architecture.md`、`architecture-views.md`、`architecture.html`；专题文档不得塞入该目录。

## Legacy Disposition

旧 `docs/project/modules/01..11` 不再是 Canonical Target。它们保留在 current tree 作为 `Superseded` 迁移材料/兼容路径，正式入口和 verifier 不再把它们视为设计事实源；后续可在历史摘要和 Git commit 可追溯条件下归档原始内容。任何旧文档与新 Taxonomy 冲突，以本 ADR、新专题文档和 Owner Registry 为准。

## Reading Paths

- Product：`docs/README.md → architecture.md → product → domain`
- Agent：`architecture → domain → agents → services → data/security`
- Knowledge：`domain → knowledge → agents → eval`
- Backend：`domain → services → data → security → deployment`
- SRE：`services → data → deployment → eval`

## Consequences

正面：读者按问题定位事实；Product/Domain/Logical Capability/Physical Service/Deployment 分离；可以从 8 个逻辑领域形成 5 个服务和多个 worker，不制造重复 Canonical State。

负面：需要更新 README、AGENTS、`.agent/system.yaml`、verifier、tests、QA links、old module status 和所有内部引用；迁移期间旧路径只能作为明确的 Superseded reference。

## Verification

Taxonomy verifier 必须检查：architecture 目录四文件、canonical files all exist、每份文档有唯一 Question/Owner/Current-Target boundary、服务数量不被旧 module count 约束、旧模块被标记 Superseded、内部链接无 broken link、没有重复 canonical ownership。
