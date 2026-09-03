# Architecture — 理想的 Zuno 应该怎样工作

`docs/architecture/` 描述设计阶段接受的总体 Target Architecture。这里不讲个人历史，也不把代码目录当架构；它从真实业务约束出发，解释一个长期法律智能工作系统应该保护哪些事实、怎样跨边界、失败后先相信谁。

## Human View

[`architecture.md`](architecture.md) Part A 是总体架构的主章节。第一次阅读沿同一个案件和故障场景往下走，不需要先背模块名：

```text
简单法律问答
→ 多材料、多版本、长期运行、正式结果和现实副作用出现
→ 不同类型的事实需要不同 Authority
→ 候选跨越边界成为更强语义
→ 责任域由这些长期事实自然产生
→ 正常任务流
→ crash / late result / authorization change / external timeout
→ recovery
→ complexity kill test
```

Part A 的目标是建立 mental model，也应能直接支撑系统设计面试。它可以有强观点和具体失败场景，但不能为了讲得漂亮制造 Current、Production 或个人 Ownership。

## Engineering / Agent View

机器先读 [`reference.md`](reference.md)，再进入 `architecture.md` Part B。总体 Part B 只保存跨模块 Authority、Contract、Completion Proof、Recovery、Version/Freshness、Security 和 Source Map；局部字段、状态机、事务和 Crash Window 下沉到 Module Part B/C。

```text
architecture/reference.md
→ architecture.md Part B
→ modules/reference.md
→ target module B/C
→ ADR
→ Evidence
→ code
```

## 模块数量不是文档先验

Documentation Architecture 不冻结“必须九个责任域”。当前 Target decomposition 可以继续使用现有九域作为已接受设计基线，但责任域数量必须由事实 Ownership、恢复边界、安全边界和演进成本推导。

未来如果 Architecture 证明某些责任可以合并，或者新的独立 Authority 必须拆出，应通过 Architecture + ADR 改变 decomposition。不要为了维持 01–09 编号或目录美观保留无价值边界。

## 这里拥有和不拥有的事实

Architecture 拥有 Target 的跨模块语义，例如：

- 哪类事实由谁最终证明；
- Candidate 如何成为 Formal Business Fact；
- Runtime progress 与 Domain commit 怎样区分；
- External Effect Outcome Unknown 怎样进入 Reconcile；
- Security Authority 何时重新判断；
- Recovery 从哪一类 durable fact 开始；
- 复杂机制在什么测量条件下应该删除。

Architecture 不拥有 Current implementation truth。代码、Migration、Test、Trace、Eval、性能和 Production Readiness 只能由 `docs/evidence/` 证明。
