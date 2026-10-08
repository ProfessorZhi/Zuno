# Round 020 P0 Implementation Status

status: `IMPLEMENTED / LOCAL_VERIFICATION_ONLY / CI_PENDING`
source_ledger: [`rb-2026-10-07-formal-020/09_improvement_ledger.md`](../red-blue/rounds/rb-2026-10-07-formal-020/09_improvement_ledger.md)
base_main: `907a1453a3169a0bab2913f33cac701cd70204d7`
production_readiness: `NOT_ESTABLISHED`

Round 020 的 improvement ledger 里 A 组三条 P0（`IMP-020-01` / `IMP-020-02` / `IMP-020-03`）经用户批准为 `APPROVED_FOR_NEXT_ROUND`。本文件记录这三条的**实施结果与验证边界**：改了什么、证据在哪、本机验证到哪一步、哪一步没有在本机验证。

本文件不改变 Round 020 的 verdict，也不把任何 Target 升级成 Current。三条修复都不新增业务模块、状态机、Receipt、Provider，也不改 Authority / Recovery 语义。

## IMP-020-02 — per-user MCP 配置的归属校验（IDOR）

### 修复前

`GET /mcp_user_config/{config_id}` 与 `DELETE /mcp_user_config/delete` 的 handler 拿到了 `login_user`，但从不使用它；DAO 与 Service 也只按 `config_id` 过滤。任意登录用户可以凭一个 `config_id` 读取或删除**他人**的 MCP 用户配置。

同模块的 `update` 路径本来就是按 `user_id` + `mcp_server_id` 定位记录的，所以这是同一模块内部两条路径的不一致，而不是"权限模型没设计"。

### 改动

- `platform/database/dao/mcp_user_config.py`：`get_mcp_user_config_from_id` / `delete_mcp_user_config` 都加上 `user_id` 条件（`id == config_id AND user_id == user_id`），签名改为必填，避免出现"忘了传"的静默无作用域调用。
- `api/services/mcp_user_config.py`：两个方法接收并透传 `user_id`；取不到记录时抛 `No permission to access this MCP user config.`。删除路径先做归属查询再删除，与 `update` 的写法一致。
- `api/v1/mcp_user_config.py`：两条 handler 传 `login_user.user_id`。

**不区分"不存在"与"属于他人"**：两种情况返回同一条错误，避免用 `config_id` 探测他人记录是否存在。

### 证据与验证

新增 `tests/api/test_mcp_user_config_ownership.py`（6 条）。它 monkeypatch DAO 替身、走**真实的 service 逻辑与真实路由**（FastAPI TestClient + dependency override），并额外静态锁住 DAO 的 WHERE 子句同时含 `id ==` 与 `user_id ==`——因为路由级测试 monkeypatch 掉了 DAO，绕开了真实 SQL。

回归证明：把三个源文件临时回到修复前，该文件 **6 条全红**（含 `_FakeDao.get_mcp_user_config_from_id() missing 1 required positional argument: 'user_id'`）；修复后 6 条全绿。

### 影响面

本仓库前端没有任何 `mcp_user_config` 调用点（`src/frontend/` 下 grep 无命中），所以收紧不破坏调用方。

## IMP-020-03 — 恢复物流工具的 TLS 校验

### 修复前

`capability/tools/delivery/action.py` 在发出请求前设置：

```python
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
```

而同一个请求带着 `Authorization: APPCODE <api_key>`。关闭校验等于把凭据交给任意中间人。

### 改动

删除这两行，改用 `ssl.create_default_context()` 的默认校验（hostname + 证书链）。**没有**为此新增配置开关：自签名场景应把 CA 装进系统信任库，而不是由代码放宽。

### 证据与验证

`src/backend/zuno/capability/tools/delivery/action.py:44-49`。该函数无既有单测覆盖；本次未新增（该函数直接发外部 HTTP，构造可信单测需要引入 stub server，超出本次切片，记为未覆盖）。

## IMP-020-01 — 索引就绪状态在读取路径上默认开启

### 修复前

读取路径一律 `or "ready"`：缺配置、缺 `health_status`、缺字段都被判定为"就绪"。写入侧 `mark_ready` 有严格判定，读取侧绕过了它。后果不是崩溃，而是**静默地用未就绪的知识作答**。

### 改动（只动读取侧默认值）

| 位置 | 变化 |
| --- | --- |
| `platform/services/retrieval/planner.py` | `graph_health` 缺失 → `unavailable`（原 `ready`） |
| `platform/services/retrieval/orchestrator.py` | `graph_available` 的 `index_health.graph` 缺失 → `unavailable` |
| `platform/services/rag/handler.py` | 构造 `index_health` 时 `vector` / `graph` 缺失 → `unavailable`；去掉"`index_capability == rag_graph` 就默认 graph ready"这一分支 |
| `platform/services/application/knowledge/query_service.py` | 构造 `index_health` 时 `vector` / `graph` 缺失 → `unavailable` |
| `platform/services/graphrag/community/models.py` | `from_dict` 读回时 `status` 缺失 → `unavailable`（仅读回侧；dataclass 与 detector 的构造默认仍是 `ready`，那是"刚构建完"的声明） |
| `api/services/product/runtime_engine.py` | 新增 `_graph_index_available()`，替换原先硬编码的 `graph_available=True` |

