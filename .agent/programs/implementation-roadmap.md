# 等待态路线骨架

state: no-active

当前没有 active program。此文件只保留下一轮 program 打开前的等待态说明，不承载已完成 program 的执行细节。

## 打开新 Program 的规则

1. 明确 program 名称、目标、范围、禁止范围和验收。
2. 把新的 roadmap 和 `PHASE01_*.md` 起始 phase 文件放入 `.agent/programs/`。
3. 更新 `.agent/programs/current.md`、`.agent/programs/README.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md` 和 `AGENTS.md`。
4. 如果新 program 影响 docs / `.agent` / runtime / verifier / tests，同步更新 `.agent/system.yaml`、`.agent/references/verification-map.md` 和 repo tests。
5. 每次新 program 都从 `PHASE01` 开始编号。

## 最近完成归档

`zuno-eight-deliverables-full-realization-v1` 已完成并归档到：

- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`

归档内保存原始 roadmap、closure checklist 和 PHASE01-PHASE10 文件。
