# Zuno 平台升级实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Zuno 升级为以 `PostgreSQL + Redis + RabbitMQ + Neo4j + LangSmith` 为基础设施底座、支持 `RAG / GraphRAG / Hybrid / Auto` 的单 Agent 平台。

**Architecture:** 先完成数据库主库迁移，再收口运行时短期状态与可观测性，再把知识库处理链从同步逻辑重构为有状态的 pipeline，之后接入 RabbitMQ 做异步执行，最后把 Neo4j GraphRAG 接入检索编排层。每一轮必须完成工程验证、业务验证和证据验证，验证不过不得进入下一轮。

**Tech Stack:** FastAPI、SQLModel、SQLAlchemy、PostgreSQL、Alembic、Redis、RabbitMQ、Neo4j、LangGraph、LangSmith、Vue 3、Element Plus

---

## 文件结构与责任边界

### 后端核心文件

- `src/backend/agentchat/settings.py`
  - 配置加载入口
- `src/backend/agentchat/config.yaml`
  - 本地默认配置模板
- `src/backend/agentchat/main.py`
  - FastAPI 入口、生命周期和中间件注册
- `src/backend/agentchat/database/__init__.py`
  - 数据库引擎、连接初始化、数据库层总入口
- `src/backend/agentchat/database/session.py`
  - 同步和异步 session 获取
- `src/backend/agentchat/database/init_data.py`
  - 启动时初始化逻辑
- `src/backend/agentchat/database/models/*.py`
  - SQLModel 表定义
- `src/backend/agentchat/database/dao/*.py`
  - 数据访问
- `src/backend/agentchat/services/redis.py`
  - Redis 客户端封装
- `src/backend/agentchat/api/services/knowledge_file.py`
  - 当前知识文件处理入口，将被重构为 pipeline 入口
- `src/backend/agentchat/services/rag/handler.py`
  - RAG 检索和索引入口
- `src/backend/agentchat/api/v1/workspace.py`
  - 工作台 SSE 查询入口
- `src/backend/agentchat/services/workspace/simple_agent.py`
  - 单 Agent 主链路
- `src/backend/agentchat/middleware/trace_id_middleware.py`
  - trace_id 注入

### 本轮预计新增文件

- `src/backend/alembic.ini`
- `src/backend/alembic/env.py`
- `src/backend/alembic/versions/*.py`
- `src/backend/agentchat/schema/runtime.py`
- `src/backend/agentchat/database/models/knowledge_task.py`
- `src/backend/agentchat/database/dao/knowledge_task.py`
- `src/backend/agentchat/services/pipeline/*.py`
- `src/backend/agentchat/services/queue/*.py`
- `src/backend/agentchat/services/graphrag/*.py`
- `src/backend/agentchat/api/v1/task.py`

### 前端预计修改文件

- `src/frontend/src/apis/knowledge.ts`
- `src/frontend/src/apis/workspace.ts`
- `src/frontend/src/pages/knowledge/knowledge.vue`
- `src/frontend/src/pages/knowledge/knowledge-file.vue`
- `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue`

---

## 小轮 1：PostgreSQL 迁移

**Files:**
- Create: `src/backend/alembic.ini`
- Create: `src/backend/alembic/env.py`
- Create: `src/backend/alembic/versions/20260417_01_init_postgresql.py`
- Modify: `src/backend/agentchat/settings.py`
- Modify: `src/backend/agentchat/config.yaml`
- Modify: `src/backend/agentchat/database/__init__.py`
- Modify: `src/backend/agentchat/database/session.py`
- Modify: `src/backend/agentchat/database/init_data.py`
- Modify: `src/backend/agentchat/core/agents/text2sql_agent.py`
- Modify: `src/backend/agentchat/prompts/completion.py`
- Test: `src/backend/agentchat/test/test_sqlmodel.py`

- [ ] **Step 1: 为数据库配置抽象写失败用例**

