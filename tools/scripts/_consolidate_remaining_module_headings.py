from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

RUNTIME = [
    '### 这个模块解决的是“长任务怎样继续”，不是“让很多 Agent 自己商量”',
    '### 最简单的 while-loop Agent 为什么难以恢复',
    '### Single Controller 为什么是控制权约束，不是“只有一个模型”',
    '### 为什么需要三层 Graph，而不是把所有动态性塞进 LangGraph 拓扑',
    '### 为什么 PlanVersion 激活后不能原地修改',
    '### Ready Step 为什么不能只看“前驱 completed”',
    '### 并行和 Join 为什么最容易暴露控制语义问题',
    '### Step 执行成功为什么不等于业务完成',
    '### Retry != Replan != Reconcile',
    '### Replan Barrier 为什么需要一个清楚的切换点',
    '### Late Result 为什么既不能一律丢，也不能一律收',
    '### Checkpoint 为什么是恢复工具而不是业务数据库',
    '### Interrupt / Resume 为什么必须带新鲜度检查',
    '### Lease 和 Fencing 为什么只解决 Controller 所有权，不解决业务正确性',
    '### Budget 和取消为什么也是控制事实',
    '### 为什么 Runtime 应优先复用框架而不是自研宿主能力',
    '### Controller 为什么要把“决定”和“执行”分离',
    '### Dynamic Plan 为什么不等于“每一步都让 LLM 重规划”',
    '### 并行度为什么受正确性和资源双重约束',
    '### 恢复为什么不能简单重放全部 Node',
    '### Runtime 的复杂度什么时候应该退回普通 Workflow',
    '### “等待”为什么有时是正确进展，而不是 Runtime 卡死',
    '### Plan 激活前为什么要证明它至少可执行，而不是只看 LLM 输出像不像计划',
    '### Runtime 负载准入为什么和 Step 并行度是两个问题',
    '### Checkpoint 为什么不应该无限长成完整事件仓库',
    '### 当前、目标与缺口',
]

CAPABILITY = [
    '### 这个模块解决的是“专业能力怎样成为产品契约”，不是“把所有算法包装成 Tool”',
    '### 最简单的 provider.call() 为什么会慢慢失去边界',
    '### Capability = 稳定专业语义',
    '### Provider 为什么必须和 Capability 分开',
    '### Provider Conformance != task quality',
    '### provider execution failure 和 capability semantic drift 为什么是两类故障',
    '### Eligibility 为什么不是“服务健康”',
    '### Invocation 为什么需要绑定版本和输入身份',
    '### Fallback 为什么必须保护专业语义',
    '### Cache 为什么不能把专业输出变成永久事实',
    '### Capability、Model 和 Tool 为什么不能混成一个抽象',
    '### 研究成果怎样进入 Capability，而不是直接进入架构',
    '### 为什么强模型不能成为所有 Capability 的默认答案',
    '### Provider 退出为什么必须是正常路径',
    '### 什么时候 05 应该更简单',
    '### Capability Version 什么时候应该变，Provider Version 什么时候应该变',
    '### Deterministic Capability 和 Generative Capability 为什么可以共享能力边界',
    '### Qualification 为什么要和 Release 生命周期绑定',
    '### Build / Buy 对专业能力意味着什么',
    '### 05 为什么不应该变成中央 Prompt / Plugin 市场',
    '### Capability 的失败语义为什么要允许“不会做”，而不是强迫每个 Provider 给答案',
    '### 专业能力的组合为什么不应该产生隐藏的“超级 Capability”',
    '### Schema 兼容为什么不等于 Capability 语义兼容',
    '### 资格为什么应该绑定已验证范围，而不是给 Provider 一个全局绿色勾',
    '### Provider 退役为什么要考虑正在运行和历史结果',
    '### 研究结果进入 Capability 为什么必须能被复现，而不是只引用论文结论',
    '### 当前、目标与缺口',
]

