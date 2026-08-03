# Goal05 PHASE22 CC-MM-2 Environment Verification

agent: claude-code
model: claude-minimax
worker: CC-MM-2
cost_scope: single-agent-pr-handoff
session_id: 32b67ef2-b1e9-42f6-aef8-b28271711ab9
date: 2026-08-03
branch: codex/phase22-environment-verification-claude-minimax-cc-mm-2
status: environment_probe_only

> environment_probe_only, benchmark_not_measured, no release decision.

## Coordinator Review

```text
worker_commit=bb522d2b
coordinator_decision=WORKER_ACCEPTED_FOR_INTEGRATION
coordinator_score=88
accepted_paths=docs/evidence/goal05-phase22-worker-cc-mm-2-environment-verification.md
api_cost_usd_estimated=0.666285
provider_quota_basis=unknown
duration_ms=107524
```

Score breakdown:

```text
identity and traceability: 8/10
scope containment: 15/15
requirement fit and correctness: 16/20
tests and reproducibility: 12/15
evidence honesty: 10/10
security / approval / audit: 15/15
cost and time efficiency: 4/5
integration risk: 8/10
```

Coordinator notes: worker evidence omitted the actual session id in-file, but the coordinator recovered it from Claude Code `stream-json --verbose` logs. No additional worker resume was used after budget exhaustion because the accepted path was evidence-only and the metadata fix is a coordinator integration amendment.

## Scope

This evidence records the **non-destructive** environment verification probe run
in this worker session for PHASE22. It does **not** declare a benchmark pass,
admit any canonical profile as `measured`, or contribute to a release decision.

Allowed scope (per worker contract):

- `infra/docker/**` (read-only inspection of compose manifests)
- `tools/evals/zuno/synthetic_benchmark/**` (directory does not yet exist on
  this branch — recorded as `unknown`, no mutation attempted)
- `tools/scripts/**phase22*environment*.py` (no matching script exists on this
  branch — recorded as `unknown`, no mutation attempted)
- `tests/evals/synthetic_benchmark/**` (directory does not yet exist on this
  branch — recorded as `unknown`, no mutation attempted)
- `docs/evidence/goal05-phase22-worker-cc-mm-2-environment-verification.md`
  (this file)

Forbidden scope (per worker contract, not touched):

- `.agent/programs/program-manifest.yaml`
- `.agent/programs/current.md`
- `docs/status/production-readiness.md`
- `docs/evidence/goal05-phase22-synthetic-benchmark/**`
- `src/backend/zuno/**` core contracts
- No destructive cleanup was performed against running host containers.

## Docker Host Probe

Observed on this session at 2026-08-03 (host where the worker shell runs):

```powershell
docker --version
docker compose version
docker ps
docker compose -f infra/docker/docker-compose.yml --profile elasticsearch ps
```

Observed host toolchain:

```text
Docker version 29.4.0, build 9d7ad9f
Docker Compose version v5.1.1
```

Observed container set (from `docker ps`; all started ~2 hours before probe):

| container           | image                                                              | status          |
|---------------------|--------------------------------------------------------------------|-----------------|
| zuno-postgres       | postgres:16                                                        | Up (healthy)    |
| zuno-redis          | redis:7.0-alpine                                                   | Up (healthy)    |
| zuno-rabbitmq       | rabbitmq:3.13-management-alpine                                    | Up (healthy)    |
| zuno-neo4j          | neo4j:5-community                                                  | Up (healthy)    |
| zuno-elasticsearch  | docker.elastic.co/elasticsearch/elasticsearch:7.17.24              | Up (healthy)    |
| zuno-minio          | minio/minio:RELEASE.2023-03-20T20-16-18Z                           | Up (healthy)    |
| zuno-etcd           | quay.io/coreos/etcd:v3.5.5                                         | Up (healthy)    |
| zuno-milvus         | milvusdb/milvus:v2.4.15                                            | Up (healthy)    |
| zuno-backend        | docker-backend                                                     | Up (healthy)    |
| zuno-worker         | docker-backend                                                     | Up (no healthcheck) |
| zuno-frontend       | docker-frontend                                                    | Up (healthy)    |

## Per-Service Probes (run, not asserted as benchmark)

### PostgreSQL (`zuno-postgres`)

```bash
docker exec zuno-postgres pg_isready -U postgres -d zuno
docker exec zuno-postgres psql -U postgres -d zuno -c "SELECT version();"
```

