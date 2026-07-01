# Capability 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/capability/` 目前是 capability metadata、ToolCard retrieval、selector foundation、Tool Control Plane contract 和本地 deterministic tool runtime 的目标层入口，公开 CapabilityRecord、ToolCard、CapabilityRegistry、ToolCardRegistry、NativeBM25Retriever、DynamicCapabilitySelector、selection trace、ToolCardManifest、ExecutorRegistry、ApprovalGate、MCPTrustContract、ToolResultNormalizer、ToolControlPlaneRuntime、ToolRuntimeRequest、InMemoryCredentialBroker、SandboxPolicyEnforcer 和 NetworkPolicyDecision 等 surface。当前已提供 `contracts.py`、`registry.py`、`selector.py`、`policy.py`、`execution.py`、`trace.py`、`retrieval.py`、`control_plane.py` 和 `runtime.py`。真实 provider 实现仍在 `src/backend/zuno/platform/services/application/capabilities/` 和相关 registry 路径；当前 runtime 只证明本地可测 executor、approval gate、credential-ref-only broker、network policy decision、sandbox audit context 和 redacted approval ledger，不是生产级外部工具平台。

`capability/tools/` 不按 CLI / API 拆成两类顶层目录。CLI / API 是 execution adapter、runtime type 或 provider metadata，不是 capability 的主分类。

PHASE02 的 provider 分类入口是 `docs/architecture/repo-ownership-matrix.md` 和 `CAPABILITY_TOOL_PROVIDER_CLASSIFICATIONS` / `CAPABILITY_MCP_SERVER_CLASSIFICATIONS`。新增 tool 或 MCP server 目录前，必须先声明分类、target owner、compat path、测试和 verifier。

## Target role

目标状态下，Capability 层负责 ToolCard / capability metadata、权限、健康状态、成本提示、能力召回与 schema selection，并通过 Tool Control Plane runtime 管理 execution adapter、side-effect risk、approval、credential ref、sandbox context、MCP trust、result normalization 和 audit trace。它为 Agent 提供可选择且可治理的能力，不直接拥有具体工具 provider runtime 或 API response shape。

工具目录优先按能力语义和 owner 管理；CLI / API 只作为执行适配信息进入 ToolCard、manifest 或 runtime metadata。

当前分类只表达目录治理，不改变 runtime 行为：`builtin-provider`、`provider-adapter`、`model-provider-adapter`、`api-provider-adapter`、`executor-adapter`、`builtin-converter`、`builtin-domain-tool`、`mcp-provider`、`mcp-smoke-server` 和 `mcp-compat-proxy` 都仍归 Capability 层管理。

## 允许新增内容

- capability contract、selector trace、permission / health / cost 相关轻量类型。
- 不加载旧 provider、DB 或外部工具重型实现的 facade re-export；PHASE08 本地 runtime surface 必须保持无旧 provider 副作用。
- 指向旧 application capability owner 的边界说明。
- 本地 deterministic tool runtime、credential reference broker、network policy decision、sandbox context、redacted approval ledger 和 task event bridge。

## 禁止事项

- 禁止把生产级 ToolCard retrieval、optional vector capability search、完整 dynamic orchestration、rootless / gVisor / Firecracker sandbox、真实网络代理、外部 vault / OAuth credential broker 或生产级 MCP governance 写成已完成 Current。
- 禁止直接迁移或删除 `zuno.services.application.capabilities`、`zuno.services.capability_registry` 等旧 import path。
- 禁止改变工具权限、执行模式、API capability search response key 或 runtime tool wiring。
- 禁止把 `capability/tools/` 按 CLI / API 二分为顶层分类，除非后续有独立 ToolCard / execution adapter 迁移计划。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_capability_layer_surfaces.py`
- `tests/agent/test_capability_system.py`
- `tests/agent/test_capability_registry.py`
- `tests/agent/test_tool_control_plane_contract.py`
- `tests/agent/test_tool_control_plane_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`
