# 工程工作流

## Source of truth

```text
AGENTS.md                 仓库边界、入口、停止条件
.agent/system.yaml        机器可读路由
.agent/references/        当前 Agent 工作规则
.agent/programs/          active / queued 执行状态
docs/                     正式人类事实
```

`.agent/` 不保存架构或模块正文镜像；`docs/history/` 只保存批准的历史摘要。

## 修改流程

1. `git status --short --branch`，确认 `main`、HEAD 和 origin/main。
2. 读取对应架构、模块 Target、`code-map.md` 和 `task-routing.md`。
3. 先写清 owner、contract、失败语义和删除边界。
4. 先实现 canonical path，再迁移 API、前端、worker、测试和工具调用方。
5. 删除旧 facade、旧 route、旧施工 verifier 和不再有 caller 的 shim。
6. 运行 focused tests、module verifiers、repo gates。
7. `git diff --check`，检查 docs Current/Target/History，commit + push。

## 代码规则

- Product Surface 负责 northbound API、command、projection、delivery。
- Agent Runtime 负责 Controller/Coordinator；是否启用 Multi-Agent 由 Target policy 和 Eval 决定，不把工程协作多线程写成产品事实。
- Tool effect 必须经过 Security、Approval、Budget、Idempotency 和 audit。
- API、前端、worker 不直接访问 provider 或数据库 owner。
- 失败必须保留 blocked/refused/recovery 事实，不用 fallback 把失败改成成功。

## 清理规则

- 未提交内容、未进入 main 的 commit、Migration、用户文件、benchmark evidence 和 thread prompt，未证明可丢弃前默认保留。
- 已获得明确授权的历史压缩只能删除当前树副本；远端 Git history 仍作为考古恢复源。
- 删除前用精确 manifest，确认路径位于仓库范围；删除后报告数量和保留入口。
- 不以 worktree、branch、stash 数量或磁盘占用作为删除理由。

## 收尾闸门

```text
main == origin/main
main worktree clean
repo structure / docs entrypoints / doc boundaries PASS
git diff --check PASS
旧 Program1 SUPERSEDED / RETIRED
active implementation program NONE
```
