# PHASE04：小步边界清理
> 状态：queued draft / not active。不要直接执行本文；打开该 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

## 目标

只做低风险边界清理：import facade、历史命名、生成物忽略、过时 docs 前台移除。

## 验收

旧 import 不破坏，runtime 行为不变，repo hygiene tests 通过。