EFFECTS = [
    '### 这个模块从一个最危险的问题开始：HTTP 超时以后，现实世界到底发生了什么',
    '### 最简单的 try/except + Retry 为什么会制造重复副作用',
    '### Transport Success 不等于 Effect Success',
    '### 为什么先“准备动作”，再真的发送',
    '### PreparedAction 保护的是什么',
    '### 幂等为什么既看 key，也看动作内容',
    '### Send Boundary 为什么是恢复设计的关键切点',
    '### Outcome Unknown（结果未知）不得映射为普通 Failed',
    '### Reconcile 到底在做什么',
    '### Retry Safety 为什么必须按操作分类',
    '### Authorization、Approval 和 Audit 为什么在执行前重新检查',
    '### Compensation 为什么不是“把旧 Receipt 改成失败”',
    '### Crash Window 为什么要围绕耐久事实设计',
    '### Delivery 和 Tool Effect 为什么要协作而不是合并',
    '### 模型为什么只能提出动作，不能批准自己',
    '### 什么时候 06 可以很薄',
    '### Exactly-once 为什么通常不是可以对外承诺的现实语义',
    '### Effect Class 为什么应该影响默认策略',
    '### Remote Idempotency 为什么必须被验证而不是相信文档一句话',
    '### Reconciliation 为什么需要明确终止条件',
    '### Compensation 为什么不能被当作事务 rollback',
    '### “已确认效果”为什么也不等于“远端所有业务语义都完成”',
    '### Tool Adapter 为什么不能吞掉远端的不确定性',
    '### 人工对账为什么也必须重新进入结构化恢复链',
    '### 幂等为什么解决不了两个“不同但冲突”的动作',
    '### Outcome Unknown 积压为什么本身就是一种运行风险',
    '### 远端 API schema 没变，Effect 语义也可能已经漂移',
    '### 自动化边界为什么应该受“可确认性”约束',
    '### 当前、目标与缺口',
]

MODEL_GATEWAY = [
    '### 这个模块解决的是“模型怎样成为受控依赖”，不是“所有 AI 逻辑都放到网关”',
    '### 最简单的“每个模块自己调 SDK”为什么会失控',
    '### Model Role 与具体 Provider / Model 解耦',
    '### Provider technically available 为什么远远不等于当前能用',
    '### 为什么模型输出永远先是 Proposal',
    '### 为什么调用成功要和上层成功保持距离',
    '### 强模型和弱模型为什么应该按任务价值分配',
    '### Routing 为什么要同时看质量、安全、预算和延迟',
    '### Retry 和 Fallback 为什么必须有边界',
    '### Budget / Quota 为什么要累计整个失败链',
    '### Cancellation 为什么不能只记录一个本地 flag',
    '### Timeout 后启动 fallback 为什么会产生竞态',
    '### Prompt ownership 为什么不应该全部归 Gateway',
    '### Structured output 为什么需要两层校验',
    '### Cache 为什么默认不能假设模型调用幂等',
    '### Secret 和业务数据为什么是两种不同治理问题',
    '### 为什么 Model Gateway 默认不需要独立微服务',
    '### 模型版本漂移为什么即使 API 不变也值得治理',
    '### 路由稳定性为什么有时比每次选“当前最优”更重要',
    '### Deadline 为什么和 Budget 一样属于路由约束',
    '### Provider outage 的降级为什么要区分 Role',
    '### Model Gateway 的缓存为什么要谨慎对待上下文安全',
    '### Model Usage 为什么既是成本事实，也是恢复事实',
    '### Provider abstraction 为什么不能追求“所有模型行为完全一样”',
    '### 模型调用的“可复现”为什么只能是有边界的可复现',
    '### Model Gateway 为什么不应该决定“哪些证据放进 Prompt”',
    '### Quota 紧张时为什么要保护任务级公平，而不是谁先重试谁占满',
    '### 价格变化为什么也可能让原来的路由策略失效',
    '### 当前、目标与缺口',
]

SECURITY = [
    '### 这个模块保护的不是“用户是否登录”，而是“下一步现在还能不能做”',
    '### 最简单的“登录 + RBAC”为什么覆盖不了长任务',
    '### Continuous Authorization（持续授权）到底意味着什么',
    '### 为什么三种“人点同意”必须拆开',
    '### Approval 为什么必须绑定具体动作而不是 Step 编号',
    '### 模型外发为什么由安全策略决定，不由 Model Gateway 决定',
    '### Secret 为什么只传引用和短期 Lease',
    '### Mandatory Audit 为什么和普通 Trace 不是一回事',
    '### Prompt Injection 为什么不能靠“更聪明的模型”解决',
    '### 数据生命周期为什么不能只有 deleted=true',
    '### 为什么跨 Store 删除不应该追求一个巨大 2PC',
    '### 安全服务不可用时为什么高风险路径默认 fail closed',
    '### 撤权发生在不同时间点为什么结果不同',
    '### SecurityEpoch 为什么是新鲜度边界',
    '### Decision Cache 为什么不能变成永久 Capability Token',
    '### 多租户隔离为什么必须跟着资源引用走',
    '### 什么时候 08 应该更简单',
    '### Policy Decision 和 Policy Enforcement 为什么必须分开',
    '### Security Freshness 为什么不等于把 TTL 设得极短',
    '### 可信身份为什么不能来自调用方自己提交的字段',
    '### Approval 为什么自己也有生命周期',
    '### Audit 数据本身为什么也需要最小化和生命周期',
    '### 安全平台哪些应该 Buy，哪些必须由 Zuno 定义',
    '### 安全拒绝为什么也需要可解释，而不是只返回 403',
    '### Authorization 到真正执行之间为什么还存在 TOCTOU 风险',
    '### 后台 Worker 为什么不能继承用户的全部长期权限',
    '### “允许执行”为什么不等于“这个动作业务上是正确的”',
    '### Policy 版本升级为什么也需要兼容和可回溯',
    '### 当前、目标与缺口',
]

