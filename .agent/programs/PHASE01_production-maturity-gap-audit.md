# PHASE01 Production Maturity Gap Audit

status: active

## 目标

对四大总交付物和八类 runtime-first 交付物做生产成熟度差距审计，形成可执行的 owner map、验证矩阵、外部依赖矩阵和停止条件。

## 范围

- 读取 `docs/architecture/production-readiness.md`、`docs/architecture/architecture.md`、`.agent/references/code-map.md`、`.agent/references/verification-map.md`。
- 核对 Web / Desktop、API、Agent Runtime、Memory、Tool、Knowledge、Security、Trace / Eval、repo governance 的 Current 证据。
- 标明每个 Production Target 属于本地可实现、需要外部服务、需要用户凭据、需要 Future program 或需要停止决策。

## 禁止范围

- 不修改 runtime 行为。
- 不把 Target 写成 Current。
- 不删除 compatibility、vendor、legacy alias 或 provider path。

## 验收闸门

- 产出成熟度差距表，覆盖四大总交付物和八类 runtime-first 交付物。
- 产出 owner map，指向具体目录、测试和 verifier。
- 产出 PHASE02-PHASE12 的执行优先级和停止条件。
- 更新本 phase 状态和后续 phase 入口。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```
