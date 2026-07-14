# Canonical Directory Contract

program: zuno-canonical-architecture-runtime-realization-v1
status: mandatory-closure-contract
owner: Repository Governance

## 1. 目标

Program 完成后，仓库只保留十一模块新架构对应的清晰物理目录。迁移期的 Alias、Compatibility Bridge、Feature Flag、Dual Read/Write 和旧入口必须在 PHASE22 删除。

以下规则不允许因兼容、Token、工期或测试困难而降低：

```text
生产源码零 legacy 目录
生产源码零 legacy_* / *_legacy 文件
零 legacy alias registry
零永久旧 Runtime 主路径
零永久双写/双读
零无期限 Feature Flag
零第二套领域 Owner
```

`docs/history/**` 中的历史档案不受名称限制，因为它们不是生产源码或活跃执行路径。

## 2. 后端顶层六根

`src/backend/zuno/` 只保留：

```text
api/
agent/
memory/
capability/
knowledge/
platform/
```

不得新增十一模块同名顶层目录，也不得恢复旧 `core/`、`services/`、`schema/`、`database/`、`tools/` 等根级兼容包。

## 3. Canonical Target Tree

```text
src/backend/zuno/
├── api/
│   ├── product/
│   │   ├── routes/
│   │   ├── dto/
│   │   └── dependencies/
│   ├── services/product/
│   └── projection/
│
├── agent/
│   ├── domain/
│   │   ├── run/
│   │   ├── task/
│   │   ├── plan/
│   │   ├── step/
│   │   ├── action/
│   │   ├── control/
│   │   └── finalization/
│   ├── application/
│   │   ├── controller/
│   │   ├── planning/
│   │   ├── execution/
│   │   ├── recovery/
│   │   └── finalization/
│   ├── runtime/
│   │   ├── agent_run_graph/
│   │   ├── step_execution_graph/
│   │   ├── nodes/
│   │   ├── reducers/
│   │   └── routing/
│   └── ports/
│
├── memory/
│   ├── domain/
│   ├── application/
│   ├── policy/
│   ├── retrieval/
│   ├── rendering/
│   ├── ports/
│   └── adapters/
│
├── capability/
│   ├── domain/
│   ├── application/
│   ├── registry/
│   ├── projection/
│   ├── ports/
│   └── tool_runtime/
│       ├── domain/
│       ├── application/
│       ├── ports/
│       ├── adapters/
│       └── projection/
│
├── knowledge/
│   ├── ingestion/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── ports/
│   │   ├── adapters/
│   │   └── workers/
│   ├── domain/
│   ├── application/
│   ├── index/
│   ├── retrieval/
│   ├── graph/
│   ├── evidence/
│   ├── ports/
│   └── adapters/
│
└── platform/
    ├── contracts/
    ├── config/
    ├── database/
    │   ├── agent/
    │   ├── product/
    │   ├── ingestion/
    │   ├── knowledge/
    │   ├── memory/
    │   ├── capability/
    │   ├── tool_runtime/
    │   ├── security/
    │   └── observability/
    ├── model_gateway/
    ├── security/
    ├── observability/
    ├── storage/
    ├── queue/
    ├── checkpoint/
    ├── resources/
    └── vendor/
```

目录可以根据模块文档增加正常命名的子包，但不得改变 Owner 或重新引入旧根。

## 4. Product Client Tree

```text
apps/web/src/product/
├── api/
├── contracts/
├── stores/
├── projections/
├── streaming/
├── components/
└── pages/

apps/desktop/src/product/
├── bridge/
├── contracts/
├── authorization/
└── delivery/
```

Program 关闭时，旧 API Client、旧 Pinia Store、旧 SSE Handler、单一 pending approval 模型和旧 Desktop Bridge 必须删除。不得保留 `legacy/` 或永久 `compatibility/` 前端目录。

## 5. 外部版本兼容

确有外部客户端兼容要求时，只允许使用正常的版本化 Adapter：

```text
api/product/v1/
api/product/v2/
adapters/versioned/v1_to_v2.py
```

规则：

- Adapter 只转换 Transport Contract；
- 不拥有领域状态；
- 不绕过 Security、Audit、Budget 或 Final Gate；
- 不调用旧 Runtime；
- 版本支持期、Owner 和 Sunset Policy 明确；
- 名称不得包含 legacy；
- 内部代码只依赖当前 Canonical Contract。

## 6. 禁止路径

Program 完成时，以下路径或模式必须不存在于生产源码：

```text
src/backend/zuno/platform/compatibility/legacy_aliases.py
src/backend/zuno/**/legacy/
src/backend/zuno/**/legacy_*.py
src/backend/zuno/**/*_legacy.py
apps/web/src/**/legacy/
apps/desktop/src/**/legacy/
tests/legacy_guards/
```

如果 `platform/compatibility/` 只为 Alias 存在，整个目录删除。若仍有与旧架构无关的协议兼容能力，迁移到对应 Owner 的 `adapters/versioned/` 并删除 compatibility 目录。

## 7. Import 和依赖方向

```text
API → Application Port
Application → Domain / Outbound Port
Adapter → Outbound Port implementation
Domain → 不依赖 FastAPI、Vue、LangGraph、Provider SDK、ORM、OTel
Agent → 不反向依赖 API
Module → 不直接写其他 Owner Repository
Frontend → 只依赖 Product Contract / Projection
```

禁止通过 Alias、动态 Import、Monkey Patch 或 re-export 隐藏逆向依赖。

## 8. 迁移期例外

临时兼容代码必须同时满足：

```text
registered_in_cutover_matrix = true
owner != null
removal_task = P22-T03
expires_at != null
default_path = canonical_new
new_calls_forbidden = true
```

任何条件缺失，CI 失败。

## 9. Closure Guard

PHASE22 必须新增/更新机器验证，扫描以下生产根：

```text
src/backend/zuno
apps/web/src
apps/desktop/src
```

验证：

1. 路径名无 `legacy`。
2. 不存在 `legacy_aliases.py`。
3. 不存在从旧 root alias 导入。
4. 不存在旧 Runtime Feature Flag 分支。
5. 不存在旧/新双写和旧 Store 读回退。
6. 不存在 Tool/Model/RAG 直接旁路。
7. Canonical Tree 的 Owner 和依赖方向满足静态规则。

未通过任一项，Program 不得归档。
