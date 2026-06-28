# 目标模式提示模板

> 复制后替换所有 `<...>` 占位符。本模板只保存执行骨架，不保存固定本地路径、历史 program 事实、旧 phase 事实或项目结论。

## 任务

```text
目标：<本轮目标>
工作目录：<repo 或 worktree 路径>
目标分支：<codex/...>
允许范围：<可修改路径或文件>
禁止范围：<禁止修改路径或文件>
验收闸门：<本轮必须满足的验收>
```

## 启动检查

先执行并报告：

```powershell
git fetch origin
git status --short --branch
git log --oneline origin/main..HEAD
```

如果有未提交改动、未解释的本地提交，或当前 worktree / branch 不符合本轮目标，停止并报告。

## 必读

- `AGENTS.md`
- `<本轮相关 docs / .agent / module AGENTS>`
- `<本轮相关 phase 或 program 文件>`
- `<本轮相关 verifier / test / code map>`

实现任务在读完相关文档后再读代码；不要只凭文档推断 runtime 行为。

## 规则

1. 目标不清楚时，先澄清会改变工作的关键决策。
2. 目标清楚时，用满足验收闸门的最短路径执行。
3. 每轮重新确认 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
4. 正式结论写入 `docs/`；只给 Agent 使用的导航、模板和执行辅助材料放入 `.agent/`。
5. 被替换计划移动到 `docs/history/`，不要直接删除。
6. 不把 Target 写成 Current，不把执行工作流里的多 agent 写成 Zuno runtime 架构。
7. 修改后运行本轮列出的最小有效验证。
8. 验证通过后提交并推送；如果验证或 push 阻塞，保留证据并停止报告。

## 验证

```powershell
<verification command 1>
<verification command 2>
<verification command 3>
```

## 收尾输出

- branch / commit / push 状态
- 修改文件列表
- 完成项
- 验证命令和结果
- 需要主线程决策的问题
