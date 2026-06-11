# Zuno Refactor Execution Plan

## Current Status Update (2026-06-11)

- `Phase 1` completed on top of `origin/main`.
- `Phase 2` completed on top of the updated `main`.
- `Phase 3` is completed on top of the updated `main`.
- `Phase 4` is completed on top of the updated `main`.
- `Phase 5` is completed and already merged to `main`.
- `Phase 6` is completed under the new serial ledger.
- `Phase 7` is the current serial phase.

当前 `Phase 6` 的判断口径也已经更硬：

- 不再沿用早期“foundation 节点已经单独落地”的假设
- 直接以当前 `main` 基线为准
- 凡是当前 `Phase 6` 入口在 `main` 上仍然实际依赖的 entrypoint / runtime foundation / verification test / node-op 文档脚本，都属于真实 `Phase 6` bundled node

当前 `Phase 6` bundle 统一用下面这组命令观察和验收：

- `python tools/scripts/preview_phase6_bundle_scope.py --groups`
- `python tools/scripts/preview_phase6_bundle_scope.py --summary`
- `python tools/scripts/preview_phase6_bundle_scope.py --group logical_phase6_delta`
- `python tools/scripts/preview_phase6_bundle_scope.py --group runtime_foundations --stat`
- `python tools/scripts/preview_phase6_bundle_scope.py --dry-run`
- `python tools/scripts/preview_phase6_bundle_scope.py --stage-command`
- `python tools/scripts/verify_phase6_bundle_ready.py`

## 这份文档的职责

这份文档只回答两件事：

1. 新的 `Phase 1-7` 应按什么顺序线性推进
2. 每个 phase 到什么证据强度才算真正关闭

它是当前仓库的 phase 真相来源。
如果其他历史文档和这里冲突，以这里为准。

## 串行执行规则

后续 phase 必须严格串行：

1. `Phase N` 未关闭，不进入 `Phase N+1`
2. 单个 phase 内部任务可并行，但 phase 之间不可并行
3. 每个 phase 结束后必须先跑本阶段最小测试
4. 每个 phase 结束后必须同步 `docs/architecture/` 和 `README.md`
5. 每个 phase 结束后必须作为独立 GitHub 节点推送，再并回 `main`

默认节奏：

```text
phase 内并行任务
  -> 跑本阶段最小验证
  -> 回看 README / docs / phase 状态
  -> 单独推 GitHub
  -> 合并回 main
  -> 再进入下一个 phase
```

## 最终共同目标

所有 phase 最终都服务于同一目标：

```text
形成一个本地优先的 Agent 工作台，
它拥有清晰项目结构、清晰分层边界、
深度 LangGraph + GraphRAG 主线、
GraphRAG 动态更新、普通/增强两档检索、
本地 embedding、本地评测、自动化测试，
以及正式 GitHub 展示面。
```

## Phase 1：运行时收口与可运行恢复

目标：

- `zuno` 成为主运行时入口
- bridge / alias / runtime contract 收口
- 启动链路恢复稳定

建议最小测试：

1. `pytest -q tests/test_zuno_public_entrypoints.py`
2. `pytest -q src/backend/agentchat/test/test_zuno_alias_imports.py`
3. `pytest -q tests/test_zuno_runtime_chain_guard.py`
4. `import zuno.main` smoke

完成判定：

1. 最小测试通过
2. `zuno.main` 可导入并持有最小 `app`
3. 高价值 alias / contract 不再漂移
4. README 与架构文档不再把旧桥接当主路径

GitHub 节点：

- 作为“运行时收口与可运行恢复”独立推送

## Phase 2：项目文件夹与结构硬治理

目标：

- 根目录主骨架清楚
- `src/backend`、`src/frontend`、`apps/desktop` 角色清楚
- 发布边界、私有边界、本地边界清楚

建议最小测试：

1. `python tools/scripts/verify_repo_structure.py`
2. `pytest -q tests/test_repo_structure_consistency.py`
3. `pytest -q tests/test_publish_boundary.py`

完成判定：

1. 文件夹结构发生真实整理
2. 根目录主骨架清楚
3. 主要目录职责稳定可解释
4. README、架构文档、publish boundary 已同步
5. 本阶段最小测试通过

