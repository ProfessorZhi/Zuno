# Program Roadmap

## 当前状态

当前没有 active program。

每次新 program 都从 `PHASE01` 开始编号；已完成 program 必须归档到 `docs/history/programs/`，并从 `.agent/programs/` 前台移除 `PHASE*.md` 文件。

`zuno-six-layer-internalization-v1` 已完成并归档；它在 Program 3 已经完成 root / alias surface closure 的基础上，让 `api / agent / memory / capability / knowledge / platform` 六层内部拥有了第一批清晰、可测试、无副作用的目标层入口。

## 总边界

允许：

- 增加薄 facade、contracts、policy、selector、retrieval、rendering、trace 等目标层入口。
- 保留旧 public import path，并证明新旧入口对象一致。
- 修正文档中 Current / Target 混淆。
- 增加 focused tests 和 verifier guard。

禁止：

- 改 API response shape。
- 改 DB schema。
- 改 frontend。
- 改 eval baseline。
- 重写 GeneralAgent 主循环。
- 删除 `zuno.services.*`、`zuno.core.*`、`zuno.database.*` 等旧 public import path。
- 把未完成的 production runtime 能力写成 Current。

## 已完成 Program

- `zuno-six-layer-internalization-v1`：完成六层内部第一批 thin surfaces、README 边界、focused tests、repo verifier 和 Agent verifier 收口。
- `zuno-repo-layout-cleanup-v1`：完成 Program 3 root / alias surface closure。

## 最近完成历史

Program 4 已完成并归档：

- `docs/history/programs/zuno-six-layer-internalization-v1/`

Program 3 已完成并归档：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 完成态中，`src/backend/zuno` 根目录只允许：

```text
__init__.py
main.py
api/
agent/
memory/
capability/
knowledge/
platform/
```

旧 import path 必须继续可用，并由 `platform/compatibility/legacy_aliases.py` 或后续明确 compatibility 机制保护。

## Queued / Not Active

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`：target blueprint 已刷新；`overview.html` / Mermaid 生成展示仍可作为后续 follow-up。
