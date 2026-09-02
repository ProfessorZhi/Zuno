from pathlib import Path

ARCH = Path("docs/architecture/architecture.md")
text = ARCH.read_text(encoding="utf-8")na = text.index("## Part A — Architecture Narrative")
b = text.index("## Part B — Detailed Architecture Specification")
prefix, part_a, part_b = text[:a], text[a:b], text[b:]

heading_changes = {
    "### 2. 最简单的系统，以及它开始失效的地方": "### 2. 从简单系统到事实边界",
    "### 3. 四种不能混在一起的“成功”": "**四种成功。**",
    "### 4. 机器结果首先是候选": "**候选与正式事实。**",
    "### 5. 按事实权威划分责任": "### 3. 事实权威与责任边界",
    "### 6. 材料、知识派生与正式业务事实": "### 4. 材料、知识与正式业务事实",
    "### 7. 领域状态与运行状态": "### 5. 领域状态与运行状态",
    "### 8. 长任务的计划与控制": "### 6. 长任务的计划、控制与恢复",
    "### 9. 三种不同的恢复动作": "**Retry、Replan 与 Reconcile。**",
    "### 10. 长任务中的持续授权": "### 7. 持续授权与现实副作用",
    "### 11. 外部副作用与现实结果": "**外部副作用的确认。**",
    "### 12. 九个逻辑责任域": "### 8. 九个逻辑责任域",
    "### 13. 三类任务路径": "**三类任务路径。**",
    "### 14. 一个关键崩溃窗口的恢复": "### 9. 故障恢复与业务演进",
    "### 15. 新证据与历史成果": "**新证据到来以后。**",
    "### 16. 研究能力与可替换实现": "### 10. 研究能力、部署与复杂度",
    "### 17. 逻辑边界与物理部署": "**逻辑边界与物理部署。**",
    "### 18. 复杂度的退出机制": "**复杂度的退出机制。**",
    "### 20. 跨模块的一致性与恢复": "### 11. 跨模块一致性与系统约束",
    "### 27. 稳定的是语义，不是今天的实现": "### 12. 稳定语义与架构演进",
    "### 28. 架构演进必须包含迁移": "**迁移是架构演进的一部分。**",
    "### 29. 过载与局部故障": "**过载与局部故障。**",
    "### 30. Current、Target、Evidence 与 Unknown": "### 13. Current、Target、Evidence 与 Unknown",
    "### 31. 总体架构留下的几条原则": "**架构的长期骨架。**",
}
for old, new in heading_changes.items():
    if old not in part_a:
        raise SystemExit(f"missing heading: {old}")
    part_a = part_a.replace(old, new, 1)

