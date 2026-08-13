# 项目状态入口

`docs/project/status/` 只回答当前仓库和 Target 的状态问题，不重述历史故事，也不把目标文档当作运行证据。

| 文档 | Canonical Question |
| --- | --- |
| [`current-reality.md`](current-reality.md) | 当前仓库实际有什么证据？ |
| [`target-status.md`](target-status.md) | Target、Hypothesis 和 Future 分别处于什么状态？ |
| [`production-readiness.md`](production-readiness.md) | 生产 readiness 是否已经证明？ |

Current 需要代码、Migration、Test、Trace、Eval 或真实运行证据；Target 需要 accepted ADR 和架构文档；Hypothesis 需要 Benchmark、Spike、Security Evidence 或 User Validation；没有证据时保持 `UNKNOWN` / `NOT_ESTABLISHED`。

此目录不拥有业务 Domain State、Runtime Checkpoint 或架构 Contract；这些跨层关系由 [`../architecture/architecture.md`](../architecture/architecture.md) 说明。