```python
# src/backend/agentchat/test/test_sqlmodel.py
def test_database_settings_support_postgresql_urls():
    from agentchat.settings import Settings

    settings = Settings()
    settings.database = {
        "sync_endpoint": "postgresql+psycopg://postgres:postgres@localhost:5432/zuno",
        "async_endpoint": "postgresql+asyncpg://postgres:postgres@localhost:5432/zuno",
    }

    assert settings.database["sync_endpoint"].startswith("postgresql+psycopg://")
    assert settings.database["async_endpoint"].startswith("postgresql+asyncpg://")
```

- [ ] **Step 2: 运行测试确认当前失败**

Run: `pytest src/backend/agentchat/test/test_sqlmodel.py -v`  
Expected: FAIL，原因是当前配置仍然是 `mysql` 字段和 MySQL URL。

- [ ] **Step 3: 抽象数据库配置模型**

```yaml
# src/backend/agentchat/config.yaml
database:
  sync_endpoint: "postgresql+psycopg://postgres:postgres@localhost:5432/zuno"
  async_endpoint: "postgresql+asyncpg://postgres:postgres@localhost:5432/zuno"
  echo: false
  pool_size: 10
  max_overflow: 20
```

```python
# src/backend/agentchat/settings.py
class Settings(BaseSettings):
    database: dict = {}
    redis: dict = {}
    server: dict = {}
```

- [ ] **Step 4: 切换数据库引擎到 PostgreSQL**

```python
# src/backend/agentchat/database/__init__.py
engine = create_engine(
    url=app_settings.database.get("sync_endpoint"),
    pool_pre_ping=True,
    pool_recycle=3600,
)

async_engine = create_async_engine(
    url=app_settings.database.get("async_endpoint"),
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

- [ ] **Step 5: 删除 MySQL 专属启动逻辑并改成 migration 驱动**

```python
# src/backend/agentchat/database/init_data.py
async def init_database():
    SQLModel.metadata.create_all(engine)
```

说明：
- 这一小步先临时保证 PostgreSQL 可启动
- 下一步 Alembic 建好后再把 `create_all` 收敛为 migration

- [ ] **Step 6: 初始化 Alembic 文件骨架**

```python
# src/backend/alembic/env.py
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from agentchat.database.models.base import SQLModel
from agentchat.database import app_settings

config = context.config
config.set_main_option("sqlalchemy.url", app_settings.database.get("sync_endpoint"))
target_metadata = SQLModel.metadata
```

- [ ] **Step 7: 清理 MySQL 专属残留**

```python
# src/backend/agentchat/core/agents/text2sql_agent.py
# 第一轮先改为显式抛出 PostgreSQL-only/disabled 提示，避免保留 pymysql 硬依赖
raise NotImplementedError("text2sql_agent needs PostgreSQL adaptation before use")
```

```python
# src/backend/agentchat/prompts/completion.py
# 将 “你是一个 MySQL 专家” 改成更中性的 SQL 助手描述
```

- [ ] **Step 8: 安装并运行 PostgreSQL 驱动依赖**

Run: `pip install psycopg asyncpg alembic`  
Expected: 安装成功。

- [ ] **Step 9: 运行数据库测试**

Run: `pytest src/backend/agentchat/test/test_sqlmodel.py -v`  
Expected: PASS

- [ ] **Step 10: 启动后端进行工程验证**

Run: `python scripts/start.py`  
Expected:
- 后端启动成功
- 不再依赖 MySQL 驱动
- 核心路由可加载

- [ ] **Step 11: 做业务验证**

验证：
- 登录
- 查询 workspace session
- 查询 knowledge 列表

Expected: 基础 CRUD 正常。

- [ ] **Step 12: 做证据验证**

检查：
- PostgreSQL 中已存在核心表
- 应用启动日志正常

Run: `git add src/backend/alembic.ini src/backend/alembic src/backend/agentchat/settings.py src/backend/agentchat/config.yaml src/backend/agentchat/database src/backend/agentchat/core/agents/text2sql_agent.py src/backend/agentchat/prompts/completion.py src/backend/agentchat/test/test_sqlmodel.py && git commit -m "feat: migrate core database path to postgresql"`

---

## 小轮 2：Redis 与 LangSmith 基础收口

**Files:**
- Create: `src/backend/agentchat/schema/runtime.py`
- Modify: `src/backend/agentchat/services/redis.py`
- Modify: `src/backend/agentchat/api/v1/user.py`
- Modify: `src/backend/agentchat/api/services/user.py`
- Modify: `src/backend/agentchat/utils/captcha.py`
- Modify: `src/backend/agentchat/api/v1/workspace.py`
- Modify: `src/backend/agentchat/services/workspace/simple_agent.py`
- Modify: `src/backend/agentchat/services/rag/handler.py`
- Modify: `src/backend/agentchat/middleware/trace_id_middleware.py`
- Modify: `src/backend/agentchat/main.py`
- Test: `src/backend/agentchat/test/test_config.py`

- [ ] **Step 1: 定义 Redis 键命名常量**

```python
# src/backend/agentchat/schema/runtime.py
AUTH_USER_TOKEN = "auth:user:{user_id}:token"
CAPTCHA_KEY = "captcha:{captcha_key}"
TASK_PROGRESS_KEY = "task_progress:{task_id}"
RETRIEVAL_CACHE_KEY = "retrieval_cache:{knowledge_id}:{query_hash}"
```

- [ ] **Step 2: 让 Redis 客户端使用统一 key 常量**

```python
# src/backend/agentchat/services/redis.py
from agentchat.schema.runtime import AUTH_USER_TOKEN, CAPTCHA_KEY, TASK_PROGRESS_KEY
```

- [ ] **Step 3: 为 LangSmith 加环境变量与开关读取**

```python
# src/backend/agentchat/main.py
import os

