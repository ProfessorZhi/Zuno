# 已知坑

- 不把 Target 文档、类名、目录存在或 Mock test 当作 Current/production proof。
- Product command 不允许通过 shadow、canary、rollback 或旧 route 绕过单一路径。
- 不用 synthetic tenant、默认用户、临时 SQLite 或异常吞掉来掩盖身份和持久化失败。
- 不把 Application & Integration 变成 Plan/Step/Retry/Replan/Tool owner。
- 不把 Codex/Claude 工程协作多线程写成产品 Multi-Agent runtime。
- 删除历史前先做精确 manifest；用户明确授权的 current-tree 压缩不等于远端历史重写。
- Windows workspace 操作先核对 `Get-Location`、`git rev-parse --show-toplevel` 和目标绝对路径。
- 长 prompt、JSON 和敏感参数放文件传递，避免嵌套 PowerShell 改写内容。

验证失败时先读失败输出和当前事实源，再修根因；不要删掉断言或恢复旧 facade。
