# PHASE02：根目录与 Docs Hygiene
> 状态：本线程完成文档/模板收口，等待主线程合并后统一更新 `.agent/programs/current.md`。

## 目标

清理根目录和 docs 前台，把历史、生成物、临时文件、旧入口归位。

根目录目标是少而稳定：只保留必要项目入口、一等目录和 package/config 文件。对 `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 等先确认 tracked 状态、用途和 `.gitignore`，再决定移动、归档、忽略或删除。

`docs/` 前台只承载正式真相；历史材料、旧计划、旧审计和生成报告进入 `docs/history/` 或被 `.gitignore` 排除。

## PHASE01 输入

- Thread A 确认根目录当前没有 `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、`data/` 实体，也没有 tracked 脏目录。
- `reports/` 和 `data/` 不能盲删或整目录粗暴忽略，需要白名单语义：正式证据进 `docs/evidence/`，示例输入进 `examples/` 或 `tools/evals/`，运行生成物保持 local/ignored。
- `docs/architecture/README.md` 和 `docs/architecture/target-architecture.md` 需要判断是否承载了过细的 active phase / queued program 执行状态。
- `.agent/templates/goal-mode-prompt.md` 需要瘦身为模板骨架，不保存固定路径或历史 program 事实。

## 本 phase 决策

1. `docs/architecture/README.md` 只作为架构入口和正式文档导航，不再重复维护 active phase、queued program 顺序或具体执行状态。
2. `docs/architecture/target-architecture.md` 只写目标架构、设计边界、非近期目标和与 Current 的硬边界；执行 program 状态迁到 `docs/architecture/roadmap.md` 和 `.agent/programs/`。
3. `docs/architecture/roadmap.md` 作为正式人类状态入口，简洁说明 Program 3 active、Program 4/5 queued，并明确 queued 不等于 active。
4. `.agent/templates/goal-mode-prompt.md` 只保留可复制执行骨架和变量占位，不保存固定绝对路径、历史 program 事实、旧 phase 事实或项目结论。
5. `data/` / `reports/` 使用白名单语义，不做根级整体忽略，也不把运行输出提交到前台。

## `data/` / `reports/` 白名单语义

```text
path | 可 tracked 内容 | 默认不可 tracked 内容 | 目标位置
docs/evidence/ | 正式证据、可复核结论、公开 demo 证据 | 临时运行日志、未整理生成报告 | 正式证据入口
examples/ | 可读、可复用、体积受控的示例输入 | 下载原始数据、运行输出、缓存 | 示例输入
tools/evals/ | eval 工具、样例数据、说明文档 | 大体积 raw/normalized/corpus/ingested 数据 | eval 源码和小样例
data/ | 仅在明确白名单后保留小型示例或索引 | raw downloads、normalized/corpus/ingested、zip/json/jsonl 运行数据 | 默认 local/ignored
reports/ | 仅在明确提升为正式证据后迁入 docs/evidence | runtime reports、临时 smoke 结果、real_runtime 输出 | 默认 local/ignored
```

现有 `.gitignore` 已忽略 multihop eval 的 raw / normalized / corpus / ingested 数据和 real runtime reports。PHASE05 负责把这条白名单语义机器化到 verifier / tests。

## 验收

- 根目录职责清楚，`data/` / `reports/` 的 tracked 边界有正式说明。
- `docs/architecture/README.md` 不再承载过细 active phase / queued program 执行状态。
- `docs/architecture/target-architecture.md` 不再承担执行 program 入口。
- `docs/architecture/roadmap.md` 是正式人类状态入口，queued program 不被写成 active。
- `.agent/templates/goal-mode-prompt.md` 是模板骨架，不保存固定路径或历史事实。
