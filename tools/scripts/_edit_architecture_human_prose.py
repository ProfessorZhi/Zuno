from __future__ import annotations

from pathlib import Path


PATH = Path("docs/architecture/README.md")

REPLACEMENTS = {
    "法律智能系统最危险的时刻，往往不是模型明确报错，而是一次执行看起来成功了，却留下了几种含义完全不同的“成功”。":
        "法律智能系统更危险的故障，常发生在一次执行表面成功、却留下几种含义完全不同的“成功”时。显式模型报错反而更容易识别和处理。",
    "Zuno 的 Target Architecture 从一个很朴素的规则出发：**不同种类的事实，由不同的责任域证明；一个事实跨越边界以后，必须留下足以支持恢复和审计的因果记录。** Agent、RAG、GraphRAG、模型网关和工作流框架都服务于这条规则，而不是反过来决定系统边界。":
        "Zuno 的 Target Architecture 从一个很朴素的规则出发：**不同种类的事实，由不同的责任域证明；一个事实跨越边界以后，必须留下足以支持恢复和审计的因果记录。** 系统边界先由这条规则确定，Agent、RAG、GraphRAG、模型网关和工作流框架再作为实现手段进入设计。",
    "从这里开始，系统必须持续回答一组比“模型输出是什么”更难的问题：当时依据的是哪一版材料；知识是否覆盖了当前任务需要的范围；哪些内容只是机器候选；哪些结果已经成为正式业务事实；谁做过专业判断；旧结果为什么失效；崩溃以后应该相信哪一份记录；外部动作究竟有没有真实发生。":
        "结果进入长期生命周期以后，系统必须持续回答一组比“模型输出是什么”更难的问题：当时依据的是哪一版材料；知识是否覆盖了当前任务需要的范围；哪些内容只是机器候选；哪些结果已经成为正式业务事实；谁做过专业判断；旧结果为什么失效；崩溃以后应该相信哪一份记录；外部动作究竟有没有真实发生。",
    "这张表决定了后面大量看似细碎的设计选择。":
        "这些事实边界直接约束后续的完成证明、恢复顺序、版本新鲜度和权限判断。",
    "同样，一次模型调用成功、一个 Runtime Step 完成、一个 Domain 事务提交、一个外部 Effect 被确认，都是“成功”，但它们分别证明不同事情。恢复时最重要的不是寻找一个全局 `success=true`，而是先确定当前问题属于哪一种事实。":
        "一次模型调用成功、一个 Runtime Step 完成、一个 Domain 事务提交、一个外部 Effect 被确认，分别证明不同事情。恢复时先确定当前问题属于哪一种事实，再读取对应 Owner 的完成证明；全局 `success=true` 无法承担这个角色。",
    "Zuno 的主要工程边界都出现在“某种信息准备获得更强语义”的时刻。正常流程里这些边界几乎没有存在感；真正的价值体现在材料不完整、进程崩溃、权限变化和网络结果未知时。":
        "Zuno 的主要工程边界都出现在“某种信息准备获得更强语义”的时刻。正常流程中这些边界只增加必要约束；材料不完整、进程崩溃、权限变化或网络结果未知时，它们决定系统依据什么事实继续收敛。",
    "**机器候选进入正式业务状态。** 检索、模型和专业 Capability 可以产生 EvidenceCandidate 或 Proposal。需要长期保存的法律结果进入 Legal Domain 后，Domain 根据材料版本、专业规则、必要的人审与当前安全条件决定是否接纳。接纳事务同时形成新的 DomainVersion 和 `AdmissionReceipt`。Receipt 不是为了多造一个对象，它记录的是“这个正式结果为什么成立”的因果凭据，后面的恢复依赖这份事实。":
        "**机器候选进入正式业务状态。** 检索、模型和专业 Capability 可以产生 EvidenceCandidate 或 Proposal。需要长期保存的法律结果进入 Legal Domain 后，Domain 根据材料版本、专业规则、必要的人审与当前安全条件决定是否接纳。接纳事务同时形成新的 DomainVersion 和 `AdmissionReceipt`。Receipt 记录“这个正式结果为什么成立”的耐久因果凭据，后续恢复以这份事实确认正式提交是否已经发生。",
    "Security 在每一次受保护的跨越前重新判断当前权限、数据政策、Approval 和 Secret 条件。这样控制成本集中在真正改变业务事实或现实状态的地方，而不是让每一次低风险计算都经过同样沉重的审批。":
        "Security 在每一次受保护的跨越前重新判断当前权限、数据政策、Approval 和 Secret 条件。检查点集中在真正改变业务事实、暴露受保护数据或影响现实状态的边界，低风险纯计算继续保持较轻路径。",
    "九个责任域不是先画出来再寻找理由。前面的事实和边界稳定以后，系统自然需要这些长期 Owner。":
        "前面的事实类型和跨边界动作稳定以后，九个长期 Owner 随之确定。每个责任域存在，是因为有一类事实需要唯一的最终解释权和恢复依据。",
    "Platform / Infrastructure 位于这些责任域之下，提供 PostgreSQL、Object Store、Queue、Checkpointer、CAS、Lease、Fencing、Clock、Backup/Restore、Network 和 Secret Delivery 等技术原语。它们可以非常成熟，也可以完全复用现有平台，但不会因为数据库事务成功就自动拥有更上层的业务语义。":
        "Platform / Infrastructure 位于这些责任域之下，提供 PostgreSQL、Object Store、Queue、Checkpointer、CAS、Lease、Fencing、Clock、Backup/Restore、Network 和 Secret Delivery 等技术原语。这些能力优先复用成熟平台；数据库事务成功只证明对应技术提交完成，上层业务事实仍由各自 Owner 解释。",
    "这九个责任域首先是逻辑 Ownership。它们可以落在同一个 Python 进程里，也可以按工作负载拆成 Worker；是否成为独立网络服务属于部署问题，而不是架构图上的模块数量问题。":
        "这九个责任域首先是逻辑 Ownership。它们可以落在同一个 Python 进程里，也可以按工作负载拆成 Worker；是否成为独立网络服务由扩缩容、安全隔离、故障半径和部署生命周期等约束决定，与逻辑模块数量分开。",
    "长任务恢复最容易犯的错误，是把“离崩溃最近的状态”当成最可信的状态。Zuno 采用相反顺序：先找到当前问题对应的 Owner Fact，再修复 Runtime、Cache、Projection 或通知状态。":
        "长任务恢复从当前问题对应的 Owner Fact 开始。离崩溃最近的状态可能只是较弱的 Runtime、Cache、Projection 或通知记录；确认权威事实以后，再修复这些派生状态。",
    "如果恢复逻辑只看 Checkpoint，它会再次提交同一份正式结果。正确顺序是按稳定 causation 查询 Domain：匹配的 AdmissionReceipt 已经存在，说明正式业务提交已经成立。Runtime 随后把自己的控制状态修到与 Domain 一致，而不是让较弱的控制投影推翻较强的领域事实。":
        "如果恢复逻辑只看 Checkpoint，它会再次提交同一份正式结果。系统应按稳定 causation 查询 Domain：匹配的 AdmissionReceipt 已经存在，说明正式业务提交已经成立。Runtime 随后把自己的控制状态修到与 Domain 一致，使较弱的控制投影重新跟随较强的领域事实。",
    "取消也遵循事实边界。Cancellation 停止未来工作，不会神奇地回滚已经正式提交的 Domain fact 或已经发生的现实 Effect。晚到结果是否仍可接纳，由对应 Owner 根据版本、因果和当前状态判断。":
        "取消也遵循事实边界。Cancellation 只停止未来工作；已经正式提交的 Domain fact 和已经发生的现实 Effect 保持历史事实。晚到结果是否仍可接纳，由对应 Owner 根据版本、因果和当前状态判断。",
    "Zuno 的另一个长期问题来自项目本身的研究背景。论文、实验模型和规则系统不断变化，业务系统却需要稳定依赖。把一个研究模型包一层 Python wrapper 只能证明 Demo 能跑，不能证明它已经成为长期工程能力。":
        "Zuno 的研究背景带来另一类长期变化：论文、实验模型和规则系统不断演进，业务系统却需要稳定依赖。Python wrapper 加一次 Demo 只能证明链路能够运行；长期工程能力还需要稳定语义、版本、资格和评测。",
    "架构因此必须允许自己缩小。某项复杂机制长期无法在 Evaluation 中证明收益时，关闭它、回到 baseline 或恢复共进程部署都属于正常演进，而不是架构失败。":
        "架构必须允许自己缩小。某项复杂机制长期无法在 Evaluation 中证明收益时，就关闭它、回到 baseline 或恢复共进程部署；这属于正常工程收敛。",
    "设计与实施之间保持这个方向：先说明系统应该保护什么，再选择最简单的实现；实现结果通过 Evidence 验证、缩小或修正 Target Architecture。已有代码目录、框架 Feature 或单次 Demo 都不能反过来成为新的事实 Authority。":
        "设计先说明系统必须保护什么，再选择最简单的实现；实现结果通过 Evidence 验证、缩小或修正 Target Architecture。代码目录、框架 Feature 和单次 Demo 提供实现或试验信息，不拥有新的事实 Authority。",
}


def main() -> None:
    text = PATH.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"expected exactly one match, got {count}: {old[:90]}")
        text = text.replace(old, new)
    PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
