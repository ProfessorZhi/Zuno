# Debugging

## 最短路径

1. 先确认 `git status --short --branch`、当前 commit 和运行配置。
2. 按 `docs/architecture/architecture.md` 识别 owner，再按 `code-map.md` 找入口。
3. 先复现最小失败，再沿 Application & Integration → Agent Runtime & Control →
   Tool Runtime & Effects → Security & Governance → Platform 的调用链定位；不要从异常处添加兼容分支。
4. 对失败分类：身份/授权、幂等/并发、持久化/恢复、模型/工具、投影/交付。
5. 修复后运行对应模块测试、repo verifier 和 `git diff --check`。

## 禁止的调试修复

- 不用 synthetic tenant、默认用户、临时 SQLite 或 shadow/rollback 分支掩盖失败。
- 不把异常吞掉后返回成功，不在 API 层直接读写 owner 数据库。
- 不保留旧 facade 作为“临时”路径；需要迁移时直接迁移调用方并删除旧入口。
