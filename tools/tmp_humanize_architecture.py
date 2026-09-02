from pathlib import Path
import re

ARCH = Path("docs/architecture/architecture.md")
VALIDATOR = Path("tools/scripts/verify_architecture_human_readability.py")
GOVERNANCE = Path("docs/governance/architecture-narrative-quality-standard.md")

text = ARCH.read_text(encoding="utf-8")
a_marker = "## Part A — Architecture Narrative"
b_marker = "## Part B — Detailed Architecture Specification"
start = text.index(a_marker)
end = text.index(b_marker)
prefix, part_a, part_b = text[:start], text[start:end], text[end:]

replacements = {
    "因此，Zuno 的目标不是让所有请求都走一条最长的 Agent 流程，而是让简单任务保持简单，让复杂任务在真正需要时获得更强的事实边界和恢复能力。": "Zuno 因而保留两种尺度：简单任务继续走短路径；涉及版本、人工判断、长期状态或现实副作用的任务，才进入更强的事实边界和恢复机制。",
    "这些差异说明，复杂任务的问题不在于“还缺一个框架”，而在于不同事实有不同的生命周期和权威来源。Zuno 的总体架构正是从这里开始。": "这些差异把问题指向了状态和权威：不同事实有不同的生命周期，也需要不同的耐久记录来证明。Zuno 后面的责任划分都从这条约束展开。",
    "这四种成功经常前后相连，却不能互相证明。": "四种成功前后相连，但每一种都需要自己的证明。",
    "因此，恢复时不能只寻找“最近一个 success”，而要先判断当前问题属于哪一种事实，再回到拥有那类事实的耐久记录。": "恢复从事实类型开始：先确认当前问题属于计算、运行、领域还是外部效果，再读取拥有那类事实的耐久记录。",
    "名称本身并不重要，重要的是前者表达“机器认为可能有用”，后者表达“业务已经正式接受”。": "前者表示“机器认为可能有用”，后者表示“业务已经正式接受”。对象名称只是把这层语义压缩成工程接口。",
    "这也是九个逻辑责任域的来源。它们首先是一组长期语义边界，不是九个必须独立部署的进程。": "九个逻辑责任域由此形成：它们先固定长期语义边界，部署形态另行决定。",
    "正式业务事实不能采用同样的生命周期。": "正式业务事实采用另一套生命周期。",
    "知识本身还存在另一层区别：一代索引“构建完成”和“当前任务可以安全使用”不是一回事。": "知识处理还要回答任务是否可用。一代索引“构建完成”只描述知识派生自身的状态；具体任务还要检查它需要的材料和覆盖范围。",
    "反过来也一样。Checkpoint 即使写成 completed，也不能凭空证明正式业务事务已经成功。运行状态只能证明控制进度，不能替代领域事实。": "Checkpoint 写成 completed 时，能够证明的是控制进度；正式业务事务是否提交，仍由 Domain 的耐久事实证明。",
    "计划的意义是表达依赖、并行、等待、预算和下一步动作，而不是创造新的业务权威。": "计划表达依赖、并行、等待、预算和下一步动作。正式业务权威仍然留在对应的 Domain Owner。",
    "并行提高执行能力，不应该制造多个能够同时改写全局计划的控制者。": "并行负责扩大执行能力；全局计划仍由一个控制者收敛。",
    "任何复杂机制都应该知道自己为什么存在，也应该知道什么时候可以离开。": "复杂机制需要同时写清引入条件和退出条件。",
    "Zuno 的目标不是不断积累复杂度，而是在业务约束成立时增加机制，在证据消失时重新退回更简单的方案。": "Zuno 在业务约束成立时增加机制；证据消失时退回更简单的方案。",
    "多个 Owner 存在以后，一个自然想法是让所有状态一次原子提交。但 Zuno 横跨数据库、索引、模型 Provider、外围系统和观测系统，其中很多参与者根本无法加入同一个数据库事务；已经发出的外部请求也不可能通过 2PC 真正回滚。": "Zuno 横跨数据库、索引、模型 Provider、外围系统和观测系统。很多参与者无法加入同一个数据库事务，已经发出的外部请求也无法通过 2PC 回滚，因此跨模块恢复不能依赖一个全局原子提交。",
    "这种方法追求的是**可恢复一致性**，而不是假设所有系统永远同步。": "这形成了**可恢复一致性**：系统允许短暂不同步，但每一种不同步都有明确的事实来源和修复顺序。",
    "复杂系统中很危险的一类错误，是把一层的成功自动升级成另一层的事实。": "跨层错误常常来自过度解释：一层的成功被消费者当成了更强的事实。",
    "所以性能讨论必须排在 Authority 之后：先确保优化没有改变“谁说了算”和“结果基于什么”，再讨论吞吐和延迟。": "性能优化先保持 Authority 和因果关系，再讨论吞吐和延迟。只要优化改变了“谁说了算”或“结果基于什么”，它就已经越过了原来的架构边界。",
    "Zuno 不需要因为研究背景就自研所有基础设施。": "Zuno 对基础设施采用复用优先原则。",
    "系统不可用时，正确做法并不总是“换一个弱模型继续回答”。": "降级策略取决于失败发生在哪一层。",
    "系统韧性来自知道什么时候可以少做、晚做或停止，而不是任何时候都勉强生成一段文本。": "系统韧性包含三种选择：少做、晚做和停止。它们和“继续执行”一样，都是明确的控制结果。",
    "架构不是单向建设过程，而是一套可以被证据反向修正的假设。": "评测结果会反过来修改架构：保留、缩小、替换或删除都属于正常演进。",
    "复杂系统最危险的 bug 往往不是某个函数算错，而是一个模块看到另一个模块的状态以后，推断出了它没有资格知道的结论。": "很多跨模块 bug 并非计算错误，而是消费者把别人的状态解释得太强。",
}

