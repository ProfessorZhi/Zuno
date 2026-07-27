# Goal03 Wave A Gate Review

status: gate_blocked
phase: PHASE09, PHASE12, PHASE14
pr: goal03-repair/wave-a-product-knowledge-capability
head_at_review: 74dfbd3af9b9a257134e48b352f7801e6053e774

本文记录 2026-07-27 对 PR A 的当前 Gate 复核。结论只用于阻止误合并，不把任何 Phase 写成 completed。

## 当前已验证

- PR A 当前 head 为 `74dfbd3af9b9a257134e48b352f7801e6053e774`，GitHub `validate` 为 `SUCCESS`，merge state 为 `CLEAN`。
- Docker Desktop 与 `zuno-postgres` 已恢复，真实 PostgreSQL integration 不再被 `localhost:5432` 阻塞。
- 当前可用并 healthy 的容器依赖覆盖 PostgreSQL、RabbitMQ、MinIO、Elasticsearch、Neo4j、etcd；Milvus 镜像尚未完成拉取，Vector 外部索引服务无法启动。
- Alembic head 为 `20260726_40`。
- PHASE09 Product backend 当前 API / persistence / projection / action token / completion / workspace default runtime focused suites 通过。
- PHASE12 Knowledge 当前 local BM25 / vector / graph adapter dispatch、visibility receipt、durable Knowledge port、active snapshot unavailable fail-closed、cutover / rollback / deletion propagation focused suites 通过。
- PHASE14 Capability 当前 supply-chain guard、installation / activation CAS、revocation、ordered transition outbox、progressive loading budget、Agent Core / Workspace planner capability runtime port focused suites 通过。

## 当前运行命令

```powershell
python -m pytest -q tests/api/test_product_runtime_batch.py tests/repo/test_product_surface_target_protocols.py tests/api/test_goal03_product_route.py tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
python -m pytest -q tests/repo/test_goal03_wave_a_migration_contract.py tests/api/test_completion_unified_runtime.py tests/api/test_workspace_task_runtime.py -p no:cacheprovider
python tools/scripts/verify_product_surface_target_protocols.py
python -m pytest -q tests/knowledge/test_knowledge_runtime_batch.py tests/knowledge/test_index_jobs_runtime.py tests/knowledge/test_evidence_ledger.py tests/knowledge/test_corrective_retrieval_runtime.py tests/agent/test_knowledge_layer_surfaces.py tests/api/test_knowledge_api_contract.py tests/api/test_knowledge_reindex.py tests/agent/runtime/test_runtime_dependency_factory.py -p no:cacheprovider
python -m pytest -q tests/capability/test_capability_skill_layer.py tests/capability/test_capability_runtime_batch.py tests/api/test_goal03_capability_route.py tests/agent/runtime/test_runtime_state_contract.py::test_runtime_strategy_selection_uses_capability_runtime_port tests/agent/runtime/test_runtime_state_contract.py::test_runtime_strategy_selection_blocks_when_capability_runtime_fails tests/api/test_workspace_task_runtime.py::test_workspace_planner_uses_capability_runtime_port_for_plugins -p no:cacheprovider
python tools/scripts/verify_capability_skill_target_protocols.py
docker compose -f infra/docker/docker-compose.yml up -d elasticsearch neo4j etcd milvus
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.17.24
docker pull neo4j:5-community
docker pull quay.io/coreos/etcd:v3.5.5
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}"
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/knowledge/indexing tests/knowledge/test_index_jobs_runtime.py
docker compose -f infra/docker/docker-compose.yml up -d neo4j etcd
docker compose -f infra/docker/docker-compose.yml up -d elasticsearch
python -m pytest -q tests/integration/test_goal03_wave_a_external_index_adapters.py -p no:cacheprovider
python -m pytest -q tests/knowledge/test_index_jobs_runtime.py tests/agent/test_knowledge_layer_surfaces.py -p no:cacheprovider
docker pull milvusdb/milvus:v2.4.15
```

结果：

```text
37 passed, 1 warning
36 passed, 1 warning
Product Surface target architecture verification passed.
50 passed
16 passed, 1 warning
Capability / Skill target architecture verification passed.
Elasticsearch compose image resolution failed with Docker registry EOF.
Direct Elasticsearch image pull downloaded layers but stalled; the process was stopped and the image is not available.
Direct Neo4j and etcd image pulls downloaded layers but stalled; the processes were stopped and the images are not available.
Milvus was requested through compose, but no Milvus image or running service is available.
16 passed
compileall passed
zuno-neo4j healthy
zuno-etcd healthy
zuno-elasticsearch healthy
2 passed
20 passed
Milvus direct image pull stalled without progress; the process was stopped and the image is not available.
```

当前已确认运行的真实依赖：

```text
zuno-postgres: healthy
zuno-rabbitmq: healthy
zuno-minio: healthy
zuno-elasticsearch: healthy
zuno-neo4j: healthy
zuno-etcd: healthy
```

当前已确认缓存镜像：

```text
postgres:16
rabbitmq:3.13-management-alpine
minio/minio:RELEASE.2023-03-20T20-16-18Z
docker.elastic.co/elasticsearch/elasticsearch:7.17.24
neo4j:5-community
quay.io/coreos/etcd:v3.5.5
```

## Gate 结论

Wave A Gate 当前不能通过，PR A 当前不能合并。

最小 mandatory blocker：

```text
PHASE12 Milvus Vector external index adapter cutover is not implemented as Current.
```

根因：

- 原始目标要求 PHASE12 调用仓库配置的真实索引 Adapter，并覆盖 BM25、Vector、Graph Build Job、Write Batch、Lease、Fencing、Attempt、Count、Hash、Visibility、Sample Retrieval 验证。
- 当前 `KnowledgeIndexRuntime` 已证明 local BM25 / vector / graph adapter dispatch SPI 和 sample retrieval visibility，不再用 dispatch receipt 冒充可见。
- 后续 expand 层已新增外部 adapter binding contract，并证明外部 adapter 必须通过自身 readback 才能把 visibility 标为 `visible`；adapter contract 仍需为 `current` 才能进入默认 retrieval payload，readback 无匹配时 target 会降级且不进入 retrieval payload。
- Elasticsearch BM25 与 Neo4j Graph 外部 adapter 已通过真实容器服务 readback integration，`INDEX_ADAPTER_CONTRACTS` 对应项已标为 `current`。
- 但 `INDEX_ADAPTER_CONTRACTS` 仍明确把 `milvus` 标为 `target_blocked`。
- 本轮 Milvus 直接镜像拉取再次长时间停滞并停止；没有 Milvus 镜像或运行服务，因此无法执行真实 Vector Adapter 的 cutover / visibility / sample retrieval 证明。

因此不能把 PHASE12 写成 completed，也不能把 PHASE09/12/14 Wave A Gate 汇总写成 passed。

## 边界

- 本 review 不回滚 PR A 已完成修复。
- 本 review 不启动 Wave B。
- 本 review 不修改 `.agent/programs/current.md`、`.agent/programs/closure-checklist.md` 或 `docs/status/production-readiness.md` 的 phase 状态。
- 浏览器 E2E、UI reconnect 和更大范围旧 API cutover fault matrix 仍需后续 Gate 汇总处理；但当前第一个阻止 Wave A 合并的 mandatory blocker 是 PHASE12 外部索引 Adapter 未成为 Current。
