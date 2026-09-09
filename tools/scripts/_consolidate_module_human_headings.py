from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

APPLICATION = [
    '### 这个模块首先解决“外部产品看到什么”，而不是“谁离用户近谁就拥有一切”',
    '### 最简单的入口层为什么很快会遇到边界问题',
    '### 负责组合，不负责重新发明事实',
    '### Scope 为什么必须先于 Agent 和模型',
    '### 外部身份声明为什么不能直接升级成权限',
    '### 简单问答为什么应该保持短路径',
    '### 复杂任务为什么需要显式 Invocation，而不是一个巨大 if/else',
    '### 四种“完成”为什么必须明确分开',
    '### 普通答案和正式 WorkProduct 为什么不能共用同一条发布权威',
    '### Agent Version = 产品能力 / 配置版本',
    '### 新证据出现以后，为什么“失效”和“通知成功”必须分开',
    '### 为什么 Push 和 Pull 都有价值',
    '### Delivery 为什么需要独立身份',
    '### 为什么有副作用的 Delivery 要交给 06',
    '### Consumer Ack 为什么只能叫 Observation',
    '### 重复请求为什么不应该启动第二个复杂 Run',
    '### 取消为什么只是停止还能停止的未来工作',
    '### Host Adapter、Backpressure 和 Contract Version 为什么属于产品边界',
    '### 什么时候这个模块应该更简单',
    '### 同步 API 和异步任务为什么要共享业务语义，而不是共享传输形态',
    '### 发布决定为什么也需要新鲜度，而不能只在生成结束时判断一次',
    '### 为什么产品状态应该面向用户行动，而不是暴露内部状态机全集',
    '### 多 Host 场景下为什么不能把一个消费者的确认当成全局完成',
    '### 01 的复杂度预算应该花在哪里',
    '### Application Projection 为什么可以缓存，但不能成为新的业务真相',
    '### API 兼容为什么不仅是字段能不能解析',
    '### 入口过载时为什么要拒绝、排队或降级，而不是无限接受',
    '### 当前、目标与缺口',
]

DOMAIN = [
    '### 这个模块回答的是“什么才算正式法律业务事实”',
    '### 最简单的“把最终答案存进数据库”为什么不够',
    '### 候选和正式事实必须有一道清楚的门',
    '### 为什么需要一组很小但稳定的领域对象',
    '### Formal Admission 为什么必须留下耐久证明',
    '### 为什么 DomainVersion 不能被 Runtime 的 completed 覆盖',
    '### WorkProduct 为什么不能只保存最终文本',
    '### 检索引用为什么不能直接成为正式成果引用',
    '### 人工业务决定和安全审批为什么必须分开',
    '### 新证据出现以后为什么要保留历史而不是覆盖旧结果',
    '### 为什么失效传播应该有界而不是一律全案重跑',
    '### 并发正式提交为什么不能靠“最后写入者获胜”',
    '### 幂等为什么必须绑定 canonical 业务输入',
    '### 崩溃恢复为什么先读 Domain 而不是先重放 Agent',
    '### 02 不应该拥有什么',
    '### 什么时候领域模型应该更简单',
    '### 正式领域模型为什么描述业务关系，而不是模型推理过程',
    '### “正式”为什么不是一个 boolean，而是一种事务边界',
    '### Domain Version 为什么是乐观并发的因果保护，而不是数据库技巧',
    '### 失效为什么要和删除区分',
    '### 领域复杂度什么时候应该停止增长',
    '### Human Review 为什么不能只保存“最终同意了”',
    '### “正式事实”为什么不是“客观法律真理”',
    '### 相互冲突的 Evidence 为什么可以同时正式存在',
    '### 修正历史错误为什么应该形成新版本，而不是偷偷改旧记录',
    '### 当前、目标与缺口',
]

