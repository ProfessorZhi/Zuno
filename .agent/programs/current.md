# 当前程序

当前 active program：

```text
zuno-six-layer-internalization-v1
```

状态：active。

## 当前目标

Program 3 已完成 `src/backend/zuno` 顶层目录收口；当前 program 不再处理 root alias surface，而是让六层内部逐步长出可解释的目标层入口。

Program 3 固定的六层顶层仍是：`api / agent / memory / capability / knowledge / platform`。

本轮先做低风险 internalization：

- 不改 API 行为。
- 不改 DB schema。
- 不改 frontend。
- 不改 eval baseline。
- 不重写 GeneralAgent 主循环。
- 不删除旧 public import path。
- 只做无副作用 facade、薄入口、文档、测试和 verifier 可证明的边界推进。

## Active Phase

- `PHASE01_six-layer-current-inventory.md`：completed。
- `PHASE02_memory-layer-foundation-surfaces.md`：in progress。

## 当前事实

`src/backend/zuno/memory/` 已从只有 `README.md` / `__init__.py` 的纯 facade，推进为包含下列薄入口：

- `contracts.py`
- `store.py`
- `policy.py`
- `review.py`
- `retrieval.py`
- `rendering.py`
- `engine.py`

这些文件仍复用 `zuno.services.memory.layers` 的 foundation objects；物理实现位于 `src/backend/zuno/platform/services/memory/layers.py`。这不等于 production-grade memory extraction、retrieval、consolidation 或 Memory DB 已完成。

## 归档边界

最新完成 program 仍是：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 不能被改写成未完成；它完成的是 root / alias surface closure。当前 program 接续处理六层内部成熟化。
