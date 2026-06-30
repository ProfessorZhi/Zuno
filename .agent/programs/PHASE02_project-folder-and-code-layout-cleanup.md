# PHASE02 Project Folder And Code Layout Cleanup

status: active

## 目标

先把项目文件夹、代码 ownership、compat/vendor 边界和本地缓存噪音整理清楚，再进入 runtime feature implementation。

## 关键判断

`src/backend/zuno` 顶层六层已经清楚，真正需要治理的是六层内部：`platform/services` 过胖、`capability/tools` 和 `capability/mcp/servers` 视觉上零碎、`platform/compatibility` 同时承载 alias 和 vendor、旧 import 仍通过 compatibility matrix 保护。

本 phase 的目标不是为了“看起来少几个文件”而移动代码，而是把 ownership 说清楚：业务语义代码应该回到自己的领域层，platform 只承载跨层基础设施，compatibility 只保留 legacy import registry 和迁移说明。任何移动都必须先证明 import matrix、legacy guards、repo verifier 和 focused tests 能保护旧路径；不能直接删除兼容层来换取视觉清爽。

目标收敛方向：

```text
src/backend/zuno/
  api/                         # FastAPI routes, DTO, session/task/artifact contracts
  agent/                       # Single Controller Runtime, state graph, planning, streaming
  memory/                      # context_builder, raw events, summaries, structured memory
  capability/                  # ToolCard registry, selector, policy, executors, MCP adapters
  knowledge/
    ingestion/                 # parser router, Document IR, chunk/provenance, parser golden tests
    retrieval/                 # basic RAG, sparse/dense/hybrid search
    graphrag/                  # entity/relation extraction, community reports, local/global/drift
    evidence/                  # evidence bundle, citation, grounding checks
  platform/
    model_gateway/             # local/API model provider boundary
    storage/                   # SQL, object, vector, graph, search provider adapters
    jobs/                      # ingest/embedding/index/artifact background jobs
    observability/             # OTel/LangSmith-compatible trace, metrics, eval export
    security/                  # policy, DLP, approval, sandbox, credentials
    vendor/                    # vendored shims only
    compatibility/             # legacy import registry only
```

## 步骤

- [ ] 生成 backend ownership matrix，覆盖 `api / agent / memory / capability / knowledge / platform`。
- [ ] 输出 `docs/architecture/repo-ownership-matrix.md`，列必须包含 `current_path`、`current_role`、`target_owner`、`target_path`、`compat_path`、`migration_risk`、`tests`、`verifier`、`status`。
- [ ] 为每个当前“零碎目录”标注 target owner、迁移理由、迁移风险、旧 import path 和测试覆盖。
- [ ] 清理未跟踪 `__pycache__`、`.pytest_cache` 和本地临时产物。
- [ ] 盘点 `platform/services` 中每个子目录的 target owner。
- [ ] 盘点 `capability/tools` 与 `capability/mcp/servers` 的 provider / builtin / compat 分类。
- [ ] 设计 `compat import registry` 与 `platform/vendor` 分离方案。
- [ ] 给 `knowledge/ingestion`、`platform/security`、`platform/observability` 预留 README 和 import guard，不提前搬运行时逻辑。
- [ ] 更新 `tools/scripts/verify_repo_structure.py` 和 repo tests，固定新目录规则。
- [ ] 增加 guard：禁止新增无 owner 的 `platform/services/*` 业务代码、禁止把 runtime code 放进 `platform/compatibility`、禁止 vendor shim 与 legacy alias registry 混写。

## 输入 / 输出文件

输入：

- `src/backend/zuno/**`
- `src/backend/zuno/*/README.md`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- `tests/repo/test_repo_structure_consistency.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`

输出：

- `docs/architecture/repo-ownership-matrix.md`
- 更新后的六层 README ownership 描述。
- 更新后的 repo structure verifier / repo tests。
- 可审计的 compat/vendor 分离方案。

## 依赖与阻塞

- 本 phase 是 PHASE03-PHASE10 的代码写入前置门。
- 在 ownership matrix 生成前，后续 phase 不应新增 runtime 目录或大规模移动文件。
- 任何兼容路径退役都必须先保留 old import path 的测试证据；不能为了视觉清爽直接删除。

## 验收

- 读者能从 README 和 ownership matrix 判断每个目录做什么。
- `platform/services` 不再是业务逻辑停车场；新代码能从目录名判断 domain owner。
- `capability` 内部按 ToolCard / policy / executor / MCP adapter 分层，而不是按 CLI/API 这种接入方式做顶层主分类。
- `platform/vendor` 与 `platform/compatibility` 分离：vendor 放第三方 shim，compatibility 放旧 import registry。
- 本地缓存不出现在 VS Code 项目树的结构判断中。
- 旧 import path 不被破坏。
- 新 runtime 代码不会继续写入 compatibility。
- 只有本 phase 的 verifier 和 legacy import tests 通过后，才允许把“代码布局治理”写入 Current；目标代码树在此之前仍是 Target。

## 验证

```powershell
git ls-files | rg "__pycache__|\\.pyc$"
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/repo/test_repo_structure_consistency.py tests/legacy_guards/test_zuno_alias_imports.py -p no:cacheprovider
```
