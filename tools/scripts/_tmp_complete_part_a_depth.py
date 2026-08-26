from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def insert_before(path: str, marker: str, addition: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    if marker not in text:
        raise RuntimeError(f"marker not found in {path}")
    target.write_text(text.replace(marker, addition.strip() + "\n\n" + marker, 1), encoding="utf-8")


ARCH = r'''
### 26. 一个架构边界是否成立，最终要看它能不能减少错误的“推断”

复杂系统最危险的 bug 往往不是某个函数算错，而是 A 模块看到 B 模块的一个状态后，推断出了它其实没有资格知道的结论：看到索引构建完成就推断任务 READY，看到 Step completed 就推断 Domain 已提交，看到 HTTP timeout 就推断 Effect 失败，看到旧 Authorization allow 就推断未来仍允许。

因此 Zuno 的边界设计可以用一个很朴素的问题验收：**这个模块对外暴露的事实，是否足够让消费者做正确判断，同时又没有诱导它推断更强事实？** 如果一个 Contract 经常需要消费者“顺便猜一下”，说明 Owner 或 completion proof 仍然不够清楚；如果每个消费者都复制同样判断逻辑，则应该把判断收回真正的 Authority。

这也是为什么文档质量本身属于架构质量。读者如果必须依赖内部名词和隐含惯例才能知道谁说了算，工程实现更容易重复同样误判。Human Narrative 先把因果讲清，Engineering Reference 再冻结精确语义，两层共同减少错误推断，而不是让术语数量成为复杂度的遮羞布。

另一个验收方法是做“删除测试”：暂时拿掉某个边界，看看错误推断是否重新出现。如果删除独立 Domain authority 后 Runtime completed 就被迫承担正式业务含义，说明该边界确有必要；如果拿掉某个额外层后所有重要不变量仍然能被更简单组件保护，就应该质疑这层复杂度。边界的价值必须表现为减少真实歧义、故障或责任冲突，而不是让架构图更对称。
'''

M02 = r'''
### Human Review 为什么不能只保存“最终同意了”

专业人员介入的价值不仅是给模型结果盖章。人可能接受一部分、修改另一部分、拒绝某条 Finding，也可能因为材料不足要求补证。如果系统只保存最终 `approved=true`，未来无法解释哪些内容来自机器、哪些是人工修订，也无法把人工判断用于后续质量评测。

因此 HumanDecision 应绑定被判断的业务对象版本和决策内容，必要时保存结构化修改或理由引用。它仍然不是把所有编辑过程录屏，而是留下足以解释正式结果的专业责任链。新的对象版本产生后，旧 HumanDecision 是否仍适用也需要按因果重新判断，不能成为永久“人工已审”标签。

这条边界让人机协作真正进入 Domain，而不是停留在 UI 层按钮状态；同时 09 可以在不把人工决定改写成模型标签的前提下，统计 reviewer acceptance、修改类型和常见失败模式。
'''

M05 = r'''
### Capability 的失败语义为什么要允许“不会做”，而不是强迫每个 Provider 给答案

专业系统容易把 Provider success rate 当成目标，于是实现会倾向于任何输入都返回一个结构完整的结果。但某个 Capability 可能只支持特定材料类型、语言、案件阶段或风险等级；超出已验证范围时，最安全的行为是明确 unsupported / insufficient / review required。

这种“有边界的不会做”必须进入 Capability 语义，否则 Runtime 无法区分“任务本来不适用”和“Provider 临时坏了”。前者可能需要换 Capability、Replan 或人工，后者才适合 retry / fallback。同样，Eval 也应该惩罚在未知范围里自信输出，而不是只奖励覆盖率。

Capability 越能精确声明自己的适用范围，上层越不需要依赖模型自报 confidence 来猜是否可信。专业能力的成熟度不在于永远返回答案，而在于知道自己的资格边界。

### 专业能力的组合为什么不应该产生隐藏的“超级 Capability”

一个复杂法律分析可能组合事件抽取、证据比较、法条检索和综合判断。为了调用方便，把整条链包装成一个巨大 Capability 看起来很省事，但会重新隐藏每一步的版本、失败和质量责任。某个子能力升级后，团队也无法判断最终变化来自哪里。

更合理的是只在业务上确实形成稳定整体语义时才提供组合能力，并继续保留关键子能力的 causation。Runtime 可以编排多个 Capability，05 负责每个专业边界的契约和资格；不要因为“一个接口更简单”就牺牲可替换性和可评测性。组合层如果没有独立专业语义，应留在 Runtime Plan，而不是升级成新的长期能力类型。
'''

M06 = r'''
### “已确认效果”为什么也不等于“远端所有业务语义都完成”

06 能证明的是 Zuno 关心的现实动作结果，例如某个创建请求对应远端记录已经存在、某个提交动作被目标系统接收。它不一定拥有远端系统内部更后续的审批、展示、归档或人工采用状态。

因此 EffectReceipt 需要清楚描述它证明的 Effect boundary，而不是使用含糊的 `SUCCESS` 让上层推断“对方全部处理完成”。如果产品还需要观察远端后续状态，应通过明确查询或 01 的 consumer observation 建模，而不是扩大 06 的权威范围。

这个限制也保护集成可替换性：Zuno 只承诺自己能够用 API、业务唯一键或回执证明的现实事实，不因为缺少对远端数据库的直接控制就伪造更强一致性。

### Tool Adapter 为什么不能吞掉远端的不确定性

SDK 或 Adapter 常常会把底层异常统一成一个漂亮的 `ToolError`。如果这个抽象把“请求尚未发送”“请求已发送但响应未知”“远端明确拒绝”全部合并，上层就失去了选择 Retry 或 Reconcile 所需的信息。

因此 Adapter 应保留影响 Effect truth 的最小传输事实，06 再根据 Tool semantics 判断恢复。抽象的目标是隐藏无关协议细节，不是隐藏决定正确性的故障窗口。一个好的 Tool abstraction 应该让调用方更难误重试，而不是让所有错误看起来一样简单。
'''

M07 = r'''
### Model Usage 为什么既是成本事实，也是恢复事实

模型调用已经发出后，即使上层后来取消 Run、拒绝结果或 Replan，Provider 仍可能已经消耗 token 并产生费用。只在“最终采用结果”上记成本，会系统性低估失败链和 fallback 的真实代价。

因此每个 Attempt 的 Usage 应独立 settlement，再沿 causation 归因到 Run / Step。这样 04 可以看见当前 Budget 还剩多少，09 也能回答一次 Reflection、Planner retry 或 Provider fallback 到底放大了多少成本。

Usage 同时帮助解释取消边界：本地 cancel 并不撤销已经发生的远端计算。系统可以停止等待或阻止后续调用，但不能为了让 Run 状态好看而把已发生资源事实删除。

### Provider abstraction 为什么不能追求“所有模型行为完全一样”

统一 API 能屏蔽认证、请求格式和基础 structured output 差异，但不同模型在上下文窗口、tool calling、推理延迟、语言表现和拒答策略上天然不同。如果 Gateway 试图用越来越多隐藏转换把它们伪装成完全等价，上层最终会依赖一套没人能解释的后处理。

更合理的是统一真正稳定的调用 contract，同时让 Role qualification 显式表达差异。上层依赖“这个模型满足当前 Role 的最低行为要求”，而不是相信所有 Provider 是可无损替换的同一种函数。抽象应减少偶然差异，不能抹掉决定质量的真实差异。
'''

M08 = r'''
### 安全拒绝为什么也需要可解释，而不是只返回 403

高风险系统必须 fail closed，但如果拒绝只有一个通用 `DENY`，工程师和业务人员无法判断是权限不足、数据外发限制、Approval 缺失、SecurityEpoch 过期、Secret 不可用还是 Legal Hold 导致。结果往往是调用方为了“修复可用性”绕开门禁。

08 因此应该返回最小但可解释的 decision reason / requirement：告诉消费者下一步是禁止、等待审批、重新获取当前决定、切换允许 Provider，还是必须人工处理。敏感策略细节不必暴露给不可信客户端，但可信内部模块需要足够信息选择正确恢复路径。

可解释拒绝并不意味着上层可以修改安全判断。01 可以把原因翻译成用户行动，04 可以等待或 Replan，07 可以换到允许的 Provider，但只有 08 能在条件变化后形成新的 Authorization / Approval 事实。
'''


def main() -> None:
    insert_before("docs/architecture/architecture.md", "### 19. Current、Target、Evidence 和 Unknown 必须始终分开", ARCH)
    insert_before("docs/modules/02-legal-domain-work-product.md", "### 当前、目标与缺口", M02)
    insert_before("docs/modules/05-capability-skill.md", "### 当前、目标与缺口", M05)
    insert_before("docs/modules/06-tool-runtime-effects.md", "### 当前、目标与缺口", M06)
    insert_before("docs/modules/07-model-gateway.md", "### 当前、目标与缺口", M07)
    insert_before("docs/modules/08-security-governance.md", "### 当前、目标与缺口", M08)
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
