# Goal03 Wave A Product Agent Assets Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE09 的 Product-owned Agent 产品资产最小持久化纵切：

- `AgentDraft`、`AgentPublication`、`AgentInstallation`、`AgentCatalogEntry` 拥有独立 PostgreSQL 表。
- Publication / Installation / Catalog 只接受 `PUBLISHED` 的 `AgentVersion`。
- Catalog 查询返回 Product-owned authorized catalog read model，不把 Agent Core Run 当作产品资产。
- RuntimeRequest 仍绑定一个 `active_agent_version_id`，Product 不创建 AgentRun。

## Migration

```text
revision: 20260726_38
down_revision: 20260725_37
```

新增表：

```text
product_agent_drafts
product_agent_publications
product_agent_installations
product_agent_catalog_entries
```

## 代码证据

- `infra/db/alembic/versions/20260726_38_goal03_product_agent_publication_installation.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `tests/repo/test_goal03_wave_a_migration_contract.py`
- `tests/integration/test_goal03_wave_a_persistence.py`

## 验证

```powershell
alembic -c infra/db/alembic.ini upgrade head
```

结果：

```text
Running upgrade 20260725_37 -> 20260726_38
```

```powershell
python -m pytest -q tests/repo/test_goal03_wave_a_migration_contract.py tests/integration/test_goal03_wave_a_persistence.py tests/api/test_goal03_product_route.py -p no:cacheprovider
```

结果：

```text
14 passed
```

## 边界

本证据证明 Product Agent Draft / Publication / Installation / Catalog 已有 additive schema、repository methods 和 PostgreSQL integration proof。

本证据不单独证明完整 PHASE09 completed；完整旧 API cutover、E2E client reconnect/cutover 和全 UI contract 仍需 Closure Gate 汇总证明。