Observed:

```text
/var/run/postgresql:5432 - accepting connections
PostgreSQL 16.14 (Debian 16.14-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
```

Status: **reachable, healthy**. Read-only `SELECT version()` only; no write attempted.

### Redis (`zuno-redis`)

```bash
docker exec zuno-redis redis-cli ping
```

Observed: `PONG`

Status: **reachable, healthy**. No write attempted.

### RabbitMQ (`zuno-rabbitmq`)

```bash
docker exec zuno-rabbitmq rabbitmq-diagnostics -q ping
docker exec zuno-rabbitmq rabbitmqctl list_queues
```

Observed:

```text
Ping succeeded
Listing queues for vhost / ...
name	messages
```

Status: **reachable, healthy, no queues enumerated yet**. No publish/consume
attempted (would be a destructive side effect under shared broker state).

### Neo4j (`zuno-neo4j`)

```bash
docker exec zuno-neo4j cypher-shell -u neo4j -p neo4j12345 "RETURN 1 AS ok;"
```

Observed:

```text
ok
1
```

Status: **reachable, healthy**. Read-only `RETURN 1` only; no cypher write
attempted against application datasets.

### Elasticsearch (`zuno-elasticsearch`)

```bash
docker exec zuno-elasticsearch curl -fsS http://localhost:9200/_cluster/health
curl -fsS http://localhost:9200/_cluster/health?pretty
```

Observed:

```text
{
  "cluster_name": "docker-cluster",
  "status": "yellow",
  "timed_out": false,
  "number_of_nodes": 1,
  "number_of_data_nodes": 1,
  "active_primary_shards": 5,
  "active_shards": 5,
  "unassigned_shards": 4,
  "active_shards_percent_as_number": 55.55555555555556
}
```

Status: **reachable, cluster `yellow`**. Yellow is expected for a single-node
cluster (no replica shards can be assigned); no read/write attempted against
Zuno indices.

### MinIO (`zuno-minio`)

```bash
docker exec zuno-minio curl -fsS -o /dev/null -w "minio_live=%{http_code}\n" http://localhost:9000/minio/health/live
docker exec zuno-minio curl -fsS -o /dev/null -w "minio_ready=%{http_code}\n" http://localhost:9000/minio/health/ready
```

Observed:

```text
minio_live=200
minio_ready=200
```

Status: **reachable, live + ready**. No bucket put/get attempted.

### Milvus (`zuno-milvus`) + Etcd (`zuno-etcd`)

```bash
docker exec zuno-milvus curl -fsS http://localhost:9091/healthz
docker exec zuno-etcd etcdctl endpoint health --endpoints=http://localhost:2379
```

Observed:

```text
OK
http://localhost:2379 is healthy: successfully committed proposal: took = 13.294857ms
```

Status: **Milvus reachable + OK, etcd reachable + healthy**. No
collection/insert/query attempted against Zuno collections.

### Backend HTTP (`zuno-backend`)

```bash
curl -fsS http://localhost:7860/health
```

Observed: `{"status":"OK"}`

Status: **reachable, healthy**. No API mutation attempted.

### Checkpointer

The official LangGraph PostgreSQL Checkpointer
(`langgraph.checkpoint.postgres.PostgresSaver`, ADR 0005) targets the
existing `zuno-postgres` instance (`postgresql+psycopg://postgres:postgres@postgres:5432/zuno`
in `infra/docker/docker_config.example.yaml`). Postgres above is reachable.

Status: **unknown until a phase22 environment verifier script is run**. No
matching `tools/scripts/**phase22*environment*.py` exists on this branch yet
(see "Unknown / Not Probed" below), so no `setup()` / `put()` / `get_tuple()`
lifecycle was exercised by this worker. That work belongs to a later
phase22 environment-verification worker and is out of scope here.

## Unknown / Not Probed by This Worker

The following items were **not** probed in this session and are recorded as
`unknown` rather than `passed`:

- `tools/evals/zuno/synthetic_benchmark/` directory — does not exist on this
  branch (`unknown`).
- `tests/evals/synthetic_benchmark/` directory — does not exist on this branch
  (`unknown`).
- `tools/scripts/**phase22*environment*.py` — no matching file on this branch
  (`unknown`).
- Official LangGraph PostgreSQL Checkpointer write/read-back lifecycle against
  `zuno-postgres` — not exercised here; deferred to a follow-up worker.
