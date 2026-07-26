# Goal03 Wave A PostgreSQL Integration Recovery Evidence

status: partial_integration_evidence
phase: PHASE09, PHASE12, PHASE14
commit_scope: Docker/PostgreSQL environment recovery and Goal03 persistence integration rerun

本文只证明当前本机环境已从 `localhost:5432` / Docker daemon 不可用状态恢复，并且 Goal03 Wave A 的真实 PostgreSQL persistence integration 已进入业务断言并通过。该证据不关闭 PHASE09、PHASE12 或 PHASE14，也不表示 Wave A Gate 已获 Coordinator Approval。

## 环境恢复

- `com.docker.service` 已从 stopped / start pending 恢复为 running。
- Docker Desktop Linux engine 已可连接。
- `zuno-postgres` 容器已运行并暴露 `0.0.0.0:5432->5432/tcp`。
- `zuno-rabbitmq` 与 `zuno-minio` 也已启动。

## 已运行验证

```powershell
docker version
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m pytest -q tests/integration/test_goal03_wave_b_persistence.py -p no:cacheprovider
python -m pytest -q tests/repo/test_goal03_wave_a_migration_contract.py tests/repo/test_product_surface_target_protocols.py -p no:cacheprovider
python -m pytest -q tests/api/test_goal03_product_route.py tests/frontend/test_product_wiring_v1_api_contract.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_package_a_delivery_settlement.py tests/capability/test_capability_runtime_batch.py -p no:cacheprovider
```

结果：

```text
Docker Desktop 4.69.0 / Engine 29.4.0 connected.
zuno-postgres Up healthy on localhost:5432.
3 passed
2 passed
15 passed
7 passed
51 passed
```

## 已证明

- `tests/integration/test_goal03_wave_a_persistence.py` 不再被 Alembic / PostgreSQL 连接阻塞，并通过 PHASE09、PHASE12、PHASE14 的当前 persistence assertions。
- Alembic head 与 Wave A migration contract 在真实 PostgreSQL 环境中可被测试夹具执行。
- 之前记录的 `localhost:5432` / Docker daemon unavailable 只保留为历史失败指纹，不再是当前环境事实。

## 未证明

- 本证据不证明 PHASE09 的 Projection/SSE/AvailableAction/Cutover 全部 mandatory tests 已完成。
- 本证据不证明 PHASE12 的真实外部 BM25/Vector/Graph adapter、ACL/Temporal/Conflict、rollback 和 deletion propagation 全部完成。
- 本证据不证明 PHASE14 的 Installation/Activation CAS、revocation propagation、supply-chain crash recovery、progressive loading budget 和 legacy registry full cutover 全部完成。
- `tests/integration/test_goal03_wave_b_persistence.py` 通过只说明当前 Wave B persistence baseline 可运行；PR B 仍必须按目标要求在 PR A 合并后从最新 `main` 启动。
