# 当前程序

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

## Program 3 定义修正

Program 3 没有结束。之前归档的 PHASE01-05 只是 first slice，完成了审计、docs hygiene、六层迁移计划、六层 README 和 repo hygiene guardrails。

前置程序状态：

- `zuno-workflow-doc-system-v1`：已完成并归档。
- `zuno-target-architecture-refresh-v1`：已完成并归档。

新的 Definition of Done 是：

```text
第一次打开 VS Code / Explorer 时，src/backend 目录也要清爽。
```

这意味着 Program 3 继续处理 backend physical layout cleanup：解释或收拢 `fastapi_jwt_auth`，降低 `src/backend/zuno` 顶层目录拥挤感，把旧 runtime 目录逐步靠近 `api / agent / memory / capability / knowledge / platform` 六层表达。

## 当前 Phase

- `PHASE06_backend-directory-clarity-audit.md`：first slice complete。已盘点 `src/backend` 和 `src/backend/zuno` 顶层目录。
- `PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`：first slice complete。已退休 `src/backend/fastapi_jwt_auth` 顶层 compatibility shell，runtime 改用 `zuno.compatibility.vendor.fastapi_jwt_auth`。
- `PHASE08_backend-physical-cleanup-slices.md`：active。当前从文档/guardrail 进入真正物理迁移。本轮改为挂机模式，由主线程统一处理 resources / compatibility 物理迁移和验证收口。

## 已完成并归档的 Program 3 first slice

- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md`

## 后续队列

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

## 当前边界

- 不开新 program；这是 Program 3 definition 修正后的 continuation。
- 不把 PHASE01-05 搬回 active 前台，它们是 first slice 历史证据。
- 不做无测试的大搬家；每次目录移动都必须有 import / repo structure / focused tests。
- 不删除 `fastapi_jwt_auth`，除非先证明 public import 和兼容测试可以安全迁移。
