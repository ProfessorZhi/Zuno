# Zuno Architecture

`docs/architecture/` 是 Zuno **总体 Target Architecture** 的 Canonical Owner。目录入口与架构正文分开，避免 `README.md` 同时承担导航和完整教材正文。

## 阅读入口

- [`architecture.md`](./architecture.md) —— Human Narrative。先从简单方案进入，再沿材料版本、正式业务事实、长任务恢复、现实副作用和持续授权理解总体架构为什么形成。
- [`reference.md`](./reference.md) —— Engineering / Agent Reference。保存跨责任 Authority、Contract、Completion Proof、Recovery、Security、Persistence 和 Source Precedence。
- [`architecture-views.md`](./architecture-views.md) —— 架构视图与投影视角。
- [`architecture.html`](./architecture.html) —— 由总体架构文档生成的浏览版本。

第一次阅读的主线是：

```text
docs/project/README.md
→ docs/architecture/architecture.md
→ docs/modules/README.md
→ selected module README
→ docs/evidence/README.md
```

实现或架构审查任务则从 `reference.md` 下钻到 `docs/modules/*/reference.md`、ADR、Evidence 和代码。

## 事实边界

`architecture.md` 与 `reference.md` 共享同一个 Target Architecture Owner，但承担不同视图。前者负责因果叙事，后者压缩工程 Contract；两者都不能把 Project History、Current Evidence 或个人 Ownership 改写成 Target 的附属事实。

Current 是否已经实现某项设计，只由 [`docs/evidence/`](../evidence/README.md) 的代码、测试、Trace、Eval 或运行证据证明。模块内部责任进入 [`docs/modules/`](../modules/README.md)，长期设计理由进入 [`docs/decisions/`](../decisions/README.md)。