KNOWLEDGE = [
    '### 这个模块先解决一个反直觉问题：文件到了，不代表任务已经能用',
    '### 最简单的一份文件一个向量索引为什么会失效',
    '### 正式材料、知识派生和任务就绪为什么是三层',
    '### KnowledgeGeneration lifecycle != task-level ReadinessDecision',
    '### 为什么部分完成必须显式，而不能假装成功',
    '### 检索命中为什么仍然只是候选',
    '### CitationLineage 为什么只解释“怎么找到的”',
    '### 为什么一条 Retrieval Pipeline 不应该处理所有问题',
    '### 多路检索以后为什么还需要停止条件',
    '### GraphRAG 为什么只能是条件能力',
    '### 新材料进入时为什么不能原地修改 serving 索引',
    '### Worker 重试为什么不能让部分写入变成“已激活”',
    '### Cache 为什么只能优化派生数据',
    '### 权限变化为什么会让“之前算好的知识”暂时不可用',
    '### Knowledge stale 和 Domain stale 为什么属于不同 Owner',
    '### 什么时候 03 应该更简单',
    '### Processing Spec 为什么必须进入 generation 身份',
    '### Readiness 为什么必须按 Required Capability 判断',
    '### Retrieval Quality 为什么不仅是 Recall@K',
    '### Serving 切换为什么比“所有 Store 同时完成”更现实',
    '### 数据生命周期为什么要区分“停止召回”和“物理清除”',
    '### “没检索到”为什么不能直接解释成“材料里没有”',
    '### 检索结果为什么要保留来源多样性，而不是只追求相似度最高',
    '### 新一代知识构建失败时，为什么旧 Serving 不应该一起被拖垮',
    '### Ingestion 和 Retrieval 为什么需要不同的资源隔离',
    '### 当前、目标与缺口',
]


def consolidate(relative: str, expected: list[str], replacements: dict[str, str | None]) -> None:
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


def main() -> None:
    consolidate(
        'docs/modules/application/README.md',
        APPLICATION,
        {
            APPLICATION[0]: '### 从外部请求到稳定产品语义',
            APPLICATION[6]: '### 复杂任务把受理、运行、正式结果和发布拆成不同事实',
            APPLICATION[9]: 'Agent Version = 产品能力 / 配置版本，它和某一次运行内部的 PlanVersion 属于不同层次。',
            APPLICATION[10]: '### 结果离开当前请求以后，失效与交付成为长期问题',
            APPLICATION[13]: '### 一旦交付改变外部世界，Effect truth 必须离开 Application',
            APPLICATION[19]: '### 多 Host 与异步接口共享业务语义，不共享传输形态',
            APPLICATION[23]: '### 复杂度预算只花在产品边界真正需要的地方',
            APPLICATION[27]: '### 当前、目标与缺口',
        },
    )
    consolidate(
        'docs/modules/domain/README.md',
        DOMAIN,
        {
            DOMAIN[0]: '### 从机器输出到正式法律业务事实',
            DOMAIN[4]: '### 正式提交必须留下可以跨崩溃恢复的证明',
            DOMAIN[6]: '### 正式成果必须保存当时采用的材料、判断与版本',
            DOMAIN[11]: '### 并发、幂等与恢复都服从 Domain Authority',
            DOMAIN[16]: '### 领域模型只保存未来仍有业务意义的关系',
            DOMAIN[21]: '### 人工判断、冲突证据和历史修正必须可追溯',
            DOMAIN[25]: '### 当前、目标与缺口',
        },
    )
    consolidate(
        'docs/modules/knowledge/README.md',
        KNOWLEDGE,
        {
            KNOWLEDGE[0]: '### 材料到达只是开始：任务是否可用需要独立判断',
            KNOWLEDGE[2]: '### 正式材料、可重建派生与任务就绪是三层事实',
            KNOWLEDGE[3]: '工程上继续保持 `KnowledgeGeneration lifecycle != task-level ReadinessDecision`，因为两者回答的是不同的问题。',
            KNOWLEDGE[5]: '### 检索只负责产生有来源的候选',
            KNOWLEDGE[7]: '### 路由与 GraphRAG 只在问题需要时增加',
            KNOWLEDGE[10]: '### KnowledgeGeneration 必须可构建、验证、切换和回收',
            KNOWLEDGE[17]: '### 质量、停止条件和复杂度由任务要求与 Eval 决定',
            KNOWLEDGE[23]: '### 失败隔离不能污染当前 Serving',
            KNOWLEDGE[25]: '### 当前、目标与缺口',
        },
    )

    counts = {
        'application': 7,
        'domain': 7,
        'knowledge': 8,
    }
    for name, count in counts.items():
        text = (ROOT / 'docs/modules' / name / 'README.md').read_text(encoding='utf-8')
        observed = sum(1 for line in text.splitlines() if line.startswith('### '))
        if observed != count:
            raise RuntimeError(f'{name}: expected {count} macro headings, got {observed}')


if __name__ == '__main__':
    main()
