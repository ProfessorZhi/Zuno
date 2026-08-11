# 文档同步 Skill

当任务触碰 `docs/`、`.agent/`、AGENTS.md、README、架构、状态、ADR、治理或术语边界时使用。

## 唯一正式事实源

```text
docs/project/             = Zuno 项目知识入口
docs/project/facts/       = Current facts / UNKNOWN / history evidence
docs/project/architecture/ = 跨层总架构与图展示配对（固定四文件）
docs/project/product/     = 产品任务与外部 Host
docs/project/domain/      = 法律业务事实、版本和生命周期
docs/project/agents/      = Agent、Capability、Skill 与 Multi-Agent Runtime
docs/project/knowledge/   = Knowledge、Evidence、Retrieval、Graph Projection
docs/project/services/    = Logical Capability 到 Physical Service 的边界
docs/project/data/        = 数据 Ownership、一致性和恢复
docs/project/security/    = 权限、隔离、审计和安全可验证性
docs/project/eval/        = 法律质量、效率和复杂度 Benchmark
docs/project/deployment/  = Python Microservice 运行、扩缩容和部署 Profile
docs/project/modules/     = 上一阶段 11 模块的 Superseded 迁移材料
```

专题文档回答唯一 `canonical_question`；总架构只组合跨层关系。`.agent/` 只保存路由、Program、模板和验证器，不保存架构正文镜像。

## 正式入口与阅读顺序

```text
Product:  docs/project/README.md → architecture → product → domain
Agent:    architecture → domain → agents → services → data/security
Knowledge: domain → knowledge → agents → eval
Backend:  domain → services → data → security → deployment
SRE:      services → data → deployment → eval
```

工程实现/审查继续读取 ADR、共享 Contract、Status/Evidence 和 active Program。`Current` 必须有代码、Migration、Test、Trace 或 Eval 证据；Target/Hypothesis 不得偷换成 Current。

## Canonical taxonomy 路由

| Canonical Question | 正式文档 | Owner |
| --- | --- | --- |
| 产品任务、用户和 Host | `docs/project/product/product-architecture.md` | Product Owner |
| 法律业务世界是什么 | `docs/project/domain/legal-domain-model.md` | Domain Owner |
| Domain State 如何版本化和失效 | `docs/project/domain/domain-state-lifecycle.md` | Domain Lifecycle Owner |
| Agent 如何执行和协作 | `docs/project/agents/agent-platform.md` | Runtime Owner |
| Multi-Agent 的层级和边界 | `docs/project/agents/multi-agent-runtime.md` | Multi-Agent Owner |
| 信息如何成为证据 | `docs/project/knowledge/knowledge-evidence-architecture.md` | Knowledge Owner |
| 为什么是这些服务 | `docs/project/services/service-architecture.md` | Service Boundary Owner |
| 谁拥有数据、如何恢复 | `docs/project/data/data-ownership-and-recovery.md` | Data Owner |
| 谁可以做什么、如何验证安全 | `docs/project/security/security-architecture.md` | Security Owner |
| 怎样证明质量和效率 | `docs/project/eval/legal-eval-and-benchmark.md` | Eval Owner |
| 服务如何运行和扩缩容 | `docs/project/deployment/microservice-deployment.md` | Deployment Owner |

## 同步规则

架构语义变化时同步 `architecture.md`、`architecture-views.md`、`architecture.html`；专题事实只改其 Owner 文档。服务、Domain、Runtime、Checkpoint、Tool Effect、Security 和 Eval 不能在多个文档各自定义。

## Focused verification

```powershell
git diff --check
python tools/scripts/verify_architecture_document_set.py
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_red_blue_session.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```