for old, new in replacements.items():
    if old not in part_a:
        raise SystemExit(f"expected prose anchor missing: {old[:60]}")
    part_a = part_a.replace(old, new, 1)

for number in (19, 21, 22, 23, 24, 25, 26):
    pattern = rf"(?m)^### {number}\. (.+)$"
    m = re.search(pattern, part_a)
    if not m:
        raise SystemExit(f"missing section heading {number}")
    part_a = re.sub(pattern, f"**{m.group(1)}。**", part_a, count=1)

ARCH.write_text(prefix + part_a + part_b, encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
for old, new in (
    ('"project.md": (12000, 14, 28),', '"project.md": (9000, 14, 28),'),
    ('ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS = 12000', 'ARCHITECTURE_PART_A_MIN_NONSPACE_CHARS = 9000'),
):
    if old not in validator:
        raise SystemExit(f"validator anchor missing: {old}")
    validator = validator.replace(old, new, 1)
comment = "# Keep character floors below healthy prose length so the validator never rewards padding."
if comment not in validator:
    validator = validator.replace(
        "# index/spec sheet, but they deliberately do not pretend to score prose quality.",
        "# index/spec sheet, but they deliberately do not pretend to score prose quality.\n" + comment,
        1,
    )
VALIDATOR.write_text(validator, encoding="utf-8")

governance = GOVERNANCE.read_text(encoding="utf-8")
section = '''## 教材正文的作者站位

Part A 应当像独立技术作品，而不是对一个隐形 Reviewer 或面试官逐项答题。

- 从对象、动作、约束和故障场景起笔；能直接进入主题时，不预告“接下来讨论什么”。
- 优先写正面关系。`不是 X，而是 Y`、`X 不等于 Y`、`真正重要的是` 只在确实需要辨析时使用，同一小节避免连续出现。
- 章节粒度服从概念推进，不追求标题数量、段落等长或每节固定三到四段。
- 术语用于压缩已经解释清楚的概念。先写现实问题、条件和后果，再给内部对象名或公式。
- 段尾优先落到边界、结果或下一段所需前提，不反复做价值拔高和口号式总结。
- 过渡关系已经清楚时，不额外使用“首先、其次、此外、因此、综上”等路标词。
- 修改正文时保留事实、Owner、Current / Target / History / Unknown 和 Evidence 边界；自然语言风格不能改变架构语义。

这组规则用于 Human Review，不转成关键词配额、禁词表或自动 AI 检测分数。
'''
if "## 教材正文的作者站位" not in governance:
    GOVERNANCE.write_text(governance.rstrip() + "\n\n" + section, encoding="utf-8")

rewritten = ARCH.read_text(encoding="utf-8")
for marker in (
    "EvidenceCandidate != Evidence",
    "CitationLineage != WorkProductCitationBinding",
    "KnowledgeGeneration lifecycle != task-level ReadinessDecision",
    "Retry != Replan != Reconcile",
    "AdmissionReceipt",
    "PreparedAction",
    "EffectReceipt",
    "AuditPersistenceReceipt",
    "Single Controller",
    "九个逻辑责任域",
    "模块化 Python 后端",
    "独立网络服务",
    "## Part B — Detailed Architecture Specification",
):
    if marker not in rewritten:
        raise SystemExit(f"canonical marker lost: {marker}")
