from pathlib import Path


def read(path):
    return Path(path).read_text(encoding='utf-8')


def write(path, text):
    Path(path).write_text(text, encoding='utf-8')


def replace_once(path, old, new):
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly 1 match, got {count}: {old[:100]!r}')
    write(path, text.replace(old, new, 1))


def replace_range(path, start_marker, end_marker, replacement):
    text = read(path)
    s = text.find(start_marker)
    if s < 0:
        raise SystemExit(f'{path}: start marker not found: {start_marker!r}')
    e = text.find(end_marker, s)
    if e < 0:
        raise SystemExit(f'{path}: end marker not found: {end_marker!r}')
    if text.find(start_marker, s + 1) >= 0:
        raise SystemExit(f'{path}: start marker not unique: {start_marker!r}')
    write(path, text[:s] + replacement + '\n\n' + text[e:])


replace_range(
    'docs/README.md',
    '## 推荐阅读顺序',
    '`docs/project/README.md` 只是导航。',
    '''## 推荐阅读路径

第一次理解 Zuno，不建议把整个 `docs/` 当成一条必须从 1 读到 10 的流水线。更好的方式是先拿到最短的项目 / 架构主线，再按目的进入研究、工程精度或维护材料。

### 核心路径：先建立 Zuno 的 mental model

1. [Project 主文档](./project/project.md)：先理解项目从哪里来、为什么普通 RAG / Generic Host 不足以覆盖全部目标，以及 Zuno 应该长期 Own 什么；如果暂时不关心历史与个人 Ownership，读到“完整 Zuno 什么时候不值得使用”以后即可先进入总体架构。
2. [总体架构](./architecture/architecture.md)：第一次只抓 Part A 的主故事。1–18 节已经完成从 baseline、Authority、恢复、安全到复杂度淘汰的核心推导；19 节以后属于横向 Stress Tests，可以二刷。
3. [模块架构](./modules/README.md)：先读三条任务路径、九个责任域和 Part A / B / C 的阅读方法；随后只选择与你当前问题最相关的一个或两个 Module Part A，不要求顺序读完九篇。
4. [Current Evidence](./evidence/README.md)：最后回到代码、Migration、Test、Trace、Eval 和运行证据，检查刚才理解的 Target 到底哪些已经 Current。

这条路径的目标不是“读完所有文档”，而是让第一次进入仓库的人尽快回答四个问题：Zuno 为什么存在、为什么不能只看通用平台 Feature List、哪些事实必须由谁负责、今天真正实现和证明到了哪里。

### 研究 / 架构深挖

当你要追问“这些能力从哪里来、为什么不用 WorkBuddy / Dify / Coze / LangGraph 直接承载、某个边界为什么被正式接受”时，再进入 [Research Knowledge Base](./research/README.md)、[有效 ADR](./decisions/README.md) 和对应 Module 的 Part B / Part C / B14.1–B14.8。`research/` 是解释和挑战架构的上游材料，不是第一次阅读必须经过的中转站。

### 维护 / 审查路径

当目标变成修改文档、审查架构、运行 Red / Blue 或维护仓库时，优先读 [Governance](./governance/)、[Current Evidence](./evidence/README.md) 和 [Maintenance](./maintenance/README.md)；需要 Interview Harness 时再进入 [Red / Blue Workflow](./maintenance/red-blue/README.md)。[术语表](./terminology.md) 用于跨文档消歧，不要求预先背诵。'''
)

replace_once(
    'docs/project/project.md',
    '''---\n\n**从这一节开始，叙事从“设计因果”切回“历史因果”。** 上面的边界解释今天为什么这样设计，不代表历史版本真的按同样顺序演进。下面只写能够由项目回忆、仓库、公开背景或 Evidence 支持的历史；恢复不了的地方保持 Unknown，不用 Target 反写过去。\n\n## 9. 项目是怎样发展到今天的''',
    '''---\n\n> **阅读分叉。** 如果你此刻只想理解“Zuno 为什么值得做、为什么不是普通 RAG、为什么这些责任需要存在”，到第 8 节已经拿到项目级设计主线，可以直接进入 [`architecture.md`](../architecture/architecture.md)。如果你需要准备项目经历、个人 Ownership，或者判断 Demo / Court-side Testing / Pilot / Current / Unknown 的证据边界，再继续下面的历史部分。\n\n**从这一节开始，叙事从“设计因果”切回“历史因果”。** 上面的边界解释今天为什么这样设计，不代表历史版本真的按同样顺序演进。下面只写能够由项目回忆、仓库、公开背景或 Evidence 支持的历史；恢复不了的地方保持 Unknown，不用 Target 反写过去。\n\n## 9. 项目是怎样发展到今天的'''
)

