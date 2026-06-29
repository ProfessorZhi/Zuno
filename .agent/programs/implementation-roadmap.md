# Zuno Repo Layout Cleanup V1

> 状态：active / definition revised。Program 3 first slice 已归档，当前从 `PHASE06` 继续。

Program ID：`zuno-repo-layout-cleanup-v1`

## Program 关系

- `zuno-workflow-doc-system-v1`：已完成并归档。
- `zuno-target-architecture-refresh-v1`：已完成并归档。
- `zuno-repo-layout-cleanup-v1`：当前 active / definition revised。
- `zuno-runtime-architecture-upgrade-v1`：queued draft / not active。
- `zuno-architecture-visuals-v1`：queued draft / not active。

每次新 program 都从 `PHASE01` 开始编号。本次从 `PHASE06` 继续，不是新开 program，而是 Program 3 first slice 归档后按用户反馈修正 Definition of Done。

本轮 continuation 的核心是 backend physical layout cleanup：目录本身要表达架构，文档只能解释边界，不能替目录背锅。

## 为什么重新打开 Program 3

用户反馈是准确的：PHASE01-05 让仓库规则、docs 和迁移计划变清楚了，但 `src/backend` 在 VS Code / Explorer 里仍然拥挤。当前已退休 `fastapi_jwt_auth` 顶层 compatibility shell，并把资源/兼容目录收敛到 `resources/` 与 `compatibility/`；`core`、`database`、`services`、`schema`、`tools`、`utils` 等旧 runtime 目录仍需后续小切片处理。

所以 Program 3 的 Definition of Done 改为：

```text
目录本身要表达架构；文档只能解释边界，不能替目录背锅。
```

## 目标

让 `src/backend` 和 `src/backend/zuno` 更接近成熟项目封面：

```text
src/backend/
  zuno/                 主 runtime 包

src/backend/zuno/
  api/
  agent/
  memory/
  capability/
  knowledge/
  platform/
  resources/
  compatibility/
  ...
```

其中 `...` 不能无限存在。每个额外目录必须被分类为：

- current required：当前必须存在，并有明确职责。
- compatibility shell：为了 public import 或历史配置暂留。
- migration source：未来要迁入六层的旧 runtime 源。
- local/generated：不该进入 repo 或不该出现在视野里。
- future retirement：需要单独计划退休。

## 当前边界

- 不开新 program；这是 Program 3 continuation。
- 不把 PHASE01-05 搬回 active 前台；它们保留在 `docs/history/programs/zuno-repo-layout-cleanup-v1/`。
- 不做无测试的大搬家。
- 不恢复 `fastapi_jwt_auth` 顶层 compatibility shell；runtime 使用 `zuno.compatibility.vendor.fastapi_jwt_auth`。
- 不把 runtime 架构升级、GraphRAG LLM extractor、frontend、eval closure 混进本 program。

## Phase

1. [PHASE06：Backend directory clarity audit](PHASE06_backend-directory-clarity-audit.md)
2. [PHASE07：FastAPI JWT compat retirement plan](PHASE07_fastapi-jwt-auth-compat-retirement-plan.md)
3. [PHASE08：Backend physical cleanup slices](PHASE08_backend-physical-cleanup-slices.md)

## 已完成 first slice

- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md`

## 验收标准

- `src/backend` 顶层只保留 `zuno/`；`fastapi_jwt_auth` 顶层 shell 的退休由测试和 verifier 固定。
- `src/backend/zuno` 顶层目录必须有 inventory 分类表和处理动作。
- 可立即安全清理的 generated/local 目录必须清理或进入 ignore/verifier。
- 不能马上搬的旧 runtime 目录必须有明确“迁入哪一层、何时迁、跑什么测试、如何回滚”。
- verifier / tests 必须能防止 Program 3 又被误判为 completed while still visually messy。
