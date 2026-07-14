# Codex GPT-5.5 Medium 执行手册

program: zuno-canonical-architecture-runtime-realization-v1
model_profile: GPT-5.5 medium
principle: 降低推理负担，不降低架构能力

## 1. 每次只做一个 Work Package

执行原则：一次只执行一个 Work Package。

不要一次读取 22 个 Phase，也不要尝试实现整个模块。Coordinator 给出 `Pxx-Tyy` 后，只读取：

1. `AGENTS.md`。
2. `.agent/programs/current.md`。
3. `.agent/programs/task-execution-contract.md`。
4. 当前 `PHASENN_*.md`。
5. 该任务列出的 Minimal Read Set。
6. 该任务列出的 Current Anchors。

除非任务要求，不读取其他模块全文，不重新设计架构。

## 2. 推荐启动提示词

```text
执行 Zuno active Program 中的 <TASK_ID>。
严格读取并遵守：
- AGENTS.md
- .agent/programs/current.md
- .agent/programs/task-execution-contract.md
- <PHASE_FILE>
只执行 <TASK_ID>，不得扩展到相邻任务。
先输出 Current/Gap/Plan，确认最新 main 与任务描述一致后再编码。
使用独立 worktree 和 codex/<task-id>-<slug> 分支。
完成真实代码、Migration、测试、证据、Commit 和 Push。
遇到 Stop Condition 立即停止，不自行修改架构。
```

## 3. 节省 Token 的正确方式

允许：

- 先打开任务列出的 3–8 个文件。
- 使用 `rg` 精确搜索类名、路由、表名、Feature Flag 和调用点。
- 只总结会影响当前任务的 Current 事实。
- 使用已有 Contract、状态表和测试模板，不重新解释架构。
- 运行 Focused Test 后再决定是否扩大搜索。
- 把复杂问题拆成 Expand/Migrate/Verify/Contract 四个提交步骤。

禁止：

- 因 Token 少而省略 Failure、Recovery、Idempotency、安全或测试。
- 用 Mock 替代任务要求的真实 Adapter/Integration。
- 把多个 Owner 合并到一个“通用 Service”。
- 读取旧 History 后以旧设计覆盖新模块。
- 猜测当前代码；必须搜索并引用路径。
- 为了减少代码删除状态、Receipt、Attempt、Version 或 Gate。

## 4. 固定思考模板

编码前只回答：

```text
Current：现在真实执行到哪里？
Gap：与任务 Target 差哪几个可验证点？
Owner：哪些事实由谁拥有？
State：允许和禁止哪些状态转换？
Failure：失败由谁 Retry、Reconcile、Recover？
Migration：怎样 Expand、Migrate、Verify、Contract？
Tests：什么测试能证明，不是“看起来实现了”？
```

不要写长篇架构复述。

## 5. Diff 控制

- 一个 Work Package 建议 1–4 个逻辑 Commit。
- 超过任务 Allowed Paths，立即停止。
- 预计修改超过 25 个 Runtime 文件时，先给 Coordinator 提交拆分建议。
- 公开 API、数据库不可逆变更、依赖升级和安全边界变化必须停止确认。
- 前端与后端 Contract 同一任务修改时，必须同时增加契约测试。

## 6. 测试顺序

```text
最小 Unit/Contract
→ Focused Integration
→ Fault/Recovery
→ Vertical Slice/E2E
→ Repo Governance
```

先跑最小失败测试，修复后再扩大，避免每次全仓测试浪费时间。Phase Closure 由 Coordinator 运行完整集成验证。

## 7. 完成报告

严格使用 `task-execution-contract.md` 的模板，至少写出：

- 起始和最终 Commit。
- 实际修改文件。
- Migration Revision。
- 实现的状态转换和 Failure 语义。
- 运行命令与结果。
- 未运行命令及原因。
- 正常、失败、恢复证据。
- 新增 Current 和仍为 Target 的边界。

不要写“应该可用”“理论支持”“基本完成”。

## 8. Coordinator 给 Codex 的最小上下文包

每次只发送：

```text
TASK_ID
PHASE_FILE
当前 main SHA
Allowed Paths
Stop Conditions
必要环境变量/服务
```

其余规则由仓库内 Program 文件提供。这能节省重复提示 Token，同时保持完整架构约束。
