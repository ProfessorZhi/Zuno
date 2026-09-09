from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

PROJECT_HEADINGS = [
    "## 1. Zuno 是什么",
    "## 2. 项目缘起：为什么会有这个项目",
    "## 3. 从问答系统到法律工作系统",
    "## 4. 通用平台的边界：为什么不直接用 Dify、Coze",
    "## 5. Zuno 必须自己承担的工程责任",
    "### 5.1 材料版本与知识就绪",
    "### 5.2 机器候选与正式业务事实",
    "### 5.3 长期引用与结果失效",
    "### 5.4 现实副作用与对账恢复",
    "### 5.5 从研究成果到稳定专业能力",
    "### 5.6 专业质量不能用 HTTP 200 代替",
    "## 6. 一个复杂法律任务怎样流过系统",
    "## 7. 三种产品形态与工程取舍",
    "## 8. 什么时候完整 Zuno 反而不值得使用",
    "## 9. 项目演进：项目是怎样发展到今天的",
    "### 9.1 加入项目时，系统已经存在",
    "### 9.2 Internal Demo 证明链路进入内部验证",
    "### 9.3 客户侧 Demo 暴露了回答质量问题",
    "### 9.4 法院侧测试进入了更真实的使用环境",
    "### 9.5 Pilot Validation 是试点，不是生产资格",
    "## 10. 团队与个人参与：团队是什么形态，我在里面做了什么",
    "## 11. 四条事实线：History、Current、Target 与 Unknown",
    "## 12. 已知与未知：相比通用方案，我们今天到底证明了什么",
    "## 13. 仍需恢复的工程证据",
    "## 14. 从项目叙事进入总体架构",
]

PROJECT_MAP = {
    PROJECT_HEADINGS[0]: "## 从智慧司法背景到长期法律工作",
    PROJECT_HEADINGS[1]: None,
    PROJECT_HEADINGS[2]: "**简单问答与长期法律工作在这里分叉。**",
    PROJECT_HEADINGS[3]: "## 通用平台之后仍然留下的法律责任",
    PROJECT_HEADINGS[4]: "Zuno 自己承担的责任集中在材料、正式事实、长期引用、现实副作用、专业能力和质量证明六类问题。",
    PROJECT_HEADINGS[5]: "**材料版本与知识就绪。**",
    PROJECT_HEADINGS[6]: "**机器候选与正式业务事实。**",
    PROJECT_HEADINGS[7]: "**长期引用与结果失效。**",
    PROJECT_HEADINGS[8]: "**现实副作用与对账恢复。**",
    PROJECT_HEADINGS[9]: "**从研究成果到稳定专业能力。**",
    PROJECT_HEADINGS[10]: "**专业质量需要独立证据。**",
    PROJECT_HEADINGS[11]: "## 任务复杂度决定需要多少 Zuno",
    PROJECT_HEADINGS[12]: "**同一组法律责任可以落在三种产品形态。**",
    PROJECT_HEADINGS[13]: "**复杂机制都有退出条件。**",
    PROJECT_HEADINGS[14]: "## 项目真实走过的阶段",
    PROJECT_HEADINGS[15]: "**加入项目时，系统已经存在。**",
    PROJECT_HEADINGS[16]: "**Internal Demo 把链路带入内部验证。**",
    PROJECT_HEADINGS[17]: "**客户侧 Demo 暴露回答质量问题。**",
    PROJECT_HEADINGS[18]: "**法院侧测试进入更真实的使用环境。**",
    PROJECT_HEADINGS[19]: "**Pilot Validation 仍属于试点。**",
    PROJECT_HEADINGS[20]: "## 团队与个人参与的边界",
    PROJECT_HEADINGS[21]: "## 今天能够相信什么",
    PROJECT_HEADINGS[22]: "**设计已经说清责任，优势仍需要测量。**",
    PROJECT_HEADINGS[23]: "**仍需恢复的工程证据。**",
    PROJECT_HEADINGS[24]: None,
}

ARCH_HEADINGS = [
    "### A1. 法律智能真正变难的时刻",
    "### A2. 一件案件里的五种事实",
    "### A3. 四次跨边界决定系统是否可信",
    "### A4. 九个责任域如何从这些边界产生",
    "### A5. 故障以后，先找事实再恢复控制",
    "### A6. 研究成果怎样变成工程能力",
    "### A7. 安全、人和时间",
    "### A8. 复杂度必须在测量中证明收益",
    "### A9. 从目标架构进入实施",
    "### A10. 研究校准",
]