replace_once(
    'docs/architecture/architecture.md',
    '''**先抓住整篇的主线，而不是先记九个模块。** Zuno 的架构成长可以压缩成七步：从普通 RAG / Generic Host 出发；发现机器计算结果不能直接成为业务事实；把材料版本、知识派生和正式领域状态分开；让长任务拥有可恢复控制；让权限在长任务中持续生效；让现实副作用拥有独立 Effect truth；最后用 Evaluation 决定 GraphRAG、Memory、Reflection、Native Runtime 等复杂度是否值得保留。九个责任域只是这些矛盾最后稳定下来的 Ownership 边界。''',
    '''**先抓住整篇的主线，而不是先记九个模块。** Zuno 的架构成长可以压缩成七步：从普通 RAG / Generic Host 出发；发现机器计算结果不能直接成为业务事实；把材料版本、知识派生和正式领域状态分开；让长任务拥有可恢复控制；让权限在长任务中持续生效；让现实副作用拥有独立 Effect truth；最后用 Evaluation 决定 GraphRAG、Memory、Reflection、Native Runtime 等复杂度是否值得保留。九个责任域只是这些矛盾最后稳定下来的 Ownership 边界。\n\n> **第一次阅读可以把 1–18 节当成完整主故事。** 读到第 18 节，你应该已经能解释 baseline 为什么不够、Authority 为什么分开、一个关键 crash window 怎样恢复，以及复杂机制什么时候应该删除。19 节以后不再增加新的“第八阶段”，而是从时间、一致性、Non-proof、性能、Build / Buy、迁移等角度对同一组边界做横向 Stress Test；需要深入系统设计时再继续。'''
)

replace_once(
    'docs/architecture/architecture.md',
    '''09 的 Evaluation 因此不仅用于证明“功能有效”，还应该主动做 ablation 和 kill test，帮助团队决定哪些复杂度不值得长期维护。\n\n### 19. 架构真正困难的是“时间”，不是把模块框画出来''',
    '''09 的 Evaluation 因此不仅用于证明“功能有效”，还应该主动做 ablation 和 kill test，帮助团队决定哪些复杂度不值得长期维护。\n\n> **第一次阅读到这里可以先停。** 1–18 节已经完成 Zuno 的总体架构因果链；如果你的下一步是理解某个责任域，直接进入 [`docs/modules/`](../modules/README.md) 和对应 Module Part A 更有效。下面的内容属于第二遍阅读：它不再引入新的模块边界，而是用更苛刻的系统设计问题检查前面的边界在时间、故障、扩展、迁移和性能压力下是否仍然成立。\n\n### 19. 架构真正困难的是“时间”，不是把模块框画出来'''
)

replace_once(
    'docs/modules/README.md',
    '''如果一个对象名必须先读 Part B 才知道它为什么存在，Part A 应补概念解释；反过来，如果 Part A 开始连续枚举字段、enum 和 crash-window 表格，则应该下沉到 Part B。\n\n## 修改一个模块时，先定位事实，不要先画调用链''',
    '''如果一个对象名必须先读 Part B 才知道它为什么存在，Part A 应补概念解释；反过来，如果 Part A 开始连续枚举字段、enum 和 crash-window 表格，则应该下沉到 Part B。\n\n> **第一次阅读到这里可以停。** 你现在只需要能说清三条任务路径的复杂度差异、九个责任域分别保护什么，以及什么时候读 Part A / B / C。下一步应按问题选择一到两个 Module Part A，而不是继续顺序背下面的 Ownership 表、Completion Proof、Cancellation、Late Result 和 Recovery Reference。下面开始更偏向架构维护者和跨模块审查。\n\n## 修改一个模块时，先定位事实，不要先画调用链'''
)

replace_once(
    'docs/governance/architecture-narrative-quality-standard.md',
    '''一个简单判断是：只看相邻两到三节，读者当然能理解局部；但如果跳到文章中段，他仍然应该能回答“前面为什么把我带到这里，后面准备解决什么”。这属于篇章编辑，不应该通过标题数量或固定模板硬编码进 Validator。''',
    '''一个简单判断是：只看相邻两到三节，读者当然能理解局部；但如果跳到文章中段，他仍然应该能回答“前面为什么把我带到这里，后面准备解决什么”。这属于篇章编辑，不应该通过标题数量或固定模板硬编码进 Validator。\n\n长篇文档还必须允许读者知道**什么时候已经拿到核心故事，什么时候开始进入深挖**。Part A 很长没有问题，但“内容都重要”不等于“所有内容都必须成为第一次阅读的必经路径”。当主因果链已经闭环，后续如果转入横向 Stress Test、历史、Reference 或实现精度，应通过自然过渡、阅读分叉或 stop point 明确告诉读者。否则读者会把“我还没读完”误解成“我还没理解系统”。\n\n这同样只属于 Human Review：不要求每篇都有固定的“到这里可以停”句式，也不要求按章节号切割。真正的验收问题是：第一次进入文档的人能否在合理阅读量内形成正确 mental model，并知道下一步应该去哪个 Owner 文档继续，而不是被迫把整套 RFC 当成线性教材读完。'''
)