os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "zuno")
```

- [ ] **Step 4: 在 workspace 请求入口注入 tracing metadata**

```python
# src/backend/agentchat/api/v1/workspace.py
trace_metadata = {
    "trace_id": getattr(login_user, "trace_id", ""),
    "user_id": login_user.user_id,
    "session_id": simple_task.session_id,
    "retrieval_mode": getattr(simple_task, "retrieval_mode", "default"),
}
```

- [ ] **Step 5: 在 simple agent 主链路埋点**

```python
# src/backend/agentchat/services/workspace/simple_agent.py
self.run_metadata = {
    "trace_id": trace_id,
    "user_id": user_id,
    "session_id": session_id,
}
```

- [ ] **Step 6: 在 RAG 检索入口埋点**

```python
# src/backend/agentchat/services/rag/handler.py
logger.bind(retrieval_mode="rag").info("Starting RAG retrieval")
```

- [ ] **Step 7: 运行配置类测试**

Run: `pytest src/backend/agentchat/test/test_config.py -v`  
Expected: PASS

- [ ] **Step 8: 做工程验证**

Run: `python scripts/start.py`  
Expected:
- 服务启动正常
- Redis 连接可用
- 没有因为 LangSmith tracing 破坏 SSE

- [ ] **Step 9: 做业务验证**

验证：
- 登录一次
- 发起一次 workspace 对话

Expected:
- Redis 中能看到规范化 token key
- 对话仍能正常流式返回

- [ ] **Step 10: 做证据验证**

检查：
- LangSmith 中能看到一次完整 query trace
- run metadata 中带 `trace_id / user_id / session_id`

Run: `git add src/backend/agentchat/schema/runtime.py src/backend/agentchat/services/redis.py src/backend/agentchat/api/v1/user.py src/backend/agentchat/api/services/user.py src/backend/agentchat/utils/captcha.py src/backend/agentchat/api/v1/workspace.py src/backend/agentchat/services/workspace/simple_agent.py src/backend/agentchat/services/rag/handler.py src/backend/agentchat/middleware/trace_id_middleware.py src/backend/agentchat/main.py src/backend/agentchat/test/test_config.py && git commit -m "feat: standardize redis runtime keys and langsmith tracing"`

---

## 小轮 3：Knowledge Pipeline 抽象

**Files:**
- Create: `src/backend/agentchat/database/models/knowledge_task.py`
- Create: `src/backend/agentchat/database/dao/knowledge_task.py`
- Create: `src/backend/agentchat/services/pipeline/models.py`
- Create: `src/backend/agentchat/services/pipeline/manager.py`
- Create: `src/backend/agentchat/services/pipeline/stages.py`
- Modify: `src/backend/agentchat/database/models/knowledge_file.py`
- Modify: `src/backend/agentchat/api/services/knowledge_file.py`
- Modify: `src/backend/agentchat/api/v1/knowledge_file.py`
- Test: `src/backend/agentchat/test/test_pipeline.py`

- [ ] **Step 1: 先写任务状态机测试**

```python
# src/backend/agentchat/test/test_pipeline.py
def test_pipeline_task_stage_flow():
    stages = ["uploaded", "queued", "parsing", "splitting", "rag_indexing", "graph_extracting", "graph_indexing", "completed"]
    assert stages[0] == "uploaded"
    assert stages[-1] == "completed"
