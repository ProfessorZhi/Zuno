# Goal Mode Prompt

你现在在仓库 `F:\internship-work\resume&resume project\02_projects\Zuno` 中工作。

按“目标模式”推进，不按旧 phase 惯性推进。
所有任务目标、当前状态、迁移规则、phase、workflow，都先从下面文档读取，不要自己重造口径：

- `docs/architecture/current-architecture.md`
- `docs/architecture/target-architecture.md`
- `docs/architecture/transition-strategy.md`
- `docs/architecture/phases/README.md`
- `docs/architecture/specs/architecture-upgrade-2026-06.md`
- `docs/development/architecture-doc-maintenance-workflow.md`

当前 phase 体系只有这 6 个：

1. `Phase 1: Repo Skeleton`
2. `Phase 2: Service Migration`
3. `Phase 3: Runtime Workflow`
4. `Phase 4: GraphRAG + Domain Pack`
5. `Phase 5: Eval + Proof`
6. `Phase 6: Public Surface`

要求：

1. 先读文档，再判断当前任务属于哪个 phase，再执行。
2. 旧文档默认只作历史参考，当前真相以上述文档为准。
3. 允许开启多 agent，但只能在任务可并行拆分时使用；主 agent 负责统一收口。
4. 每轮都要简短汇报一次：
   - 当前目标
   - 已完成
   - 正在做
   - 下一步
   - 预估总进度：`XX%`
5. 任何结构、代码、文档改动后，都要做对应最小验证，不能只改不验。
6. 如果旧测试、旧文档、旧入口阻碍新目标推进，先说明冲突，再把它们改到当前目标口径，不要退回旧方案。
7. 保持输出简洁，少复述，把判断依据放回文档和验证结果上。
