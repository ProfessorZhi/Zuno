# 任务路由 Skill

## When To Use

当任务范围、路径、模块 owner 或先读文件不确定时使用本 skill。它只解决“走哪条路”，不替代具体执行 skill。

## Mental Model

```text
user task
  -> classify surface
  -> read required truth
  -> select local skills
  -> select templates only if output skeleton is needed
  -> select focused verify
  -> stop if forbidden path is required
```

## Current Truth

`.agent/system.yaml` 是机器可读路由，本文是人工可读路由。二者必须保持一致：路径先映射到 skills，再映射到 docs_sync、templates 和 verify。

## Target Direction

后续 PHASE03 可以把部分路由检查迁移到 `tools/agent` 或 `tools/verify`，但当前 `.agent/scripts` 仍是过渡期验证器位置。

## Must Preserve

- 目标不清时先做只读审计，不修改、不提交。
- 文档和工作流任务不得越界修改 runtime。
- 架构替换要保留 `Current / Target / Future / History` 边界。
- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html` 是 Target / Proposed 视觉蓝图，不是 Current proof。
- 历史材料进入 `docs/history/`，不要因为它过时就删除。

## Before Editing

1. 读 `AGENTS.md`。
2. 读 `.agent/system.yaml`。
3. 按下表选择 task route。
4. 读 route 对应 skills 和模块 `AGENTS.md`。
5. 如果 route 需要修改用户禁止路径，停止并返回证据。

## Allowed Changes

- 更新路由表、停止条件和 docs sync 规则。
- 同步 `.agent/system.yaml`、`.agent/references/README.md`、`workflow.md`、`verification-map.md`。
- 为新 route 增加最小必要测试或 verifier 词条。

## Forbidden Changes

- 不在本文写长目标架构正文。
- 不把一次性调查流水账写成本地 skill。
- 不把 Java、microservices、event workers 或 multi-agent mode 当作近期实现 route。
- 不恢复 `.agent/skills/` 或 `.agent/workflows/`。

## Route Table

| 任务类型 | 必读 skills / docs | 执行流程 |
| --- | --- | --- |
| 范围不清、只读盘点 | `docs/architecture/*`、`docs-map.md`、`code-map.md` | 只读审计；输出范围、证据、建议下一步 |
| 文档、`.agent`、references、history | `workflow.md`、`docs-map.md`、`verification-map.md`、`known-pitfalls.md` | 文档维护流程；同步 verifiers/tests |
| 目录移动、归档、ignore、缓存清理 | `workflow.md`、`docs-map.md`、`code-map.md`、`known-pitfalls.md` | 仓库卫生流程；先搜引用再移动 |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md`、`verification-map.md` | 前端变更流程 |
| `src/backend/zuno` | `src/backend/zuno/AGENTS.md`、`runtime-call-chain.md`、`code-map.md` | 后端变更流程 |
| API / DTO / 前后端 contract | `code-map.md`、`runtime-call-chain.md`、模块 `AGENTS.md` | API contract 流程 |
| 架构替换、GraphRAG 边界、仓库布局 | `.agent/architecture/near-term/*`、`.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`、`workflow.md`、`docs-map.md` | 架构重构流程；Current/Target 分开 |
| eval tooling / datasets / metrics | `tools/evals/zuno/AGENTS.md`、`verification-map.md` | eval 变更流程 |

## Common Failure Patterns

- 直接按文件名猜 owner，跳过模块 `AGENTS.md`。
- 文档任务顺手改 runtime，让验证范围膨胀。
- 只改 README，不同步 maps、verifier、tests。
- 把 archived program 的旧 phase 编号恢复成 active program 编号。

## Debug Playbooks

- 路由冲突：以用户允许/禁止范围为最高约束，再以 `AGENTS.md` 和 `.agent/system.yaml` 为准。
- 路径属于多个 route：选择 blast radius 更小的 route；需要代码变更时再读代码。
- 验证要求修改禁止路径：停止，给出失败命令和最小证据。

## Focused Tests

```powershell
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py -p no:cacheprovider
```

## Docs Sync

修改本文后检查：

- `.agent/system.yaml`
- `.agent/references/README.md`
- `.agent/references/workflow.md`
- `.agent/references/docs-map.md`
- `.agent/references/verification-map.md`
- `AGENTS.md` 任务路由段落是否仍准确

## Lessons Learned

路由文件的职责是减少决策分叉，不是收纳所有知识。复杂事实应进入对应 skill、正式 docs 或 history。
