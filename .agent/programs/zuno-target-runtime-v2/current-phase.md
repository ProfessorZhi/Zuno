# 当前 Phase

## 状态

当前可执行 Agent 程序。

Phase 00-04 已完成并归档到：

- `docs/history/programs/zuno-target-runtime-v2/`

## 当前焦点

文档中文化、入口收敛和仓库卫生是打开下一个 runtime phase 前的闸门。这个闸门提交并推送后，下一个可执行 runtime phase 是：

```text
Phase 05：记忆引擎
```

Phase 05 必须从现有最小 `ContextOrchestrator` 基础出发，只实现聚焦的记忆切片。除非代码和测试已经证明，不要声称成熟记忆产品行为已经完成。

## 已完成切片

- Phase 00：当前状态闸门。
- Phase 01：active V2 program setup。
- Phase 02：模块边界审计和验证器。
- Phase 03：第一个低风险后端边界移动。
- Phase 04：最小 ContextOrchestrator runtime。

## 后续 Runtime 目标

按线性顺序执行：

1. Phase 05：Memory Engine。
2. Phase 06：Capability / Tool Retrieval。
3. Phase 07：Knowledge Retrieval / Fusion。
4. Phase 08：GeneralAgent LangGraph Runtime。
5. Phase 09：Product Boundary / Trace / Eval Closure。

这些都是 Target，直到每个切片被代码和聚焦测试证明。

不要在 Phase 05 没有聚焦测试、文档边界同步和收口证据前打开 Phase 06。不要在能力选择没有稳定 ToolCard trace 前打开 Phase 07。不要在 retrieval/fusion trace 稳定前打开 Phase 08。