prose_changes = {
    "在一条完整任务链中，至少存在四种不同的成功。": "同一个案件在不同层面会出现四种“成功”。",
    "所以：\n\n`Retry != Replan != Reconcile`\n\n这个区分决定了系统下一步是否可以自动行动，也构成了故障恢复的基本语言。": "三者关系可以记成：`Retry != Replan != Reconcile`。这个区分决定系统下一步能否自动行动，也构成了故障恢复的基本语言。",
    "因此，“任务开始时允许”不能变成后续所有动作的永久通行证。每当系统再次跨越一个受保护边界，例如读取新的敏感材料、把数据发送给模型、获取 Secret、执行高风险 Tool 或提交正式业务结果，都需要消费当前有效的安全决定。": "“任务开始时允许”只对当时的访问有效。系统再次读取敏感材料、向模型发送数据、获取 Secret、执行高风险 Tool 或提交正式业务结果时，都重新消费当前有效的安全决定。",
    "Zuno 因此在发送以前先形成稳定的动作身份和内容，工程上称为 `PreparedAction`。": "发送以前，Zuno 先固定动作身份和内容，工程上称为 `PreparedAction`。",
    "到这里，九个责任域已经可以从问题本身自然得到。": "前面的状态、控制和恢复问题最终落在九个逻辑责任域中。",
    "同一套边界并不意味着所有任务拥有同样复杂度。": "同一套边界支持不同复杂度的任务路径。",
    "这个例子体现了一条贯穿 Zuno 的原则：**先恢复拥有业务权威的事实，再修复缓存、检查点和其他派生状态。**": "恢复顺序由事实权威决定：**先恢复拥有业务权威的事实，再修复缓存、检查点和其他派生状态。**",
    "Zuno 不通过删除旧版本来制造“始终一致”的假象。旧版本仍然记录当时基于哪些材料和判断产生；新的材料变化形成新的领域事实，并沿依赖关系决定哪些 Finding 或 WorkProduct 进入 stale / review-required。": "Zuno 保留旧版本以及它当时依赖的材料和判断。新材料形成新的领域事实，再沿依赖关系决定哪些 Finding 或 WorkProduct 进入 stale / review-required。",
    "Zuno 来自智慧司法研究背景，因此会使用事件抽取、冲突识别、类案检索、GraphRAG、Memory、Reflection 等能力。研究积累很重要，但论文或框架本身不应该成为运行时长期依赖的接口。": "Zuno 会吸收事件抽取、冲突识别、类案检索、GraphRAG、Memory、Reflection 等研究能力。运行时长期稳定的是专业能力的输入、输出和资格条件；论文模型、规则系统、LLM 或外部服务只是这些能力在某一阶段的实现。",
    "一个专业能力可能先由论文模型实现，后来换成规则系统、LLM 或外部服务。对上层来说，真正应该稳定的是“事件抽取需要什么输入、返回什么结果、在什么条件下合格”，而不是某个具体类名。": "例如事件抽取可以先由论文模型实现，后来换成规则系统或 LLM。上层始终依赖“事件抽取需要什么输入、返回什么结果、在什么条件下合格”，而不是具体类名。",
    "九个逻辑责任域首先回答“谁负责哪类事实”，并不要求九个独立服务。默认物理形态完全可以是模块化 Python 后端，加上根据工作负载需要拆出的 Worker。": "九个逻辑责任域定义语义归属，物理部署可以从模块化 Python 后端起步，再按工作负载拆出必要的 Worker。",
    "如果简单 RAG 已经满足目标任务，就不需要 Native Runtime；如果 Hybrid Retrieval 已经覆盖某类 query，就没有必要默认启用 GraphRAG；如果通用 Host + Zuno Legal Backend 已经能够保护正式状态和恢复，就不需要复制完整宿主；如果一个逻辑模块没有独立扩缩容或安全隔离需求，也没有必要拆成微服务。": "简单 RAG 能满足目标任务时，系统停留在简单 RAG；Hybrid Retrieval 已经覆盖某类 query 时，GraphRAG 保持关闭；通用 Host + Zuno Legal Backend 已经能够保护正式状态和恢复时，继续复用 Host；逻辑模块只有出现独立扩缩容或安全隔离需求以后，才进入服务拆分。",
    "读完整体架构以后，最值得保留的不是九个模块名称，而是几条可以反复用于判断设计的原则。": "Zuno 的长期骨架由几条比模块名称更稳定的语义约束组成。",
    "这些原则构成 Zuno 的长期骨架。具体对象名、字段、Provider、数据库和部署方式都可以继续演进，只要它们没有破坏这些已经接受的事实权威和因果关系。": "具体对象名、字段、Provider、数据库和部署方式可以继续演进；事实权威、完成证明和因果关系保持稳定。",
}
for old, new in prose_changes.items():
    if old not in part_a:
        raise SystemExit(f"missing prose anchor: {old[:70]}")
    part_a = part_a.replace(old, new, 1)

# Ensure textbook-scale chapter structure: 13 numbered Part A chapters, no orphan old numbers.
for old_number in (14, 15, 16, 17, 18, 20, 27, 28, 29, 30, 31):
    if f"### {old_number}." in part_a:
        raise SystemExit(f"orphan old heading remains: {old_number}")
numbered = [line for line in part_a.splitlines() if line.startswith("### ")]
if len(numbered) != 13:
    raise SystemExit(f"expected 13 numbered chapters, found {len(numbered)}")

ARCH.write_text(prefix + part_a + part_b, encoding="utf-8")