ARCH_MAP = {
    ARCH_HEADINGS[0]: "### 简单法律问答保持短路径",
    ARCH_HEADINGS[1]: "### 一项法律工作会同时留下五类事实",
    ARCH_HEADINGS[2]: "**四次跨边界动作让信息获得更强的业务语义。**",
    ARCH_HEADINGS[3]: "### 九个责任域来自事实 Authority",
    ARCH_HEADINGS[4]: "### 故障恢复先回到 Owner Fact",
    ARCH_HEADINGS[5]: "### 研究成果通过 Capability 与 Evaluation 进入工程",
    ARCH_HEADINGS[6]: "### 时间让安全成为持续决策",
    ARCH_HEADINGS[7]: "### 复杂度只有在测量中证明收益才保留",
    ARCH_HEADINGS[8]: "### 实施从 Authority、Completion Proof 和 Recovery 开始",
    ARCH_HEADINGS[9]: "**研究只用于校准设计方向。**",
}


def transform_headings(relative: str, expected: list[str], mapping: dict[str, str | None]) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    observed = [line for line in text.splitlines() if line.startswith(("## ", "### "))]
    # Project has only these story headings; Architecture also has the Part A heading.
    if relative.endswith("project/README.md"):
        filtered = observed
    else:
        filtered = [line for line in observed if line.startswith("### ")]
    if filtered != expected:
        raise RuntimeError(
            f"{relative}: heading inventory changed\nEXPECTED:\n" + "\n".join(expected)
            + "\nOBSERVED:\n" + "\n".join(filtered)
        )

    out: list[str] = []
    for line in text.splitlines():
        if line in mapping:
            replacement = mapping[line]
            if replacement is not None:
                out.append(replacement)
        else:
            out.append(line)
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")