EVALUATION = [
    '### 这个模块其实在回答两个不同问题：发生了什么，以及这样做值不值得',
    '### 最简单的“Trace 里有完整链路，所以 Trace 就是真相”为什么危险',
    '### 事故调查为什么应该先问 Owner Fact',
    '### Correlation 为什么重要，但不能成为万能业务 ID',
    '### OpenTelemetry Baggage 为什么要保持最小化',
    '### Sampling 为什么只能影响观测细节',
    '### Eval Dataset 为什么必须版本化',
    '### 训练暴露为什么必须和测试集分开',
    '### LLM Judge 为什么只能处理适合模型判断的问题',
    '### PASS、FAIL 和 BLOCKED 为什么必须严格区分',
    '### 为什么 Critical Failure 可以否决漂亮平均分',
    '### 为什么要同时评质量、恢复、延迟和成本',
    '### 为什么指标必须按 Task Class 分层',
    '### Evaluation 为什么应该主动帮助删除复杂度',
    '### Provider-neutral Observability 为什么重要',
    '### Telemetry Provider outage 为什么不应该阻断普通业务',
    '### Release Evidence 为什么不等于 Production Readiness',
    '### 好的 Observability 为什么从问题出发，而不是从“所有地方都打日志”出发',
    '### Eval 为什么必须先定义 Decision，再选择 Metric',
    '### Counterfactual / Ablation 为什么是复杂 Agent 架构的核心证据',
    '### 线上指标和离线 Eval 为什么互相不能替代',
    '### Release Gate 为什么应该能够说“不知道”',
    '### 成本归因为什么必须沿因果链，而不是只看 Provider 月账单',
    '### SLO 和 Eval 为什么不能合成一个“系统分数”',
    '### Correlation 为什么能帮助解释，却不能证明因果',
    '### Metric 变成目标以后，为什么要主动防 Goodhart',
    '### Eval 成本为什么需要分层，而不是所有提交都跑最贵 Judge',
    '### 事故案例进入 Dataset 时为什么要防止测试集被慢慢训练掉',
    '### 当前、目标与缺口',
]


def consolidate(relative: str, expected: list[str], replacements: dict[str, str | None], target_count: int) -> None:
    path = ROOT / relative
    text = path.read_text(encoding='utf-8')
    observed = [line for line in text.splitlines() if line.startswith('### ')]
    if observed != expected:
        raise RuntimeError(
            f'{relative}: heading inventory changed\nEXPECTED:\n' + '\n'.join(expected) + '\nOBSERVED:\n' + '\n'.join(observed)
        )

    out: list[str] = []
    for line in text.splitlines():
        if line.startswith('### '):
            replacement = replacements.get(line)
            if replacement is None:
                continue
            out.append(replacement)
        else:
            out.append(line)
    path.write_text('\n'.join(out).rstrip() + '\n', encoding='utf-8')

    after = path.read_text(encoding='utf-8')
    count = sum(1 for line in after.splitlines() if line.startswith('### '))
    if count != target_count:
        raise RuntimeError(f'{relative}: expected {target_count} macro headings, got {count}')


