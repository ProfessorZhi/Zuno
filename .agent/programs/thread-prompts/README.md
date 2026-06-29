# Program 3 Thread Prompts

> 状态：active。这里保存当前多线程模式要投递到子线程的目标模式提示词。

这些提示词属于当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

## 使用规则

- 主线程先盘点可复用 Codex 线程和 git worktree，再生成或投递线程提示词。
- 主线程不能在主对话里直接粘贴完整子线程提示词；主对话只报告线程盘点结果、提示词文件路径和下一步动作。
- 主线程确认本地 `main` 已包含这些提示词，再创建或复用 Codex worktree 线程。
- 每个子线程必须运行在独立 worktree 和独立 `codex/` 分支上。
- 每个子线程必须是真正的 Codex UI 目标模式；提示词里写“目标模式”不等于 UI 目标模式。
- 每个子线程默认允许开启多 agent 模式，但多个 agent 不得同时编辑同一文件。
- 下一轮提示词更新时，默认替换或清理本目录旧提示词；只有用户明确要求归档时才移动到 `docs/history/programs/`。

## 当前线程

- `THREAD_A_fastapi-jwt-compat-prompt.md`
- `THREAD_B_backend-zuno-directory-cleanup-prompt.md`
- `THREAD_C_root-local-artifacts-cleanup-prompt.md`

## 本轮线程盘点

- `list_threads(query="Program3")`：没有可复用 Program3 子线程。
- `list_threads(query="Zuno")`：只有当前 Zuno 主线程处于 active，其它结果不是本轮 Program3 工位。
- 决策：本轮创建 3 个新的 Codex worktree 线程，每个线程绑定一个独立 `codex/` 分支。
