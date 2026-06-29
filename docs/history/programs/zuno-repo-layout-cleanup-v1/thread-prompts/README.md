# Thread Prompts

> 状态：active。当前保存 Program3 目录收口目标模式提示词。

本目录只在多线程模式启用时保存当前 active program 的子线程目标模式提示词。

当前 active 目标模式提示词：

- `PROGRAM3_DIRECTORY_CLOSURE_TARGET_MODE_PROMPT.md`

## 使用规则

- 主线程先盘点可复用 Codex 线程和 git worktree，再生成或投递线程提示词。
- 主线程不能在主对话里直接粘贴完整子线程提示词；主对话只报告线程盘点结果、提示词文件路径和下一步动作。
- 主线程确认本地 `main` 已包含这些提示词，再创建或复用 Codex worktree 线程。
- 每个子线程必须运行在独立 worktree 和独立 `codex/` 分支上。
- 每个子线程必须是真正的 Codex UI 目标模式；提示词里写“目标模式”不等于 UI 目标模式。
- 每个子线程默认允许开启多 agent 模式，但多个 agent 不得同时编辑同一文件。
- 下一轮提示词更新时，默认替换或清理本目录旧提示词；只有用户明确要求归档时才移动到 `docs/history/programs/`。

## 当前线程

主线程目标模式：

- `PROGRAM3_DIRECTORY_CLOSURE_TARGET_MODE_PROMPT.md`：在主线程目标模式内一次性执行 Program3 PHASE01-06，默认开启多 agent 模式；不是多线程/子线程提示词。

## 本轮线程盘点

- 已归档上一轮 Program3 Thread A/B/C/D/E。
- 已移除 D/E worktree，并删除本地非 `main` 分支。
- 决策：用户要求提供主线程一次性做完 PHASE01-06 的目标模式提示词，默认开启主线程内多 agent 模式，不使用多线程 coordinator。
