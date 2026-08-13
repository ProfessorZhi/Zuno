# 旧路径引用审计

状态：`COMPLETE`

## 基线观察

基线存在以下 active-route 风险：

- `docs/project/facts/` 被 `docs/README.md`、`docs/project/README.md`、`.agent/system.yaml` 和多个 verifier 当作正式入口。
- `docs/project/product/` 至 `deployment/` 被总体架构、渲染器、写作/可读性 verifier 和测试当作 Canonical Taxonomy。
- `docs/project/modules/` 被旧 Target verifier/test 直接读取。
- `docs/status/production-readiness.md` 被当前状态和旧模块文档大量引用。

## 迁移后的审计要求

1. Active docs、`.agent` 路由、入口 verifier 和默认 docs tests 只能路由到新入口。
2. `docs/history/superseded-document-taxonomy/` 内的旧路径文本可以保留，但必须通过归档 README 明确其历史性质。
3. 旧 verifier 若仍需保留，只能作为历史材料 verifier，不能被入口治理宣称为当前 Canonical verifier。
4. 内部 Markdown link verifier 必须对迁移后的 tracked 文件重新运行，不能依赖旧路径存在。

## 收口状态

本文件在迁移完成后补充：active path 残留、归档 path 残留、broken link 和 verifier 处置结果。

## 收口结果

- Active docs、`.agent` 路由和当前入口 verifier 已改走 `docs/project/history/`、`docs/project/status/`、`docs/project/architecture/`、`docs/evidence/`。
- `docs/project/facts/`、`docs/project/modules/` 和旧专题目录已不存在；旧原稿保留在 `docs/history/superseded-document-taxonomy/`。
- 归档原稿中的旧路径文本保留为历史证据，不参与当前 Canonical link 检查；归档 README 明确其 Superseded 性质。
- 旧模块专项 verifier/test 已改为只读验证归档原稿；它们不再恢复旧活动目录或成为当前架构入口。
- `verify_markdown_internal_links.py`、架构/入口/边界/结构 verifier 已通过。
- `tests/repo` 受影响迁移与历史回放子集通过；完整 `tests/repo` 仍有既有 Fleet/WorkProduct/ledger/UTF-8/运行时基线失败，详见本轮最终报告。
