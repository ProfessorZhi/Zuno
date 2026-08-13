RED Q001

当新 Evidence 到来、两个能力组件给出冲突结论、用户又要求立即出结果时，为什么不能让 Agent Runtime、Knowledge Provider 或 Checkpoint 直接把其中一个写成案件结论？请用普通工程语言说明：谁拥有把候选提升为正式业务状态的决定权、需要守住哪些边界，以及旧结论已经被展示后应如何处理。

BLUE A001

不能，因为它们都不是案件结论的权威所有者：Agent Runtime 负责 Run、Plan、Step 和恢复位置；Knowledge Provider 负责解析、检索并提供证据候选；Checkpoint 只记录执行状态，不能代表业务事实已提交。只有 Domain Owner 能在证据版本、来源、权限、冲突、依赖和必要人工复核完成后，把候选提升为正式业务状态。冲突结论必须保留各自依据和冲突状态，不能因为用户要求立即结果就选择一个，也不能把队列确认、Checkpoint 保存或 Provider 返回当成案件成功。若旧结论已经展示，新 Evidence 到来后，应将受影响结论标记为 STALE 或 REVIEW_REQUIRED，保留旧版本和展示记录，但不再把它当作当前最终结论。之后由 Domain Owner 对最新领域版本、Knowledge 投影、Runtime 状态和授权进行对账，再决定重新规划、人工复核、修订 WorkProduct 或维持原结论。

part_a_support=SUFFICIENT; answer_source=PART_A

RED CHAIN DECISION

CONTINUE_CHAIN: A001明确了Domain Owner和若干提升前置条件，但未闭合这些条件发生冲突或并发变化时的最终裁决边界。

RED Q002

如果两个不同版本的 Evidence 同时支持相互冲突的事实，权限检查分别通过但人工复核尚未完成，而 Runtime 又需要继续执行，谁有权决定候选能否进入正式案件状态？未被批准的候选、正在复核的候选和已经展示过的旧结论分别处于什么边界？

BLUE A002

权限通过只说明材料可以被系统使用，不说明哪一版本的事实正确。两份证据冲突且人工复核未完成时，候选不能进入正式案件状态。决定权属于 Domain Owner；如果该结论需要人工判断，还必须等待人工复核形成决定。执行控制层可以继续处理不依赖该结论的工作，也可以暂停、重新规划或给出明确带有限定条件的部分结果，但不能自行选定一方，更不能据此完成不可逆动作。未批准候选保留来源、版本、权限和冲突信息，只是待裁决材料；正在复核候选属于待审核状态；已展示旧结论保留历史版本，新证据影响时标记过时或需复核，不能静默覆盖。

part_a_support=SUFFICIENT; answer_source=PART_A

RED CHAIN DECISION

CONTINUE_CHAIN: A002明确了待裁决候选、复核中候选和历史旧结论的边界，但尚未说明只读分析、计划生成和副作用阻断的责任。

RED Q003

如果冲突中的候选不能作为正式事实或不可逆动作依据，Runtime 在人工复核完成前是否可以把它用于只读分析或生成待审计划？谁负责确保这些候选不会越过边界触发外部副作用，复核完成后又如何判断原计划是否仍然有效？

BLUE A003

可以，但只能把它当作尚未确认的输入。人工复核前可做只读比较、影响分析或生成未激活待审计划；计划记录证据和冲突依赖，不能提交案件结论、发送、修改数据或触发外部动作。执行控制层标记未决依赖，Domain Owner负责正式状态，Tool/Security负责外部副作用拦截。复核后重新检查证据版本、事实、冲突、权限和效果记录，前提未变才恢复，变化则重新规划，未知效果先对账。

part_a_support=PARTIAL; answer_source=PART_A_PLUS_GENERAL_KNOWLEDGE

RED CHAIN DECISION

CLOSE_CHAIN: A003已闭合当前所有权边界：未决候选可用于受限只读工作但必须标记依赖，执行控制层阻止自动执行，Domain Owner提交正式状态，Tool/Security拦截外部副作用；复核后需重新验证前提，必要时Replan并对账未知效果。


