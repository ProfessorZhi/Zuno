# Zuno Refactor Execution Plan

## Current Status Update (2026-06-11)

- `Phase 1` completed on top of `origin/main`.
- `Phase 2`: next serial phase.
- `Phase 3-7`: pending under the new serial ledger.

Latest `Phase 1` progress now verified in the repo state:

1. `src/backend/zuno/` is now present on the branch as the runtime-facing package root.
2. the public backend entrypoints now prefer `zuno.main:app`:
   - `README.md`
   - `infra/docker/Dockerfile`
   - `tools/scripts/start.py`
   - backward-compatible `src/backend/agentchat/main.py` CLI forwarding
3. Docker runtime/worker config now prefers the `zuno` path:
   - `infra/docker/docker-compose.yml`
   - `infra/docker/docker-compose.dev.yml`
   - `infra/docker/README.md`
4. runtime config discovery now prefers `ZUNO_CONFIG` and `zuno/config.yaml` while keeping fallback compatibility:
   - `src/backend/agentchat/settings.py`
5. the remaining high-value runtime manifests/configs now point to `zuno` entrypaths:
   - `src/backend/agentchat/config/mcp_server.json`
   - `src/backend/agentchat/tools/send_email/manifest.yaml`
6. the Phase 1 minimum verification set is green:
   - `pytest -q tests/test_zuno_public_entrypoints.py` -> `36 passed`
   - `pytest -q src/backend/agentchat/test/test_zuno_alias_imports.py` -> `7 passed`
   - `pytest -q tests/test_zuno_runtime_chain_guard.py` -> `2 passed`
   - minimal `import zuno.main` smoke -> `module_ok True`, `app_attr True`

## 目标

这份计划只回答一件事：

```text
从现在开始，Zuno 应该按什么线性 phase 往面试前目标推进，
并且每个 phase 结束时如何确认“真的完成了问题解决”，而不是只完成了文档表述。
```

这里不再沿用早期分散的 phase 口径。
从现在开始，统一使用新的 `Phase 1-7` 线性编号。

## 执行规则

后续 phase 必须线性推进，不并行推进多个 phase。

也就是说：

1. `Phase N` 完成前，不进入 `Phase N+1`
2. 单个 phase 内部的多个任务可以并行，只要最后一起收口验收
3. 每个 phase 结束后都必须先做一次和本阶段目标直接相关的简单测试
4. 每个 phase 结束后都必须同步 `docs/architecture/`、README，并单独推送 GitHub
5. 只有当本 phase 对应的问题真的被关闭，才允许切到下一 phase

这里的“简单测试”不是要求每次都跑全量大回归，而是要求至少有一轮最小验证。

默认节奏：

```text
phase 内任务并行推进
  -> phase 验收
  -> 跑本阶段简单测试
  -> 回看 docs/architecture
  -> 同步 README / 文档
  -> 单独推送 GitHub
  -> 再进入下一 phase
```

## 面试前最终目标

所有 phase 最终都服务于同一套目标架构：

```text
以 LangGraph 为核心运行时，
以 RAG / GraphRAG / Domain Pack 为知识主线，
具备 GraphRAG 动态更新、普通 / 增强两档检索体验、
本地 embedding、本地评测、自动化测试、
清晰项目结构、清晰分层边界和正式 GitHub 展示面的本地优先 Agent 工作台。
```

换句话说，面试前必须做到：

1. 深入运用 LangGraph，而不是停留在简单 LangChain agent 封装
2. 深入运用 GraphRAG，而不是只做概念演示或表层接入
3. 让代码结构、项目结构、评测证据、文档口径和 GitHub 展示面最终一致

## Phase 体系

### Phase 1：运行时收口与可运行恢复

目标：

- 把当前 rename / bridge / alias / runtime contract 尾巴收好
- 先让 `zuno` 主路径稳定跑起来
- 保证运行主入口、关键 import、关键 runtime contract 不再漂移

本 phase 内可并行任务：

- package / import / alias 收口
- launcher / Docker / config 路径同步
- README / docs 引用同步
- 最小启动链路 smoke 修复

必须解决的问题：

- `agentchat -> zuno` 深层 bridge 不能继续主导主阅读路径
- 关键公开入口必须优先指向 `zuno.*`
- 关键运行入口必须统一到 `zuno.main:app`

验收标准：

- `zuno` 主运行入口稳定
- 关键 import / alias contract 不再漂移
- 关键启动链路可以跑通
- 文档口径不再把旧桥接当主路径

建议最小测试集：

1. `pytest -q tests/test_zuno_public_entrypoints.py`
2. `pytest -q src/backend/agentchat/test/test_zuno_alias_imports.py`
3. `pytest -q tests/test_zuno_runtime_chain_guard.py`
4. 最小 `import zuno.main` smoke

只有同时满足下面四条，才能认为 `Phase 1` 完成：

1. 最小测试集通过
2. `zuno.main` 主路径可导入、可启动最小 app
3. 高价值 package / alias / runtime contract 基本收口
4. README 与架构文档不再把旧桥接当主路径

