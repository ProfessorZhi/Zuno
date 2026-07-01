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

## 需要先读取

- `docs/architecture/production-readiness.md`
- `docs/architecture/architecture.md`
- `docs/architecture/repo-ownership-matrix.md`
- `.agent/references/current-program.md`
- `.agent/references/code-map.md`
- `.agent/references/runtime-call-chain.md`
- `.agent/references/verification-map.md`
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/closure-summary.md`

## 需要修改的文件

- `.agent/programs/PHASE01_production-maturity-gap-audit.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- 如发现事实源漂移：`README.md`、`AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/production-readiness.md`
- 如新增机器检查：`tools/scripts/verify_repo_structure.py`、`.agent/scripts/verify_agent_system.py`、`tests/repo/test_agent_system.py`、`tests/repo/test_repo_structure_consistency.py`

## 执行拆解

1. 建立四大总交付物审计表：Current 证据、Production Target、owner、测试入口、blocked 条件。
2. 建立八类 runtime-first 交付物审计表：产品闭环、解析索引、Agent Runtime、Memory、Tool/Sandbox、Knowledge/GraphRAG、Security/Eval、治理一致性。
3. 对每个 Production Target 标记执行类型：本地可实现、需要外部 adapter、需要真实服务、需要凭据、需要用户决策、应留作 Future。
4. 为 PHASE02-PHASE12 补执行优先级：先事实源和 governance，再 repo ownership，再 runtime productionization，最后 release closure。
5. 对每个 phase 列出最小可关闭证据，禁止只用 README 或 schema 关闭。

## 多 agent 分工

- Thread A：审计 docs / `.agent` / verifier / tests 的事实源一致性。
- Thread B：审计 `src/backend/zuno` 六层 owner、compatibility、vendor、legacy alias。
- Thread C：审计产品闭环、Desktop、API、artifact、trace、feedback。
- Thread D：审计 parse/index/GraphRAG/Memory/Tool/Security/Eval 的 production target。
- 主线程：合并差距表，决定后续 phase 顺序和停止条件。

## 需要返回的证据

- 四大总交付物 maturity gap 表。
- 八类 runtime-first delivery gap 表。
- owner map：每项指向目录、测试、verifier 和文档事实源。
- external dependency matrix：哪些需要真实服务、凭据或基础设施。
- PHASE02-PHASE12 执行风险排序。

## 停止条件

- Current / Target 边界冲突，无法判断某能力是否已由代码和测试证明。
- 发现需要删除 public API、数据库 schema 或兼容路径才能继续。
- 发现生产级目标需要真实外部凭据且无法用 adapter / local fallback 表达。