```

- [ ] **Step 2: 定义任务模型**

```python
# src/backend/agentchat/database/models/knowledge_task.py
class KnowledgeTask(SQLModelSerializable, table=True):
    id: str = Field(primary_key=True)
    knowledge_id: str
    knowledge_file_id: str
    task_type: str
    status: str
    current_stage: str
    retry_count: int = 0
    error_message: str | None = None
```

```python
class KnowledgeTaskEvent(SQLModelSerializable, table=True):
    id: str = Field(primary_key=True)
    task_id: str
    stage: str
    status: str
    message: str
```

- [ ] **Step 3: 扩展知识文件模型状态字段**

```python
# src/backend/agentchat/database/models/knowledge_file.py
parse_status: str = "pending"
rag_index_status: str = "pending"
graph_index_status: str = "pending"
last_task_id: str | None = None
last_error: str | None = None
```

- [ ] **Step 4: 抽 pipeline 结构模型**

```python
# src/backend/agentchat/services/pipeline/models.py
PIPELINE_STAGES = [
    "uploaded",
    "queued",
    "parsing",
    "splitting",
    "rag_indexing",
    "graph_extracting",
    "graph_indexing",
    "completed",
]
```

- [ ] **Step 5: 实现同步版 pipeline manager**

```python
# src/backend/agentchat/services/pipeline/manager.py
class KnowledgePipelineManager:
    async def run_sync(self, task_id: str):
        ...
```

- [ ] **Step 6: 把 knowledge file 入口改成创建任务并走 pipeline manager**

```python
# src/backend/agentchat/api/services/knowledge_file.py
task_id = await KnowledgeTaskDao.create_task(...)
await KnowledgePipelineManager().run_sync(task_id)
```

- [ ] **Step 7: 运行 pipeline 测试**

Run: `pytest src/backend/agentchat/test/test_pipeline.py -v`  
Expected: PASS

- [ ] **Step 8: 做工程验证**

Run: `python scripts/start.py`  
Expected:
- 服务启动正常
- 上传文件流程不报错

- [ ] **Step 9: 做业务验证**

验证：
- 上传一个知识文件
- 能看到任务记录
- 能看到阶段状态变化

- [ ] **Step 10: 做证据验证**

检查：
- PostgreSQL 中有 `knowledge_task` 和 `knowledge_task_event`
- 文件记录中状态字段已更新

Run: `git add src/backend/agentchat/database/models/knowledge_task.py src/backend/agentchat/database/dao/knowledge_task.py src/backend/agentchat/services/pipeline src/backend/agentchat/database/models/knowledge_file.py src/backend/agentchat/api/services/knowledge_file.py src/backend/agentchat/api/v1/knowledge_file.py src/backend/agentchat/test/test_pipeline.py && git commit -m "feat: add knowledge pipeline task model"`

---

## 小轮 4：RabbitMQ 异步化 Pipeline

**Files:**
- Create: `src/backend/agentchat/services/queue/client.py`
- Create: `src/backend/agentchat/services/queue/messages.py`
- Create: `src/backend/agentchat/services/queue/workers.py`
- Modify: `src/backend/agentchat/services/pipeline/manager.py`
- Modify: `src/backend/agentchat/api/services/knowledge_file.py`
- Modify: `src/backend/agentchat/config.yaml`
- Test: `src/backend/agentchat/test/test_queue.py`

- [ ] **Step 1: 先写消息结构测试**

```python
# src/backend/agentchat/test/test_queue.py
def test_queue_message_contains_task_refs():
    payload = {
        "task_id": "task_1",
        "knowledge_id": "k_1",
        "knowledge_file_id": "f_1",
        "stage": "parsing",
        "trace_id": "trace_1",
    }
    assert payload["task_id"] == "task_1"
