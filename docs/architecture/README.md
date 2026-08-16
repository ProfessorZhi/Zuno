# Zuno 总体架构文档

`docs/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## 总体架构回答什么

总体架构回答的是：Zuno 怎样把法律领域状态、知识与证据、执行控制、安全、外部效果和可验证交付组合成一套可以恢复、替换和简化的目标架构。

Round 02 已完成，总体 Target Architecture（目标架构）和九个 Logical Responsibility Modules（逻辑责任域）已经冻结。九个责任域是事实和职责边界，不是九个进程、九个数据库或九个微服务。Platform / Infrastructure（平台与基础设施）继续是责任层，Memory / Context（记忆与上下文）继续是可选 Provider 边界。

## 现在进行到哪里

总体架构冻结后，九篇模块正文已经形成 **Design Baseline V1（设计基线 V1）**。这表示模块的主要问题、Owner、跨模块 Contract、状态族、失败、恢复、安全和持久化边界已经可以作为详细设计的共同起点，但还没有冻结所有字段、enum、数据库表、API 或 Migration。

当前按照依赖逐步深化：

```text
当前：02 法律领域与工作成果 + 03 知识与证据
下一步：08 安全与治理 + 06 工具运行与外部效果
随后：05 专业能力与技能 + 04 智能体运行与控制
再后：07 模型网关 + 09 可观测性与评测
最后：01 应用与集成
```

这个顺序先把“什么是正式业务事实、什么只是可重建知识”讲清楚，再进入安全副作用和智能执行。它是设计依赖，不是运行时调用顺序，也不是部署拓扑。

当前治理状态：

```text
overall_architecture: ROUND_02_FROZEN
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

## 阅读顺序

第一次阅读只读 [`architecture.md`](./architecture.md) Part A。一个不了解 Zuno 的高级工程师应当能够只靠 Part A 解释：为什么需要这套架构；简单问答为什么应该保持简单；复杂法律分析怎样形成正式工作成果；新证据怎样使旧结果失效；外部 POST 超时为什么不能盲目重试；Domain Commit 和 Runtime Checkpoint 不一致时怎样恢复；九个责任域为什么这样分。

如果还不了解项目为什么存在，先读 [`../project/`](../project/README.md)。需要实现、测试或审查时，再读 Part B。总体架构读懂以后进入 [`../modules/README.md`](../modules/README.md)，再读对应模块 Part A / Part B、相关 [`../decisions/`](../decisions/README.md) ADR 和 [`../evidence/`](../evidence/README.md)。

Part A 采用中文优先：普通概念能用中文清楚表达时不用多余英文；确实需要代码、框架或正式 Contract 名称时，第一次出现使用 `English（中文）`，后续优先用中文或正式标识。

## 文件职责

- `architecture.md`：跨层 Target、九个责任域、全局不变量、跨模块 Contract、状态、失败和恢复。
- `architecture-views.md`：总体架构的 Mermaid 图源，只做图形表达，不拥有第二套架构事实。
- `architecture.html`：图源展示入口，不维护平行语义。
- `README.md`：目录边界、状态和阅读入口。
- `../project/`：项目为什么存在、开发背景和团队故事，不拥有 Target 架构。
- `../modules/`：九个责任域的模块 Design Baseline V1 和后续 Deep Design。
- `../decisions/`：长期有效且具有反转成本的 ADR。
- `../evidence/`：Current 的代码、测试、Migration、Trace、Eval 和运行证据。
- `../history/red-blue/`：架构质询和裁决历史，只解释“为什么”，不拥有当前 Target。

## 一致性规则

总体架构是当前 Target 的整合表达；模块文档只能细化它，不能局部改写九模块 Owner、Canonical Kernel、Formal Admission、Knowledge / Domain authority、Retry / Replan / Reconcile 或安全政策 Owner。较早 ADR 的宽泛措辞如果已被后续 ADR 明确 supersede / refine（取代 / 细化），按后续决定解释。

如果模块深化发现必须改变这些跨层语义，应停止局部设计并记录 Architecture Gap，而不是把新决定藏进 Part B、数据库字段或代码实现。

## 维护与验证

跨层含义变化时修改 `architecture.md`；模块内部设计进入 `../modules/`；图形关系变化时同步 `architecture-views.md` 与 `architecture.html`。当前常用验证：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

不得创建第五个架构文件、`.agent/architecture/` 或 `.agent/modules/` 镜像，也不得建立第二套 Domain / Runtime / Service / State registry。
