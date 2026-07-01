# Agent 架构工作区

`.agent/architecture/` 现在只保留 Agent 维护架构时需要的最小入口，并与 `docs/architecture/` 保持同名镜像。

PHASE12 已完成 release closure；本目录继续跟随 `docs/architecture/architecture.md` 刷新 Agent 侧镜像和 HTML，不单独承载事实。PHASE02-PHASE11 的已验证 runtime / contract / UI 事实可以写入 Current；未实现的生产级 LangSmith、online eval、sandbox runtime、credential broker 和 production Desktop 闭环仍保持 Target。

当前没有 active program。最近完成并归档的 program 是 `zuno-target-architecture-runtime-full-implementation-v1`；后续仍只有在真实 API / runtime / UI 路径、focused tests、trace / eval 或 verifier 证明后，才把 Target 能力推进到 Current。生产成熟度边界由 `docs/architecture/production-readiness.md` 维护。

## 当前前台

```text
.agent/architecture/
  README.md
  architecture.md
  architecture.html
```

`architecture.md` 是 Agent 侧总架构维护镜像，必须与正式人类文档 `docs/architecture/architecture.md` 完全一致。`architecture.html` 是 Agent 侧 HTML 镜像，必须与 `docs/architecture/architecture.html` 由同一 Markdown 源生成。

## 已归档旧工作集

以下旧工作集已经被 `docs/architecture/architecture.md`、`.agent/architecture/architecture.md`、`docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html` 吸收：

- 旧 near-term 工作集
- 旧 future 工作集
- 旧 decisions 工作集
- 旧架构索引
- 旧术语表

归档位置：

- `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/`

## 边界

- 正式人类架构结论进入 `docs/architecture/architecture.md`。
- Agent 侧架构文档不手写分叉，必须通过 `python tools/agent/render_architecture.py --write` 同步。
- 图形化展示由 `docs/architecture/architecture.md` 生成到两个 HTML：`docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html`。
- 执行计划进入 `.agent/programs/`。
- Agent 操作规则、地图和验证清单进入 `.agent/references/`。
- 不要把已归档的旧工作集重新放回 `.agent/architecture/`，除非先打开新的架构重组 program 并同步 verifier / tests。