def replace_once(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{relative}: expected one replacement, got {text.count(old)}\n{old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def edit_project_meta() -> None:
    path = "docs/project/README.md"
    replace_once(
        path,
        "Zuno 是南京大学软件学院 LIPLAB 智慧司法研究与工程化背景下的法律智能 Agent 平台，面向天津法院智慧平台相关场景。它所处理的不是单纯的“让模型回答一个法律问题”，而是怎样把研究成果、案件材料、模型与算法、人工判断以及业务系统连接起来，使一项法律工作在持续演进的材料和长时间运行的任务中仍然能够被解释、复核和恢复。",
        "Zuno 是南京大学软件学院 LIPLAB 智慧司法研究与工程化背景下的法律智能 Agent 平台，面向天津法院智慧平台相关场景。它把研究成果、案件材料、模型与算法、人工判断以及业务系统连接起来，使一项法律工作在持续演进的材料和长时间运行的任务中仍然能够被解释、复核和恢复。",
    )
    replace_once(
        path,
        "本章先讲项目本身。当前实现证据由 [`docs/evidence/`](../evidence/README.md) 维护；跨模块的目标设计进入 [`docs/architecture/README.md`](../architecture/README.md)；某一个责任域内部的状态、失败和恢复，则继续进入 [`docs/modules/`](../modules/README.md)。",
        "项目历史留在这里；当前实现证据由 [`docs/evidence/`](../evidence/README.md) 维护，跨模块 Target 由 [`docs/architecture/README.md`](../architecture/README.md) 维护，单个责任域的状态、失败和恢复进入 [`docs/modules/`](../modules/README.md)。",
    )
    replace_once(
        path,
        "Zuno 的起点不是“Agent 很流行，所以做一个 Agent 平台”，而是两条已经存在多年的线在工程上相遇。",
        "Zuno 的起点来自两条已经存在多年的线在工程上相遇。",
    )
    replace_once(
        path,
        "真正不能简单外包给“平台 Feature List”的，是项目必须自己承担的业务责任。通用平台可以保存工作流状态，却不会自动替一个法律项目定义什么是正式证据；可以提供 RAG，却不会自动决定一代索引是否足以支持当前案件范围；可以重试工具调用，却不会自动知道某个外部提交超时以后现实动作是否已经发生。这些问题不是平台强弱之争，而是专业语义最终由谁负责的问题。",
        "通用平台覆盖入口、工作流、RAG 和 Tool Calling 等基础能力，项目仍必须自己承担长期业务责任：什么是正式证据，一代知识是否足以支持当前案件范围，外部提交超时以后现实动作是否已经发生。这些问题最终落在专业语义的 Authority 上。",
    )
    replace_once(
        path,
        "所以 Zuno 的边界不是“别人做不到的都自己做”，而是：**通用能力优先复用；只有长期属于法律业务、事实权威和故障恢复的责任，才由 Zuno 自己拥有。**",
        "Zuno 的边界遵循一条约束：**通用能力优先复用；只有长期属于法律业务、事实权威和故障恢复的责任，才由 Zuno 自己拥有。**",
    )
    replace_once(
        path,
        "到这里，项目层已经完成了自己的任务：说明 Zuno 从哪里来，面对什么业务问题，为什么普通 RAG 和通用平台仍然留下专业工程责任，项目历史走到了哪里，以及今天哪些结论可以相信。\n\n下一层问题不再是“为什么立项”，而是“这些责任怎样组织成一个可以长期运行和恢复的系统”。这进入 [`docs/architecture/README.md`](../architecture/README.md)。总体架构负责解释跨模块的事实边界、正常流程和恢复原则；[`docs/modules/`](../modules/README.md) 再把这些原则落实到九个责任域；当问题变成“今天到底实现了多少”，则回到 [`docs/evidence/`](../evidence/README.md)。\n\n这三层分别回答项目因果、目标设计和当前证据。把它们分开，才能既把系统讲完整，又不把尚未实现或尚未证明的内容写成事实。",
        "这些项目事实把后续架构问题限定得很清楚：普通 RAG 和通用宿主已经足以覆盖简单任务；材料版本、正式业务事实、长期恢复和现实副作用则需要更明确的 Authority。[`docs/architecture/README.md`](../architecture/README.md) 从这些约束继续推导 Target Architecture，[`docs/modules/`](../modules/README.md) 把跨模块原则落实到九个责任域。今天究竟实现了多少仍由 [`docs/evidence/`](../evidence/README.md) 回答。\n\nProject、Architecture 和 Evidence 分别承担项目因果、目标设计和当前证明。尚未实现或尚未证明的内容不会因为故事完整而升级成事实。",
    )


def edit_architecture_meta() -> None:
    path = "docs/architecture/README.md"
    replace_once(
        path,
        "本文只描述设计阶段的目标系统。模块内部 Contract、状态机和事务细节进入 [`docs/modules/`](../modules/README.md)；长期架构决策进入 [`docs/decisions/`](../decisions/README.md)；代码、测试、性能和生产资格只有在 [`docs/evidence/`](../evidence/README.md) 出现真实证据以后，才属于 Current。研究和外部方案进入 [`docs/research/`](../research/README.md)，用于提出和校准设计，不构成实现证明。",
        "Target Architecture 只定义设计阶段的跨责任边界。模块内部 Contract、状态机和事务细节进入 [`docs/modules/`](../modules/README.md)；长期架构决策进入 [`docs/decisions/`](../decisions/README.md)；代码、测试、性能和生产资格只有在 [`docs/evidence/`](../evidence/README.md) 出现真实证据以后，才属于 Current。研究和外部方案进入 [`docs/research/`](../research/README.md)，用于提出和校准设计，不构成实现证明。",
    )
    replace_once(
        path,
        "Part A 解释设计为什么存在。第一次阅读只需要沿着案件、事实、跨边界动作和故障恢复往下读；内部 Contract 名称只在概念已经清楚以后出现。\n\n",
        "",
    )
    replace_once(
        path,
        "理解 Zuno 最容易的方法，不是先背九个模块，而是先看一项法律工作同时留下哪些事实。",
        "这些事实的 Authority、生命周期和恢复依据彼此不同。",
    )
    replace_once(
        path,
        "下面这些关系构成实施不能破坏的骨架：",
        "实施必须保护这些关系：",
    )


def verify_shape() -> None:
    project = (ROOT / "docs/project/README.md").read_text(encoding="utf-8")
    project_h2 = [line for line in project.splitlines() if line.startswith("## ")]
    expected_project = [
        "## 从智慧司法背景到长期法律工作",
        "## 通用平台之后仍然留下的法律责任",
        "## 任务复杂度决定需要多少 Zuno",
        "## 项目真实走过的阶段",
        "## 团队与个人参与的边界",
        "## 今天能够相信什么",
    ]
    if project_h2 != expected_project:
        raise RuntimeError(f"project H2 mismatch: {project_h2}")

    architecture = (ROOT / "docs/architecture/README.md").read_text(encoding="utf-8")
    arch_h3 = [line for line in architecture.splitlines() if line.startswith("### ")]
    expected_arch = [
        "### 简单法律问答保持短路径",
        "### 一项法律工作会同时留下五类事实",
        "### 九个责任域来自事实 Authority",
        "### 故障恢复先回到 Owner Fact",
        "### 研究成果通过 Capability 与 Evaluation 进入工程",
        "### 时间让安全成为持续决策",
        "### 复杂度只有在测量中证明收益才保留",
        "### 实施从 Authority、Completion Proof 和 Recovery 开始",
    ]
    if arch_h3 != expected_arch:
        raise RuntimeError(f"architecture H3 mismatch: {arch_h3}")


def main() -> None:
    transform_headings("docs/project/README.md", PROJECT_HEADINGS, PROJECT_MAP)
    transform_headings("docs/architecture/README.md", ARCH_HEADINGS, ARCH_MAP)
    edit_project_meta()
    edit_architecture_meta()
    verify_shape()


if __name__ == "__main__":
    main()
