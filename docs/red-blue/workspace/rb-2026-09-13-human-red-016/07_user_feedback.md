# User Feedback — rb-2026-09-13-human-red-016

## UF-001 — Stop at first Red output

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: ROUND_INIT / RED_QUESTIONS / USER_RED_REVIEW
text: 本轮只运行到新版 Red 第一轮产出并交给用户检查；用户未 APPROVE 前禁止进入 Blue。

## UF-002 — Previous Red model was rejected

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: RED_QUESTIONS
text: Round #015 的 30 条 Primary 虽然技术上合理，但不够人味，像工程 / 架构 checklist 改写成复合问句。不得复用这种现场脚本结构。

## UF-003 — Human interviewer behavior is the calibration target

when: 2026-09-13T22:14:00+08:00
priority: highest
affected_stage: RED_QUESTIONS / USER_RED_REVIEW
text: 新 Red 必须像真实面试官：先让候选人自己暴露主线；问题简短、一次一个主要意图；下一问根据上一答里的关键词、数字、选择、困难、Ownership 或 bad case 动态生成；有价值的 thread 可以连续追，信息增益下降时自然换题。100 问只作为离线 Pressure Suite。
review_focus:
- SPOKEN_SEEDS 是否自然
- BRANCH_EXAMPLES 是否真的由上一答驱动
- 是否仍有 Reviewer checklist 味
- 是否有无信息增益的原子化追问
- 是否把 Controller rubric / Kill Switch 暴露成口头问题

## UF-004 — Direction approved; deepen like ByteDance interviews

when: 2026-09-14T00:50:00+08:00
priority: highest
affected_stage: USER_RED_REVIEW / RED_REVISION / RED_SKILL
text: 当前 answer-driven 方向是对的。继续把 Red 思维框架沉淀得更人话；问题可以深入，参考字节 AI / 大模型 / Agent 面经的连续深挖方式。深度不能靠把多个审查项塞进一个长问题，而应来自同一 thread 连续 3–5 层追问，逐步进入实现、参数、指标、异常、底层原理或真实代码。
required_behavior:
- 保留自然短 Seed 与单意图 spoken question
- 同一高价值 thread 允许连续追 3–5 层，必要时更深
- 深挖必须依赖上一答，不按预写清单机械走
- 可以追具体工程实现、参数、数据结构、状态持久化、并发、超时、评测集、指标定义、代码与真实 bad case
- 面试官可以直接说“具体一点”“这个怎么实现的”“为什么不用 X”“这个数怎么来的”，但不要每题都套模板
- 字节式基础题 / 算法题可以在项目深挖后自然切入，不要求每题都伪装成项目问题
- Blue 仍保持 BLOCKED，修改后的 Red plan 重新交给用户检查

## UF-005 — Simulated resume itself is not recruiter-readable

when: 2026-09-14T01:20:00+08:00
priority: highest
affected_stage: SIMULATED_RESUME / WORKFLOW
text: 当前模拟简历不说人话。需要对照用户本人真实简历和公开优秀 AI / Agent 简历的字数、句长、版式与信息密度重新校准。模拟简历必须先像真实求职材料，再作为 Red 的攻击接口。
findings:
- 用户真实简历采用一页、项目简介一行、技术栈一行、短 bullet 的标准招聘阅读节奏
- 当前模拟简历 4 条 bullet 平均长度约为用户真实 Zuno bullet 的 5 倍，整体更像 Evidence / provenance 摘要
- 用户真实简历自身也偏满：Zuno 8 条、Astrid 10 条、技能 7 条，后续应取其句长与语感，而不是照搬 bullet 数量
required_behavior:
- 校准 Round 增加 USER_RESUME_REVIEW，在用户批准模拟简历前禁止 Red
- 模拟项目默认 4–5 条核心 bullet，一条只讲一个主要贡献
- 用范围限定词自然表达 small-sample / Pilot / participation 边界，不写 Reviewer 式免责声明
- 若冻结简历正文改变，旧 Red plan 自动失效
resolution: Round #016 的 Red behavior 校准有效，但该 Round 的 resume attack surface 判定无效；不得继续 Blue，应由新 Round 用新 Resume Builder 重建攻击面