GitHub 节点：

- 作为“运行时收口与可运行恢复节点”单独推送

### Phase 2：项目文件夹与结构硬治理

目标：

- 真正整理项目文件夹，而不是只在文档里解释
- 明确根目录主骨架
- 明确正式项目结构、生成面、本地面、私有面的边界

本 phase 内可并行任务：

- 根目录清理与归类
- `src/` 层整理
- `backend / frontend / desktop` 边界整理
- `docs / tools / infra / tests` 归类整理
- 文档中的目录解释同步

必须解决的问题：

- 当前项目表面还是 `src + apps` 混合形态，但解释和实际整理还不够硬
- 根目录存在大量本地面 / 生成面，会干扰项目主视图
- `src/backend/zuno` 与 `src/backend/agentchat` 当前角色不够一眼看清

必须发生的实际整理动作：

- 根目录主骨架清晰化
- `src/backend` 下历史残留目录语义明确
- `src/frontend` 的正式源码层与生成层边界明确
- `apps/desktop` 与 `src/frontend` 的关系说明清楚
- `docs/architecture`、`docs/development`、`tools/`、`infra/`、`tests/` 各归其位

验收标准：

- 文件夹结构发生了可见整理，不只是文档改名
- 根目录与 `src/` 层的混乱入口明显减少
- 生成面 / 本地面 / 正式项目面三者边界清楚
- `src/backend/zuno` 主路径可见性更强
- 架构文档、README、publish boundary 与当前结构一致

建议最小测试集：

1. 结构一致性检查
2. publish boundary 检查
3. 最小 import smoke

只有同时满足下面五条，才能认为 `Phase 2` 完成：

1. 文件夹结构发生了真实整理动作
2. 根目录主骨架清楚
3. `src/backend`、`src/frontend`、`apps/desktop`、`docs/`、`tools/`、`infra/`、`tests/` 的职责稳定
4. 文档、README、publish boundary 已同步
5. 本阶段最小结构测试通过

GitHub 节点：

- 作为“项目结构硬治理节点”单独推送

### Phase 3：文档与展示面硬收口

目标：

- 让第一次看项目的人和面试官顺着主路径理解项目
- 不再被历史文档、重复说明、冲突表述带偏

本 phase 内可并行任务：

- README 重构
- docs 清理
- specs / plans / audit 口径统一
- GitHub 展示面优化

必须解决的问题：

- 同一件事在多份文档里重复、冲突或说法不一致
- 首次阅读路径不够硬，容易被历史文档拖走
- GitHub 展示面还不够像正式项目

验收标准：

- README、架构文档、开发文档口径一致
- 首次阅读路径清楚
- 过时文档不再干扰主阅读路径
- GitHub 展示面专业、稳定、面向公众

建议最小测试集：

1. 文档检查脚本
2. 最小发布边界检查

只有同时满足下面四条，才能认为 `Phase 3` 完成：

1. 公开入口文档已经形成主阅读路径
2. 过时文档和冲突表述已被清理或降级
3. README / docs / plans / specs 口径一致
4. 文档与发布边界相关最小检查通过

GitHub 节点：

- 作为“文档与展示面硬收口节点”单独推送

### Phase 4：分层架构与运行时边界强化

目标：

- 把“分层架构清晰、可扩展、可修改”这件事真正做硬
- 不只是写文档，而是让代码组织和运行时边界真正体现控制层 / 服务层 / DAO 层 / 基础设施层

本 phase 内可并行任务：

- backend 分层边界强化
- runtime contract 收紧
- knowledge / retrieval / workflow 编排边界强化
- 为未来微服务 / 云原生 / 异语言接入保留稳定边界

必须解决的问题：

- 有些运行时主路径仍然容易跨层耦合
- 文档里说分层清楚，但代码里不一定完全体现
- 后续 LangGraph / GraphRAG 深化前，运行时和服务层边界必须更稳

验收标准：

- 控制层、服务层、DAO 层、基础设施层边界清楚
- 高价值主链路不再随意跨层缠绕
- 架构文档里的分层说明能被代码结构印证

建议最小测试集：

1. 高价值 runtime contract 测试
2. 最小 import / service smoke
3. publish boundary / layering 守门测试

只有同时满足下面四条，才能认为 `Phase 4` 完成：

1. 分层边界已经在高价值代码路径上体现
2. runtime / service / dao / infra 主要耦合点已被压缩
3. 文档和代码对同一分层边界说法一致
4. 本阶段最小分层测试通过

GitHub 节点：

- 作为“分层架构与运行时边界强化节点”单独推送

### Phase 5：LangGraph + GraphRAG 主线深化

目标：

- 把文档里定义的那条主架构真正落到代码主链路里
- 深度用 LangGraph 和 GraphRAG，而不是表层接入

本 phase 内可并行任务：

- LangGraph workflow 深化
- GraphRAG 动态更新实现
- retrieval planner / orchestrator 收口
- Domain Pack 合同审查主链路深化
- 普通 / 增强模式体验固定

