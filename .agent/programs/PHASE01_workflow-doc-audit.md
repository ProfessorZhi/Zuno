# PHASE01：工作流与文档系统只读审计

## 目标

在不改文件的前提下，审计当前 `AGENTS.md`、`.agent/`、`docs/`、`tools/scripts` 和 `tests/repo` 是否能组成自洽的本地 Agent 工作流。

## 范围

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/**`
- `.agent/templates/**`
- `.agent/programs/**`
- `docs/architecture/**`
- `tools/scripts/**`
- `tests/repo/**`

## 可并行线程

- Thread A：`AGENTS.md`、`.agent/README.md`、`.agent/system.yaml` 入口和路由审计。
- Thread B：`.agent/references`、`.agent/templates` skill / template 边界审计。
- Thread C：docs entrypoints、verifiers、repo tests 防漂移能力审计。

## 不做

- 不修改文件。
- 不运行 runtime tests。
- 不移动目录。
- 不归档旧计划。

## 验收

- 输出一张问题表：问题、证据文件、影响、建议 phase。
- 区分“必须修”和“可以后续优化”。
- 明确 Program 1 后续 phase 是否需要调整。

## 验证

只读审计不提交。可以运行：

```powershell
git status --short --branch
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_docs_entrypoints.py
```

## 主线程合并结果

PHASE01 已按多线程模式完成三路只读审计：

| 线程 | 分支 | 范围 | 结论 |
| --- | --- | --- | --- |
| Thread A | `codex/program1-phase01-thread-a-entry-routing` | `AGENTS.md`、`.agent/README.md`、`.agent/system.yaml`、路由和 current program | 入口和路由骨架成立，但 PHASE02 需要收口 bootloader 阅读顺序、`system.yaml` docs_sync、工作模式措辞重复。 |
| Thread B | `codex/program1-phase01-thread-b-skill-programs` | `.agent/references/**`、`.agent/templates/**`、`.agent/programs/**`、queued programs | Skill / Template / Program 边界基本成立，但 PHASE03 需要清理模板中的项目事实、规范 references skill 结构，并给 queued program 自带 not active 标识。 |
| Thread C | `codex/program1-phase01-thread-c-docs-verifiers` | `docs/architecture/**`、`.agent/scripts/**`、`tools/scripts/**`、`tests/repo/**` | docs 和 verifier/test 当前闸门全绿，但 PHASE04 需要把 queued program 不误执行从短语检查升级为更直接的负向语义检查。 |

### 合并问题表

| 严重级别 | 问题 | 证据来源 | 影响 | 建议 phase |
| --- | --- | --- | --- | --- |
| 高 | `.agent/templates/goal-mode-prompt.md` 混入旧本地路径、旧 history/program 和 Phase 0-6 事实，不是纯提示词骨架。 | Thread B | 模板会变成第二套项目真相，后续线程可能被旧路径或旧 program 牵引。 | PHASE03 |
| 中 | `AGENTS.md` 的必读顺序对工作流任务过宽，容易削弱 bootloader “先路由、再按任务读”的定位。 | Thread A | 线程可能固定读取完整架构链，路径变长并重复 `task-routing.md` 的职责。 | PHASE02 |
| 中 | `.agent/system.yaml` 的 docs_sync 未显式覆盖 `.agent/programs/current.md` 和 `.agent/programs/implementation-roadmap.md`。 | Thread A | 修改 `.agent/**` 时可能漏同步 active program 状态面。 | PHASE02 |
| 中 | `.agent/references` 边界声明清楚，但部分文件仍是状态、命令目录或地图，不完全符合 skill / lesson / playbook 结构。 | Thread B | PHASE03 的 “每个 skill 文件能回答何时使用、读哪些文件、禁止什么、跑哪些验证” 验收无法完全落地。 | PHASE03 |
| 中 | 单个 queued program roadmap / phase 文件缺少明显 queued draft / not active 横幅。 | Thread B | 孤立打开 future program 文件时，仍可能被误当 active phase 执行。 | PHASE03；PHASE04 加 verifier |
| 中 | queued program “不能被 active current 当成正在执行” 目前主要靠目录形状和短语间接约束。 | Thread C | 防漂移能力还不够语义化；需要 verifier/test 做负向检查。 | PHASE04 |
| 低 | 工作模式说明在 `AGENTS.md`、`.agent/README.md`、`workflow.md`、`system.yaml` 多处重复。 | Thread A | 当前一致，但后续改一处漏一处会造成漂移。 | PHASE03/PHASE04 |

### 主线程决策

- 进入 PHASE02：先修 bootloader / routing / docs_sync / 常驻线程工作流表述。
- 进入 PHASE03：再修 template 与 references 边界，给 queued program 加 not active 标识。
- 进入 PHASE04：最后把 queued program 不误执行和常驻线程隔离边界写成 verifier/test。
- PHASE01 不改 runtime、不改 API、不移动目录；本阶段只合并审计结论和工作流规则。
