# PHASE03：后端六层迁移计划
> 状态：pending。等待 PHASE01 审计结果后执行。

## 目标

把 `api / agent / memory / capability / knowledge / platform` 的物理迁移顺序和风险写清楚。

本 phase 重点解决用户指出的 `src` 目录杂乱问题。目标不是立刻大搬代码，而是形成可执行迁移计划：

```text
src/backend/
  zuno/
    api/
    agent/
    memory/
    capability/
    knowledge/
    platform/
```

`src/backend` 顶层除 `zuno/` 外，任何额外目录都必须被分类为：外部兼容包、临时 vendored 代码、测试夹具、历史残留或应迁移对象，并给出处理动作。

## 验收

每层都有迁移候选、禁止边界、focused tests、rollback plan。

输出至少包括：

```text
current path | target layer | move type | public API risk | tests | rollback
```
