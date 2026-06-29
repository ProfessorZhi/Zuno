# PHASE01 六层内部成熟度盘点

状态：completed

## 目标

确认 Program 3 完成的是 `src/backend/zuno` 顶层目录和 root alias surface closure，不把它误写成六层内部 runtime 成熟化已经完成。

## 当前事实

- `src/backend/zuno` 根目录只剩 `api / agent / memory / capability / knowledge / platform`、`__init__.py` 和 `main.py`。
- 六层内部仍然有不同成熟度：`memory/` 在本轮开始时只有 `README.md` 和 `__init__.py`，是最明显的纯 facade。
- 旧 public import path 仍必须可用，尤其是 `zuno.services.*`。
- 当前 program 只能做无副作用薄入口、测试和文档；不能重写 runtime 主循环、DB schema、API 行为或 eval baseline。

## 结论

下一步先从 `memory/` 开始，因为它是最小、最清楚、最能验证的内部成熟化切片。

## 验收

- `.agent/programs/current.md` 明确当前 active program。
- `.agent/programs/implementation-roadmap.md` 明确 Phase 从 1 重新开始。
- `docs/architecture/current-architecture.md` 区分 Program 3 root closure 和当前 internalization。
