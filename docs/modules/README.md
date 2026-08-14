# 模块设计入口

status: `MODULE_BOUNDARY_NOT_FROZEN`

本目录预留给总体架构稳定后的逻辑模块设计。它不是旧的 11 模块目录恢复，也不表示当前已经确定模块数量、服务数量或部署数量。

## 当前边界

```text
FINAL_MODULE_COUNT = NOT_DECIDED
MODULE_BOUNDARIES = NOT_FROZEN
MODULE_DOCUMENTS = NONE
```

当前只维护本 README。模块文档必须在总体架构和人工 Red/Blue 复核形成稳定责任边界后，经明确决策再建立。

## 模块文档必须回答

- 模块拥有哪类状态和事实；
- 输入、输出和跨模块 Contract 是什么；
- 正常流程、失败、重试、恢复和对账如何闭环；
- 为什么需要独立模块，而不是已有 Library、Worker 或 Provider；
- 如何由代码、测试、Trace、Eval 或运行证据证明；
- 何时可以合并、替换、外置或删除。

总体跨层关系仍由 [`../architecture/architecture.md`](../architecture/architecture.md) 负责；模块文档不得在这里创建第二套全局架构事实。模块的 Current / Gap 对照必须引用 [`../facts/README.md`](../facts/README.md) 和 [`../evidence/`](../evidence/README.md)，不得把 Target 当作 Current。