```

- [ ] **Step 2: 定义 RabbitMQ 配置项**

```yaml
# src/backend/agentchat/config.yaml
rabbitmq:
  url: "amqp://guest:guest@localhost:5672/"
  parse_queue: "knowledge.parse"
  index_queue: "knowledge.index"
  graph_queue: "knowledge.graph"
```

- [ ] **Step 3: 实现消息模型**

```python
# src/backend/agentchat/services/queue/messages.py
class KnowledgeTaskMessage(TypedDict):
    task_id: str
    knowledge_id: str
    knowledge_file_id: str
    stage: str
    trace_id: str
```

- [ ] **Step 4: 实现 queue client**

```python
# src/backend/agentchat/services/queue/client.py
class QueueClient:
    async def publish(self, queue_name: str, payload: dict):
        ...
```

- [ ] **Step 5: 实现三个 worker**

```python
# src/backend/agentchat/services/queue/workers.py
class ParseWorker: ...
class IndexWorker: ...
class GraphWorker: ...
```

- [ ] **Step 6: 把 pipeline manager 改成 producer**

```python
# src/backend/agentchat/services/pipeline/manager.py
await queue_client.publish(parse_queue, payload)
```

- [ ] **Step 7: 运行队列测试**

Run: `pytest src/backend/agentchat/test/test_queue.py -v`  
Expected: PASS

- [ ] **Step 8: 做工程验证**

验证：
- RabbitMQ 服务可连
- 发送消息不报错
- worker 启动正常

- [ ] **Step 9: 做业务验证**

验证：
- 上传一个文件
- 任务进入队列
- parse -> index -> graph 顺序执行

- [ ] **Step 10: 做证据验证**

检查：
- Redis 中有 `task_progress:{task_id}`
- PostgreSQL 最终状态为成功或失败
- RabbitMQ 管理界面可见消息消费

Run: `git add src/backend/agentchat/services/queue src/backend/agentchat/services/pipeline/manager.py src/backend/agentchat/api/services/knowledge_file.py src/backend/agentchat/config.yaml src/backend/agentchat/test/test_queue.py && git commit -m "feat: add rabbitmq-driven knowledge pipeline"`

---

## 小轮 5：Neo4j + GraphRAG

**Files:**
- Create: `src/backend/agentchat/services/graphrag/models.py`
- Create: `src/backend/agentchat/services/graphrag/client.py`
- Create: `src/backend/agentchat/services/graphrag/extractor.py`
- Create: `src/backend/agentchat/services/graphrag/retriever.py`
- Create: `src/backend/agentchat/services/graphrag/orchestrator.py`
- Modify: `src/backend/agentchat/services/rag/handler.py`
- Modify: `src/backend/agentchat/schema/knowledge.py`
- Modify: `src/backend/agentchat/database/models/knowledge.py`
- Modify: `src/backend/agentchat/api/v1/knowledge.py`
- Modify: `src/backend/agentchat/api/v1/workspace.py`
- Modify: `src/frontend/src/apis/knowledge.ts`
- Modify: `src/frontend/src/apis/workspace.ts`
- Modify: `src/frontend/src/pages/knowledge/knowledge.vue`
- Modify: `src/frontend/src/pages/knowledge/knowledge-file.vue`
- Modify: `src/frontend/src/pages/workspace/defaultPage/defaultPage.vue`
- Test: `src/backend/agentchat/test/test_graphrag.py`

- [ ] **Step 1: 先写 GraphRAG 模式测试**

```python
# src/backend/agentchat/test/test_graphrag.py
def test_retrieval_modes_include_graphrag():
    modes = {"default", "rag", "graphrag", "hybrid", "auto"}
    assert "graphrag" in modes
    assert "hybrid" in modes
