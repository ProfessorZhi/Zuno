# PHASE04：小步边界清理
> 状态：pending。等待 PHASE01-03 收口后执行。

## 目标

只做低风险边界清理：import facade、历史命名、生成物忽略、过时 docs 前台移除。

可执行范围只来自 PHASE01/03 的审计结果。允许做小步、低风险、可回滚的清理，例如：

- 为目标六层补充 facade / re-export。
- 移除或归档已经确认无引用的前台历史材料。
- 把本地产物和生成物加入 `.gitignore` 或移动到正确位置。
- 给低风险目录增加 README / AGENTS 边界说明。

禁止在本 phase 做跨层大搬家、runtime 行为变更、public API 变更或数据库 schema 变更。

## 验收

旧 import 不破坏，runtime 行为不变，repo hygiene tests 通过。
