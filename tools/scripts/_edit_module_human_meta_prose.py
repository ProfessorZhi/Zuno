from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(
            f"{relative}: expected exactly one occurrence for replacement; got {text.count(old)}\n{old}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def edit_application() -> None:
    path = "docs/modules/application/README.md"
    replace_once(
        path,
        "所以 01 的价值不是成为万能业务层，而是把其他 Owner 已经成立的事实组合成对外一致的产品行为。",
        "01 把其他 Owner 已经成立的事实组合成对外一致的产品行为；授权、知识、Runtime、Domain 和 Effect 仍由各自 Owner 保持最终权威。",
    )
    replace_once(
        path,
        "**可以用一条法院 Host 集成链贯穿这一篇。** 外部系统提交一次复杂分析，先拿到受理结果；任务运行很久后形成正式 WorkProduct；随后新证据让它失效，而目标系统此时可能离线；如果最终还要把结果写回外围系统，网络 timeout 又会带来现实结果未知。01 的所有设计都应该帮助外部产品正确理解这些变化，而不是把内部九个 Owner 压成一个 `status`。",
        "一条法院 Host 集成链会连续暴露这些边界：外部系统先提交复杂分析并拿到受理结果，长任务随后形成正式 WorkProduct；新证据可能让已经发布的结果失效，而目标系统此时又可能离线；最终写回外围系统时，网络 timeout 还会让现实结果变成 Unknown。01 需要把这些变化翻译成稳定的产品行为，同时保留各个 Owner 对事实的最终权威。",
    )
    replace_once(
        path,
        "工程上可以把这个产品层决定表达为 InvocationDecision，但关键概念不是名字，而是：01 只决定“这次请求应走哪条产品路径”，不能替 03 重新判断知识资格，也不能替 08 判断授权，更不能替 02 正式准入。",
        "工程上可以把这个产品层决定表达为 InvocationDecision。它只表示“这次请求应走哪条产品路径”；知识资格仍由 03 判断，授权由 08 判断，正式准入由 02 决定。",
    )
    replace_once(
        path,
        "---\n\n**前半篇解决了“请求怎样进入、结果什么时候可以发布”；接下来进入产品生命周期。** 一旦正式结果已经离开当前请求，新的问题不再是返回什么 JSON，而是结果变旧以后怎样让外部世界尽快知道，同时又不把网络送达状态冒充成业务有效性。",
        "正式结果离开当前请求以后，产品边界进入长期生命周期。问题从“这次请求返回什么”扩展为“结果变旧以后怎样让外部世界尽快知道”，而网络送达状态仍然不能冒充业务有效性。",
    )
    replace_once(
        path,
        "---\n\n**当 Delivery 开始改变外围系统时，01 的边界到这里必须主动停下来。** 产品层知道“应该交付什么”，但现实世界“到底发生了什么”已经属于 Effect 问题；继续在 Application 里写 retry loop，只会让产品语义和副作用恢复重新混在一起。",
        "Delivery 一旦开始改变外围系统，产品层继续拥有“应该交付什么”的语义，现实世界“到底发生了什么”则由 06 的 Effect truth 证明。把 retry loop 留在 Application 会重新混合产品语义和副作用恢复。",
    )
    replace_once(
        path,
        "---\n\n**到这里先做一次删除测试。** 如果没有多 Host、异步交付、失效传播和复杂任务受理，前面很多产品生命周期语义都应该缩回去；Application 的成熟不是功能最多，而是只保留外部消费者真正需要的稳定语义。",
        "如果系统没有多 Host、异步交付、失效传播和复杂任务受理，这些产品生命周期机制应当缩回普通请求/响应边界。Application 只保留外部消费者真正需要的稳定语义。",
    )
    replace_once(
        path,
        "所以发布不是“生成完成后的固定副作用”，而是一个需要消费当前事实的边界。",
        "发布需要在边界上重新消费当前事实。",
    )
    replace_once(
        path,
        "01 更适合组合成用户可行动的产品状态：等待材料、等待审批、正在处理、结果可查看、结果需复核、交付待确认等，同时保留诊断引用供受控排障。产品状态不是隐藏真实错误，而是把多个 Owner facts 翻译成稳定的消费者语义。",
        "01 将多个 Owner facts 翻译成用户可行动的产品状态：等待材料、等待审批、正在处理、结果可查看、结果需复核、交付待确认等，同时保留诊断引用供受控排障。",
    )
    replace_once(
        path,
        "这也是为什么应用层的可靠性重点是可重复查询和可恢复传播，而不是制造一个跨所有消费者的全局提交事务。",
        "应用层可靠性因此集中在可重复查询和可恢复传播；跨所有消费者建立全局提交事务没有必要。",
    )


def edit_capability() -> None:
    path = "docs/modules/capability/README.md"
    replace_once(
        path,
        "**贯穿这一篇的例子可以只看“事件抽取”这一项能力。** 早期它可能由课题组研究模型实现，后来也可能出现规则版本、LLM Provider 或外部服务。如果 Runtime 直接依赖 `PaperAExtractor()`，每次换实现都会把 Workflow、失败语义和质量假设一起带着改；真正需要稳定下来的，是“事件抽取这项专业能力到底承诺什么”，而不是某个算法名字。下面的 Capability / Provider / Conformance / Qualification 都围绕这个问题展开。",
        "事件抽取足以说明这条边界。早期实现可能来自课题组研究模型，后来也可能出现规则版本、LLM Provider 或外部服务。如果 Runtime 直接依赖 `PaperAExtractor()`，每次替换实现都会同时改变 Workflow、失败语义和质量假设。稳定边界应落在“事件抽取这项专业能力承诺什么”，Provider 只负责实现这份承诺。",
    )
    replace_once(
        path,
        "Capability 的核心不是类名，而是一份专业承诺：输入是什么业务含义，输出表达什么，哪些情况算成功、拒绝、不可判定或需要 Review，以及结果可以被哪些后续流程消费。",
        "Capability 是一份专业承诺：输入的业务含义、输出语义、成功、拒绝、不可判定或需要 Review 的条件，以及哪些后续流程可以消费结果。",
    )
    replace_once(
        path,
        "复杂开放判断可能值得更强推理模型，稳定抽取可能更适合小模型或规则。选择依据应该是 Eval 和业务约束，而不是“最新模型能力更强”的抽象印象。",
        "复杂开放判断可能值得更强推理模型，稳定抽取可能更适合小模型或规则。选择依据来自 Eval 和业务约束；“最新模型能力更强”本身不足以成为默认路由理由。",
    )


def edit_model_gateway() -> None:
    path = "docs/modules/model-gateway/README.md"
    replace_once(
        path,
        "**贯穿这一篇的不是“怎么做一个通用 Model Gateway”，而是一条法律任务中的模型选择链。** Planner 可能需要强推理，Query Rewrite 更重视速度，结构化抽取可能适合小模型；同一份案件材料又可能只允许发给特定地域或特定 Provider。07 的价值，就是让这些调用在不泄漏业务 Authority 的前提下，仍然能解释为什么选这个模型、花了多少、失败后能否切换，以及切换以后还是否合格。",
        "一条法律任务中的模型选择链足以暴露 07 的边界。Planner 可能需要强推理，Query Rewrite 更重视速度，结构化抽取可能适合小模型；同一份案件材料还可能只允许发给特定地域或 Provider。07 让每次调用都能解释所选 Model Role、当前资格、预算和失败后的切换，同时不接管上层业务 Authority。",
    )
    replace_once(
        path,
        "---\n\n**前面先把 Role、Provider 和上层业务语义拆开；现在才进入真正的路由问题。** 路由不是“选当前最强模型”，而是在当前允许集合里做一个可解释的质量 / 安全 / 预算 / deadline 决定。",
        "Role、Provider 与上层业务语义分开以后，Routing 才能在当前允许集合中权衡质量、安全、预算和 deadline。它选择满足约束的模型，不以“当前最强”作为单一目标。",
    )
    replace_once(
        path,
        "---\n\n**到这里先收束一次边界本身。** 逻辑上统一模型调用，不等于物理上必须多一次网络跳；如果没有 Secret isolation、独立吞吐、网络出口或部署生命周期证据，07 应继续是薄的模块边界，而不是为了“AI Infra 完整”自造平台。",
        "统一模型调用是一条逻辑责任边界，不要求额外网络跳。没有 Secret isolation、独立吞吐、网络出口或不同部署生命周期的证据时，07 继续作为薄模块存在；物理拆服务只在这些约束真实出现以后发生。",
    )


def edit_security() -> None:
    path = "docs/modules/security/README.md"
    replace_once(
        path,
        "**可以用一个持续三十分钟的法律任务贯穿全文。** 用户在开始时有权读取一组材料，任务随后等待知识构建、调用模型、进入人工审批并准备执行外部动作；这期间权限、Matter 归属、数据外发政策、Approval 和 Credential 都可能变化。08 要保护的不是“入口鉴权成功”，而是每一次新的受保护动作在真正发生前都能回答：现在还允许吗？",
        "一个持续三十分钟的法律任务会让时间维度直接暴露出来。用户开始时有权读取一组材料，任务随后等待知识构建、调用模型、进入人工审批并准备外部动作；期间权限、Matter 归属、数据外发政策、Approval 和 Credential 都可能变化。08 在每个新的受保护动作发生前重新回答：现在还允许吗？",
    )
    replace_once(
        path,
        "---\n\n**因此安全的第一层不是增加更多角色，而是承认时间会改变权限前提。** 长任务中的 allow 必须有作用域和新鲜度，历史上合法做过的事与未来还能不能继续做必须分开。",
        "长任务的安全边界由时间推动：allow 必须带作用域和新鲜度，历史上合法执行过的动作不会自动授权未来动作。增加更多 RBAC 角色无法解决这个时间问题。",
    )
    replace_once(
        path,
        "---\n\n**到这里先回到 Build / Buy。** 身份目录、Secret Manager、Policy Engine 等基础设施能复用就复用；08 值得自己拥有的只是 Zuno 必须长期解释的安全 Authority、新鲜度、审批和数据用途语义。",
        "身份目录、Secret Manager、Policy Engine 等基础设施优先复用。08 自己拥有 Zuno 必须长期解释的安全 Authority、新鲜度、Approval 和数据用途语义；成熟基础设施继续提供身份、Secret 存储和策略执行原语。",
    )


def edit_evaluation() -> None:
    path = "docs/modules/evaluation/README.md"
    replace_once(
        path,
        "**贯穿这一篇只问一个决策问题：GraphRAG、Reflection、强模型、Specialist 或 Native Runtime 到底值不值得留下。** 要回答它，团队既要知道一次真实请求发生了什么，也要能把同一 task class 放进可复现实验，与更简单 baseline 比质量、恢复、时延和成本。Observability 提供因果线索，Evaluation 提供决策证据；两者都不能越权成为业务 Truth。",
        "GraphRAG、Reflection、强模型、Specialist 或 Native Runtime 是否值得保留，是 09 必须持续回答的设计问题。团队既要知道一次真实请求发生了什么，也要把同一 task class 放进可复现实验，与更简单 baseline 比质量、恢复、时延和成本。Observability 提供因果线索，Evaluation 提供决策证据；两者都不拥有业务 Truth。",
    )
    replace_once(
        path,
        "---\n\n**先把“发生了什么”讲清以后，才有资格比较“哪种设计更好”。** 评测不是在 Dashboard 上挑一个数字，而是先冻结 Dataset、版本、暴露关系和 Judge，再让结果真正可比较。",
        "可比较的 Eval 建立在可解释运行事实之上。Dataset、版本、训练暴露关系和 Judge 先被冻结，再比较不同设计；Dashboard 上的单一数字不足以支持架构选择。",
    )


def main() -> None:
    edit_application()
    edit_capability()
    edit_model_gateway()
    edit_security()
    edit_evaluation()


if __name__ == "__main__":
    main()