GitHub 节点：

- 作为“项目文件夹与结构硬治理”独立推送

## Phase 3：文档与展示面硬收口

目标：

- 首次阅读路径稳定成单一路线
- README、架构文档、开发文档、plans/specs 口径一致
- 过时、冲突、过早暴露的展示叙事不再干扰主阅读路径

当前推荐公开阅读路径：

1. `README.md`
2. `docs/README.md`
3. `docs/architecture/README.md`
4. `docs/architecture/specs/README.md`
5. `docs/architecture/plans/README.md`
6. `docs/architecture/plans/current-phase-audit.md`

建议最小测试：

1. `python tools/scripts/verify_docs_surface.py`
2. `pytest tests/test_docs_surface_consistency.py`
3. `pytest tests/test_publish_boundary.py`

完成判定：

1. 公开入口文档已形成稳定主阅读路径
2. 过时文档和冲突表述已清理、降级或移出主路径
3. README / docs / plans / specs 口径一致
4. 文档与发布边界相关最小检查通过

GitHub 节点：

- 作为“文档与展示面硬收口”独立推送

## Phase 4：分层架构与运行时边界强化

目标：

- 控制层 / 服务层 / DAO / 基础设施边界更硬
- 高价值运行时路径减少跨层缠绕

建议最小测试：

1. 高价值 runtime contract 测试
2. 最小 import / service smoke
3. publish boundary / layering 守门测试

完成判定：

1. 分层边界已在高价值代码路径上体现
2. runtime / service / dao / infra 主要耦合点被压缩
3. 文档与代码对同一边界说法一致
4. 本阶段最小分层测试通过

GitHub 节点：

- 作为“分层架构与运行时边界强化”独立推送

## Phase 5：LangGraph + GraphRAG 主线深化

目标：

- `LangGraph` 成为主运行时骨架
- `GraphRAG` 动态更新主线落地
- 普通 / 增强两档检索稳定

建议最小测试：

1. retrieval / graph / runtime 集成测试
2. `GraphRAG` dynamic update 测试
3. `Domain Pack` runtime 测试

完成判定：

1. `LangGraph` 已成为核心运行时主线
2. `GraphRAG` 动态更新主线落地
3. 两档检索体验稳定
4. 本阶段最小集成测试通过

GitHub 节点：

- 作为“LangGraph + GraphRAG 主线深化”独立推送

## Phase 6：评测与证据链固化

目标：

- 本地 embedding、本地评测、compare matrix、trace、citation 形成稳定证据链
- 阶段文档、bundle 预览脚本、readiness verifier 和真实代码范围一致
- 从当前 `main` 基线上形成一个可独立推 GitHub 的 `Phase 6` 节点

建议最小测试：

1. `pytest -q src/backend/agentchat/test/test_contract_eval_runner.py src/backend/agentchat/test/test_rag_eval_local_scheme.py src/backend/agentchat/test/test_stackless_compare_matrix.py src/backend/agentchat/test/test_rag_eval_local_launcher.py`
2. `python tools/scripts/preview_phase6_bundle_scope.py --summary`
3. `python tools/scripts/verify_phase6_bundle_ready.py`

完成判定：

1. 本地 embedding + 本地评测链路稳定
2. compare matrix 可复现
3. 自动化测试、README、`docs/architecture/`、bundle verifier 对同一套证据链说法一致
4. 当前 `main` 基线下实际依赖的 eval entrypoints / runtime foundations / verification tests 已作为同一个节点收口
5. 本阶段最小测试通过
6. 该节点已独立推 GitHub 并合回 `main`

GitHub 节点：

- 作为“评测与证据链固化”独立推送

## Phase 7：面试前总收口

目标：

- 代码、目录、文档、评测、展示面、讲解口径完全对齐

建议最小测试：

1. 最终 runtime smoke
2. 最终文档/展示面检查
3. 最终 publish boundary 检查

完成判定：

1. 前面各阶段成果口径一致
2. 公开展示面稳定
3. 文档、代码、评测、展示面统一
4. 本阶段最终检查通过

GitHub 节点：

- 作为“面试前总收口”独立推送