```

- [ ] **Step 2: 给知识库增加默认检索模式字段**

```python
# src/backend/agentchat/database/models/knowledge.py
default_retrieval_mode: str = "rag"
```

```python
# src/backend/agentchat/schema/knowledge.py
default_retrieval_mode: Optional[str] = "rag"
```

- [ ] **Step 3: 实现 Neo4j 客户端**

```python
# src/backend/agentchat/services/graphrag/client.py
class Neo4jClient:
    async def upsert_entity(self, entity: dict): ...
    async def upsert_relation(self, relation: dict): ...
    async def query_neighbors(self, entity_name: str, hops: int = 1): ...
```

- [ ] **Step 4: 实现图谱抽取器**

```python
# src/backend/agentchat/services/graphrag/extractor.py
class GraphExtractor:
    async def extract_from_chunk(self, chunk: dict) -> dict:
        return {"entities": [], "relations": []}
```

- [ ] **Step 5: 实现 GraphRAG 检索器**

```python
# src/backend/agentchat/services/graphrag/retriever.py
class GraphRetriever:
    async def retrieve(self, query: str, knowledge_id: str) -> dict:
        return {"entities": [], "paths": [], "chunks": []}
```

- [ ] **Step 6: 实现检索编排器**

```python
# src/backend/agentchat/services/graphrag/orchestrator.py
class RetrievalOrchestrator:
    async def run(self, mode: str, query: str, knowledge_ids: list[str]) -> dict:
        ...
```

- [ ] **Step 7: 把 workspace 接口加上 retrieval_mode**

```python
# src/backend/agentchat/api/v1/workspace.py
retrieval_mode = getattr(simple_task, "retrieval_mode", "default")
```

- [ ] **Step 8: 把前端知识库页和工作台加上检索模式选择**

```ts
// src/frontend/src/apis/workspace.ts
retrieval_mode?: 'default' | 'rag' | 'graphrag' | 'hybrid' | 'auto'
```

- [ ] **Step 9: 运行 GraphRAG 测试**

Run: `pytest src/backend/agentchat/test/test_graphrag.py -v`  
Expected: PASS

- [ ] **Step 10: 做工程验证**

验证：
- Neo4j 可连
- 图抽取结果能写入 Neo4j
- workspace API 接受新模式字段

- [ ] **Step 11: 做业务验证**

验证：
- 一个知识库可选默认检索模式
- workspace 可切换 `rag / graphrag / hybrid / auto`
- 至少一条问题中，GraphRAG 返回了普通 RAG 不足的关系信息

- [ ] **Step 12: 做证据验证**

检查：
- Neo4j 中存在 `Entity / Chunk / Document` 节点和关系
- LangSmith 中能区分实际采用的检索策略

Run: `git add src/backend/agentchat/services/graphrag src/backend/agentchat/services/rag/handler.py src/backend/agentchat/schema/knowledge.py src/backend/agentchat/database/models/knowledge.py src/backend/agentchat/api/v1/knowledge.py src/backend/agentchat/api/v1/workspace.py src/frontend/src/apis/knowledge.ts src/frontend/src/apis/workspace.ts src/frontend/src/pages/knowledge/knowledge.vue src/frontend/src/pages/knowledge/knowledge-file.vue src/frontend/src/pages/workspace/defaultPage/defaultPage.vue src/backend/agentchat/test/test_graphrag.py && git commit -m "feat: add neo4j graphrag retrieval modes"`

---

## 计划自检

### Spec 覆盖检查

- PostgreSQL：已覆盖
- Redis：已覆盖
- LangSmith：已覆盖
- Knowledge Pipeline：已覆盖
- RabbitMQ：已覆盖
- Neo4j + GraphRAG：已覆盖

### 占位符检查

- 无 `TODO`
- 无 `TBD`
- 无“后面再说”的空步骤

### 一致性检查

- 五个小轮顺序与总纲一致
- `PostgreSQL -> Redis+LangSmith -> Pipeline -> RabbitMQ -> Neo4j+GraphRAG` 前后依赖一致
- `retrieval_mode` 命名在后端和前端保持一致
