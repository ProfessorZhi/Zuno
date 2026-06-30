# PHASE09 Runtime Upgrade Integration

Program: `zuno-eight-deliverables-full-realization-v1`
status: planned

## 为什么

前面各层如果不进入 GeneralAgent 主路径，只会成为漂亮 facade。最终必须形成清晰的 `prepare_context -> agent_loop -> post_turn_commit` 运行链，同时保持现有 API 和兼容边界。

## 范围

覆盖交付物：

- 6. 完善的 Zuno 目标架构。
- 7. 清晰干净的代码和目录。
- 8. 一致性与验证系统。

主要目标：

- GeneralAgent runtime path 的小步集成。
- 六层目录的真实 owner 收口。
- Context、Capability、Knowledge、Trace、Memory 的协作边界。
- 必要时补前端只读 trace 展示，但不默认改产品 UI。

## 执行步骤

1. 先做只读 runtime call-chain 审计，确认最小集成点。
2. 将 mode router、context builder、tool selector、knowledge retrieval、trace hooks 接入同一 runtime contract。
3. 保留旧 import 和 API compatibility。
4. 增加 integration tests、runtime smoke tests、eval baseline comparison。
5. 同步 docs current/target 状态。

## 验收

- Runtime path 能展示完整 context、retrieval/tool、answer、post-turn evidence。
- 六层目录不是空壳，关键 owner 有测试。
- 不把未完成 feature 宣称为 Current。
- full focused test stack 通过。

## PR 边界

必须按小切片推进，不做不可审查的大包重写。共享核心文件由主线程集中审查。