必须解决的问题：

- LangGraph 还没有在所有关键主流程上深度落地
- GraphRAG 动态更新还不够硬
- 普通 / 增强两档检索体验和底层能力包边界还不够稳定

验收标准：

- LangGraph、RAG、GraphRAG、Domain Pack 的主运行链路清楚稳定
- GraphRAG 动态更新不再停留在设计层
- 普通模式 / 增强模式两档体验稳定
- 合同审查场景能体现 Domain Pack + GraphRAG 的真实价值

建议最小测试集：

1. retrieval / graph / runtime 集成测试
2. GraphRAG dynamic update 相关测试
3. Domain Pack runtime 测试

只有同时满足下面四条，才能认为 `Phase 5` 完成：

1. LangGraph 已成为核心运行时主线
2. GraphRAG 动态更新主线已落地
3. 两档检索体验已稳定
4. 本阶段最小集成测试通过

GitHub 节点：

- 作为“LangGraph + GraphRAG 主线深化节点”单独推送

### Phase 6：评测与证据链固化

目标：

- 把“这套架构为什么有价值”证明出来，而不是只靠口头解释

本 phase 内可并行任务：

- local embedding / eval 流程打磨
- compare matrix 产出
- 指标报告整理
- trace / citation / grounding 证据整理

必须解决的问题：

- 目前还不能稳定、可重复地证明 GraphRAG、领域建模、增强模式的价值
- 需要本地 embedding、本地评测、五项指标、自动化测试和 failure case 一起形成证据链

验收标准：

- 指标能证明 GraphRAG 和领域建模价值
- 本地评测可以稳定复现
- 自动化测试与人工展示证据一致
- failure case 也能被解释

建议最小测试集：

1. local eval
2. compare matrix 生成
3. 指标汇总脚本

只有同时满足下面四条，才能认为 `Phase 6` 完成：

1. 本地 embedding + 本地评测链路稳定
2. 五项核心指标与 compare matrix 可复现
3. 自动化测试和展示证据一致
4. 本阶段评测测试通过

GitHub 节点：

- 作为“评测与证据链固化节点”单独推送

### Phase 7：面试前总收口

目标：

- 把前面所有成果统一成一个可以稳定讲解、稳定演示、稳定展示的版本

本 phase 内可并行任务：

- 最终 README / docs / architecture 收口
- 最终 smoke tests
- GitHub 展示面优化
- 面试讲解路径检查

必须解决的问题：

- 历史桥接、灰色地带入口、解释噪音仍可能影响最终讲解
- 需要把代码、文档、目录、评测、展示面完全对齐

验收标准：

- 架构能讲清楚
- 结构能讲清楚
- 文档、代码、评测、展示面口径一致
- 面试前公开版本可以稳定演示与讲解

建议最小测试集：

1. 最终 smoke tests
2. 关键主链路检查
3. 最终 publish boundary 检查

只有同时满足下面四条，才能认为 `Phase 7` 完成：

1. 面试讲解路径稳定
2. 公开展示面稳定
3. 代码、文档、结构、评测已统一
4. 最终总收口测试通过

GitHub 节点：

- 作为“面试前总收口节点”单独推送

## 当前阶段判断

按这套新编号体系，当前判断应改成：

- `Phase 1-4` 已完成并已有最小验收证据
- `Phase 5-7` 尚未正式完成

保守判断下，当前仍然更适合视为：

- 继续线性推进 `Phase 5`
- 不再回到“先确认 Phase 1 是否关闭”的旧阶段判断

当前仓库口径已经同步记录了 `Phase 1-4` 的关闭判断；后续重点是保持这些阶段的验收结果稳定，并继续推进 `Phase 5-7`。

## 推荐推进顺序

后续按这个顺序线性推进：

1. 先保持 `Phase 4` 验收结果稳定
2. 再完成 `Phase 5`
3. 再完成 `Phase 6`
4. 最后完成 `Phase 7`

原因很简单：

1. 系统先稳定跑起来，后面结构治理才不会反复返工
2. 文件夹结构先收硬，后面文档和展示面才有稳定对象
3. 文档和展示面先收硬，后面技术主线深化才不会被旧表述拖住
4. 分层边界先加强，后面 LangGraph + GraphRAG 深化才不会越做越乱
5. 技术主线深化和价值证明拆开，才能分别把“实现”和“证明”做扎实
6. 面试前总收口必须放最后，专门负责统一讲解口径

## 每个 Phase 完成后的固定动作

每个 phase 结束后，固定执行：

1. 跑本阶段简单测试
2. 回看 `docs/architecture/`
3. 同步 README / 文档
4. 单独推送 GitHub

## 大更新后的文档回看要求

每当完成一次较大的架构更新，至少要回看并同步下面这些文档：

- `docs/architecture/README.md`
- `docs/architecture/zuno_refactor_plan.md`
- 相关 `specs/*.md`
- 本执行计划

同步目标：

- 删除已经解决的问题
- 更新当前仍未完成的阶段判断
- 确保 phase、spec、README 口径一致
