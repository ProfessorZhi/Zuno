# Reset Plan

## Phase A — Red / Blue Workspace Reset

```text
inventory                 COMPLETE
immutable session check   COMPLETE
old protocol archive      COMPLETE
minimal active entry      COMPLETE
routing synchronization   COMPLETE
reset verifier            COMPLETE
```

归档解决的是 active/history 混淆，不是删除历史。旧协议仍可通过 `05-red-blue/history/` 和
不可变 Session 追溯。

## Phase B — Canonical Architecture Readability Refoundation

```text
reader compass            COMPLETE
History/Current/Target    EXPLICIT
domain/runtime boundary   EXPLICIT
logical/physical boundary EXPLICIT
replacement conditions    EXPLICIT
human readability checks  RUN_REQUIRED
```

本阶段不新增模块、服务、Provider、Runtime 或 Domain Object。它只把现有 Target baseline
组织成“问题 → 边界 → 场景 → 失败 → 替代 → 反转条件”的可读路径。

## Exit condition

可读性验证通过后，状态仍是 `ACTIVE_PROTOCOL: NONE`。只有用户另行激活并设计 VNext Protocol，
才可以创建新的 Red/Blue Session。Round-007 不由本计划启动。