- Any benchmark run (paired benchmark, deep-agentic runtime, profile-runners,
  etc.) — explicitly out of scope; this worker is environment-probe only.
- Production-readiness, release-decision, archive-preflight content — forbidden
  paths, untouched.

## Proposed Write/Read-Back Matrix (proposed, not executed)

This matrix is **proposed for a follow-up environment-verification worker**
that has explicit authorization to run non-destructive write/read-back probes.
It records the *intended* probe shape; nothing below was performed in this
session.

| Service     | Write probe (proposed)                                          | Read-back probe (proposed)                              | Cleanup                  |
|-------------|-----------------------------------------------------------------|---------------------------------------------------------|--------------------------|
| PostgreSQL  | `INSERT` into dedicated `phase22_env_probe` schema-namespace table, then `SELECT` by probe id | row round-trip via `psycopg`/`asyncpg` with the same shape used by `PostgresSaver` | `DELETE` by probe id; drop schema-namespace |
| Redis       | `SET phase22:env:probe:<id> <value>` with TTL                    | `GET phase22:env:probe:<id>`                            | `DEL` key                |
| RabbitMQ    | `basic_publish` to a per-probe ephemeral queue                   | `basic_get` returns the published payload                | `queue_delete` on success/failure |
| Neo4j       | `CREATE (n:Phase22EnvProbe {probe_id:$id})` with a marker label | `MATCH (n:Phase22EnvProbe {probe_id:$id}) RETURN n`      | `MATCH (n:Phase22EnvProbe {probe_id:$id}) DELETE n` |
| Elasticsearch | `POST /phase22_env_probe/_doc/<id>` against a probe-only index | `GET /phase22_env_probe/_doc/<id>`                      | `DELETE /phase22_env_probe` |
| MinIO       | `PutObject` to a `phase22-env-probe/` prefix in the configured bucket | `GetObject` returns identical bytes                  | `RemoveObject` on the probe key |
| Milvus      | create probe-only collection `phase22_env_probe`, insert 1 vector, flush, search by id | `query` returns the inserted vector                    | drop collection          |
| etcd        | `put phase22/env/probe/<id> -- val=<v>`                         | `get phase22/env/probe/<id>`                            | `del phase22/env/probe/<id>` |
| Checkpointer | `PostgresSaver.setup()` + `put()` + `put_writes()` into a probe thread_id | `get_tuple()` + `get_state_history()` returns the same writes | `delete_thread()`        |

Hard rules for any follow-up worker that runs the matrix:

1. Use a dedicated, probe-only identifier namespace (table prefix, key prefix,
   queue name, collection name, index name, etc.) so writes never collide with
   Zuno application data.
2. Every write **must** be paired with its read-back in the same run; on any
   read-back mismatch the worker must `FAIL_CLOSED` and not retry.
3. Cleanup is mandatory after read-back, even on failure paths.
4. Probe results must be recorded in a follow-up evidence file under
   `docs/evidence/goal05-phase22-*-environment-probe.md` (the synthetic-benchmark
   subfolder remains forbidden for this worker).
5. Do **not** mark any canonical profile `measured`, `RUNTIME_OBSERVED→fixed`,
   or PHASE22 complete on the basis of probe success alone.

## Observed Blockers

- `tools/evals/zuno/synthetic_benchmark/` is not present on this branch; no
  synthetic benchmark worker surfaces to co-ordinate probes with.
- `tools/scripts/**phase22*environment*.py` is not present on this branch; no
  probe driver script to execute.
- Elasticsearch cluster reports `yellow` (single-node replica unassigned).
  That is the expected single-node state and not a benchmark blocker for
  read-only probes, but any workload that *requires* `green` must surface a
  separate repro note.
- No host cleanup was performed; existing volumes and containers are intact.

## Boundary

- This evidence is `environment_probe_only`. It does **not** claim benchmark
  pass, canonical profile `measured`, or any release decision.
- This evidence is non-destructive: no write/read-back probe was executed in
  this session. The matrix above is a proposal for a follow-up worker.
- PHASE22 closure remains blocked by the standing gaps recorded in
  `docs/evidence/goal05-phase22-completion-blockers.md` and
  `docs/evidence/goal05-phase22-measurement-admission-evidence-closure.md`;
  this evidence contributes environment liveness data, not closure.