`runtime_engine` 这一条**没有**退化成"一律不可用"，而是接到真实数据源：`KnowledgeIndexRuntime.to_retrieval_payload()` 的 `retrievers_used`（判定 = `target_status == "ready"` 且 adapter 契约当前且可见性回执为 `visible`），该 runtime 在 bootstrap 时从 durable ingestion store `rehydrate_index()` 重建。

### 降级是有记录的，不是静默的

`graph_available=False` 时 planner 走既有降级路径并留下痕迹：

```text
route_trace["fallback_reason"] = "graph_not_ready"
fallback_policy["graph_degraded"] = True
enabled_retrievers 去掉 "graph" → standard_rag
```

这正是 ledger 要求的"由调用方显式决定是否降级"。

### 为什么这不是"为了安全把系统收紧到不可用"

ledger 为这一条写了退出条件：**若实测发现大量路径确实没有 health 数据源，应先补数据源再收紧。** 实测结论是数据源存在：

- `api/services/knowledge.py` 建库模板里 `index_settings.health_status` 与 `graph_index_settings.health_status` 都是 `"ready"`，正常知识库不会因本次改动降级；
- 产品运行时 ingest 的 targets 是 `["bm25", "vector", "graph"]`，成功索引后 graph 会处于 `ready`，因此 `_graph_index_available()` 在正常路径返回 `True`，DEEP 不降级。

改动只影响"字段真的缺失"的配置（遗留 / 异常），此时 fail-closed 才是想要的。

### 现有测试里固化的 fail-open 期望，已显式化

有 5 个既有 planner 单测在**不传** `index_health` 的情况下断言图路由保持可用（`tests/retrieval/test_retrieval_planner.py` 3 条、`tests/graphrag/test_graphrag_route_activation_calibration.py` 2 条）。它们真正的意图是"图索引健康时不静默退回 standard_rag"，只是把前提留给了默认值。

处理方式：给这些调用点**显式写上** `index_health={"graph": "ready"}`，断言一个字都没改。目的是让这条前提从"默认值"变成"写出来的前提"——这正是本轮方法论教训的反面：诚实信号不能是默认值。

### 证据与验证

新增 `tests/retrieval/test_readiness_fail_closed.py`（8 条），覆盖：缺失/显式 `unavailable` 降级且带 trace、显式 `ready` 保持原路由（防止把 fail-closed 做成"一律降级"）、`from_dict` 读回不假定 ready 而构造默认仍是 ready、`_graph_index_available()` 的 True/False/KeyError/空知识空间/多空间取并集。

回归证明：把 `src/backend` 临时回到修复前，该文件 **5 条红 3 条绿**（3 条绿的是"显式 ready 保持原路由"，本来就该在修复前后都成立）；修复后 8 条全绿。

### 未做的部分

- `platform/services/graphrag/community/service.py:41,47`：`build_level0_communities` 在成功构建后把持久化 `status` 默认成 `ready`、并在返回值里声明 `community_detection_status/community_report_status = "ready"`。这是**构建方对自己刚产出的东西的声明**（该函数只在检测与报告都完成后走到），不是读取侧的 fail-open，因此本次不改。若后续要收紧，需要先定义"构建成功"与"报告可用"是否是同一件事。
- `api/dto/knowledge.py` 的 `health_status: str = Field(default="ready")` 是请求/响应 DTO 的默认值，与建库写入路径一致，本次不改。

## 验证边界（本机 vs CI）

本机（Windows，无 venv，`PYTHONPATH=src/backend`，依赖按需从清华镜像装）实际执行：

- 新增两个测试文件的全部 14 条（`test_mcp_user_config_ownership.py` 6 条 + `test_readiness_fail_closed.py` 8 条）；
- `tests/retrieval`、`tests/graphrag`、`tests/knowledge` 与 5 个 agent 规划/契约测试的集合。

该集合在本机存在 **45 条与本次改动无关的既存失败**（`test_workspace_simple_agent.py` 27 条、`test_2wiki_missed_opportunity_activation.py` 5 条等，均为本机依赖/环境差异）。取得基线的方式是：同一集合下把 `src/backend` 回到修复前再跑一遍，两份失败清单 **diff 为空**——即本次改动**净新增失败为 0**。

本分支相对 `base_main` 的改动已做行尾核对：`git diff --numstat` 与 `git diff --ignore-cr-at-eol --numstat` 逐文件一致，即 diff 中**没有纯行尾变更**。该仓库有 4 个文件的 blob 本身存的就是 CRLF 且行尾混杂（`orchestrator.py` / `planner.py` / `rag/handler.py` / `tests/retrieval/test_retrieval_planner.py`），本 PR **不重排**这些文件的既有行尾——否则一个安全修复会被上千行纯换行符变更淹没。

**没有在本机验证的部分**：

- CI `Current code selected verification` 的 Postgres-backed 用例（本机无 PostgreSQL），包括 `tests/repo/test_product_runtime_execution_spec_postgres.py` 与 `tests/architecture/test_p0_v4_execution.py`。`runtime_engine` 的 `graph_available` 改动因此**只在单元层被验证**（`_graph_index_available()` 的取值），端到端 DEEP 路由未在本机复现。
- 上述两条新增测试文件已登记进 `.github/workflows/current-code-selected-verification.yml` 的 selected 列表，否则它们不会在 CI 执行。

`production_readiness: NOT_ESTABLISHED` 保持不变：这三条修的是已证实的缺陷，不构成任何生产就绪主张。