def main() -> None:
    consolidate(
        'docs/modules/runtime/README.md', RUNTIME,
        {
            RUNTIME[0]: '### 长任务需要可恢复的控制平面',
            RUNTIME[2]: '### Single Controller 收敛控制权，三层 Graph 分离稳定拓扑与动态计划',
            RUNTIME[4]: '### 不可变 PlanVersion 让并行、Join 与新鲜度共享控制基线',
            RUNTIME[8]: '### Retry != Replan != Reconcile',
            RUNTIME[11]: '### Checkpoint 记录控制进度，Owner Fact 决定恢复结果',
            RUNTIME[15]: '### Runtime 优先复用框架，复杂度只在长任务约束出现时保留',
            RUNTIME[25]: '### 当前、目标与缺口',
        }, 7,
    )
    consolidate(
        'docs/modules/capability/README.md', CAPABILITY,
        {
            CAPABILITY[0]: '### 专业能力先成为稳定产品契约，再选择实现',
            CAPABILITY[2]: '### Capability = 稳定专业语义',
            CAPABILITY[4]: '### Provider Conformance != task quality',
            CAPABILITY[10]: '### Capability、Model 和 Tool 保持不同责任边界',
            CAPABILITY[11]: '### 研究成果通过复现与 Qualification 才进入 Capability',
            CAPABILITY[15]: '### 版本、资格与 Provider 生命周期共同保护可替换性',
            CAPABILITY[26]: '### 当前、目标与缺口',
        }, 7,
    )
    consolidate(
        'docs/modules/effects/README.md', EFFECTS,
        {
            EFFECTS[0]: '### 外部副作用的第一问题是现实世界发生了什么',
            EFFECTS[2]: '### Transport Success 不等于 Effect Success',
            EFFECTS[3]: '### PreparedAction 和 Send Boundary 把意图与发送分开',
            EFFECTS[7]: '### Outcome Unknown（结果未知）不得映射为普通 Failed',
            EFFECTS[8]: '### Reconcile、Retry Safety 与 Compensation 收敛不确定结果',
            EFFECTS[12]: '### Crash Window、幂等与远端语义共同决定恢复策略',
            EFFECTS[16]: '### Exactly-once 不作为承诺，自动化上限由可确认性决定',
            EFFECTS[28]: '### 当前、目标与缺口',
        }, 8,
    )
    consolidate(
        'docs/modules/model-gateway/README.md', MODEL_GATEWAY,
        {
            MODEL_GATEWAY[0]: '### 模型调用需要成为受控依赖，而不是散落的 SDK 调用',
            MODEL_GATEWAY[2]: '### Model Role 与具体 Provider / Model 解耦',
            MODEL_GATEWAY[3]: '### Provider 资格与模型输出都必须服从当前任务边界',
            MODEL_GATEWAY[6]: '### Routing 在质量、安全、预算和延迟之间做受约束选择',
            MODEL_GATEWAY[8]: '### Retry、Fallback、Cancellation 与 Deadline 共同形成调用生命周期',
            MODEL_GATEWAY[12]: '### Prompt、Structured Output、Cache 与 Secret 各有自己的 Owner',
            MODEL_GATEWAY[16]: '### Gateway 默认是逻辑责任，版本漂移和 Provider 差异由治理吸收',
            MODEL_GATEWAY[28]: '### 当前、目标与缺口',
        }, 8,
    )
    consolidate(
        'docs/modules/security/README.md', SECURITY,
        {
            SECURITY[0]: '### 安全判断贯穿每一次受保护动作',
            SECURITY[2]: '### Continuous Authorization 让长任务持续消费当前安全事实',
            SECURITY[3]: '### AuthorizationDecision、ApprovalDecision、HumanDecision 三者 Owner 与语义不同',
            SECURITY[5]: '### 外发、Secret、Mandatory Audit 与 Prompt Injection 形成执行前边界',
            SECURITY[9]: '### 数据生命周期和撤权需要跨 Store 收敛，而不是伪装成单事务',
            SECURITY[11]: '### Fail-closed、SecurityEpoch 与 Decision Cache 共同保护新鲜度',
            SECURITY[17]: '### Policy Decision 与 Enforcement 分离，身份和多租户边界跟随资源',
            SECURITY[28]: '### 当前、目标与缺口',
        }, 8,
    )
    consolidate(
        'docs/modules/evaluation/README.md', EVALUATION,
        {
            EVALUATION[0]: '### Observability 解释发生了什么，Evaluation 判断设计是否值得保留',
            EVALUATION[1]: '### Trace 只能解释过程，事故调查先回到 Owner Fact',
            EVALUATION[3]: '### Correlation、OpenTelemetry Baggage 与 Sampling 只服务观测，不升级成业务权威',
            EVALUATION[6]: '### Eval Dataset、Judge 与 PASS / FAIL / BLOCKED 需要版本化边界',
            EVALUATION[10]: '### 质量、恢复、延迟和成本必须按 Task Class 一起评估',
            EVALUATION[13]: '### Evaluation 的职责包括主动删除没有收益的复杂度',
            EVALUATION[18]: '### 先定义 Decision，再选 Metric；Ablation 与线上数据共同解释因果',
            EVALUATION[28]: '### 当前、目标与缺口',
        }, 8,
    )


if __name__ == '__main__':
    main()
