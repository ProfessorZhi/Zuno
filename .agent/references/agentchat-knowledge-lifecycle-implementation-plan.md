# AgentChat 知识库生命周期对齐执行计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or the repo's local TDD workflow. Steps use checkbox syntax for tracking.

**Goal:** 让 AgentChat、知识库初始化配置、后续配置修改和文件增删改共享同一套 `standard / deep` 产品契约。

**Architecture:** 前端保留旧知识库内部配置 `rag / rag_graph`，新增显式映射到 Workspace `standard / deep`。聊天任务 payload 以 `knowledge_space_profiles` 为主，旧 `retrieval_mode` 只作为兼容字段。

**Tech Stack:** Vue 3 + TypeScript frontend, FastAPI/Pydantic backend DTO, pytest static contract tests.

---

### Task 1: 前端契约测试

**Files:**

- Modify: `tests/api/test_workspace_agentic_product_contract.py`
- Read: `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- Read: `apps/web/src/pages/knowledge/knowledge-create.vue`
- Read: `apps/web/src/utils/knowledge-config.ts`

- [x] **Step 1: Write the failing test**

Add a test that checks:

```python
def test_frontend_agentchat_sends_explicit_product_profiles_from_selected_knowledge() -> None:
    root = Path(__file__).resolve().parents[2]
    workspace_page = (root / "apps/web/src/pages/workspace/defaultPage/defaultPage.vue").read_text(
        encoding="utf-8"
    )
    create_page = (root / "apps/web/src/pages/knowledge/knowledge-create.vue").read_text(
        encoding="utf-8"
    )
    config_utils = (root / "apps/web/src/utils/knowledge-config.ts").read_text(encoding="utf-8")

    assert "toWorkspaceRetrievalProfile" in config_utils
    assert "buildKnowledgeSpaceProfileSelections" in workspace_page
    assert "knowledge_space_ids:" in workspace_page
    assert "knowledge_space_profiles:" in workspace_page
    assert "retrieval_profiles:" in workspace_page
    assert "KnowledgeProductMode = 'standard' | 'deep'" in config_utils
    assert "value: 'enhanced'" not in create_page
```

- [x] **Step 2: Run test to verify it fails**

Run:

```powershell
pytest -q tests/api/test_workspace_agentic_product_contract.py::test_frontend_agentchat_sends_explicit_product_profiles_from_selected_knowledge -p no:cacheprovider
```

Expected: fail because mapping helpers and explicit payload are not present yet.

### Task 2: Product profile mapping helper

**Files:**

- Modify: `apps/web/src/utils/knowledge-config.ts`

- [x] **Step 1: Implement minimal helper**

Add:

```ts
export type KnowledgeProductMode = 'standard' | 'deep'
export type LegacyKnowledgeProductMode = KnowledgeProductMode | 'enhanced'
export type WorkspaceRetrievalProductProfile = 'standard' | 'deep'

export const toWorkspaceRetrievalProfile = (
  configInput?: LegacyKnowledgeConfigInput | null,
): WorkspaceRetrievalProductProfile => {
  const rawDefaultMode = String(configInput?.retrieval_settings?.default_mode || '').trim().toLowerCase()
  if (['deep', 'rag_graph', 'graphrag', 'hybrid'].includes(rawDefaultMode)) return 'deep'
  if (['standard', 'rag', 'auto', 'default'].includes(rawDefaultMode)) return 'standard'

  const config = normalizeKnowledgeConfig(configInput)
  return config.index_capability === 'rag_graph' ? 'deep' : 'standard'
}
```

Keep `toProductKnowledgeConfig` accepting `'enhanced'` as legacy input but prefer `'deep'`.

- [x] **Step 2: Run focused test**

Run the same pytest test. Expected: still fail on workspace page explicit payload.

### Task 3: AgentChat payload alignment

**Files:**

- Modify: `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`

- [x] **Step 1: Import helper**

Import `toWorkspaceRetrievalProfile` from `../../../utils/knowledge-config`.

- [x] **Step 2: Add selection builders**

Add:

```ts
const buildKnowledgeSpaceProfileSelections = (knowledgeIds: string[]): KnowledgeSpaceRetrievalSelection[] => {
  const profile: WorkspaceRetrievalProfile = effectiveWorkspaceRetrievalProfile.value
  return knowledgeIds.map((knowledgeSpaceId) => ({
    knowledge_space_id: knowledgeSpaceId,
    retrieval_profile: profile,
  }))
}

const buildRetrievalProfileMap = (knowledgeIds: string[]): Record<string, WorkspaceRetrievalProfile> => {
  const profile: WorkspaceRetrievalProfile = effectiveWorkspaceRetrievalProfile.value
  return Object.fromEntries(knowledgeIds.map((knowledgeSpaceId) => [knowledgeSpaceId, profile]))
}
```

- [x] **Step 3: Send explicit profiles**

Change `buildPayload` so selected knowledge IDs populate:

```ts
knowledge_space_ids: selectedKnowledgeSpaceIds,
knowledge_space_profiles: buildKnowledgeSpaceProfileSelections(selectedKnowledgeSpaceIds),
retrieval_profiles: buildRetrievalProfileMap(selectedKnowledgeSpaceIds),
```

Runtime attachment-created knowledge spaces should use the same helpers for `registered.map((item) => item.knowledgeSpaceId)`.

- [x] **Step 4: Run focused test**

Run:

```powershell
pytest -q tests/api/test_workspace_agentic_product_contract.py::test_frontend_agentchat_sends_explicit_product_profiles_from_selected_knowledge -p no:cacheprovider
```

Expected: still fail until create page mode is renamed.

### Task 4: Knowledge create page wording and enum

**Files:**

- Modify: `apps/web/src/pages/knowledge/knowledge-create.vue`

- [x] **Step 1: Rename product mode**

Change `value: 'enhanced'` to `value: 'deep'`, title to `深度检索`, and all `productMode.value === 'enhanced'` checks to `productMode.value === 'deep'`.

- [x] **Step 2: Run focused test**

Run:

```powershell
pytest -q tests/api/test_workspace_agentic_product_contract.py::test_frontend_agentchat_sends_explicit_product_profiles_from_selected_knowledge -p no:cacheprovider
```

Expected: pass.

### Task 5: Verification

**Files:**

- Verify only.

- [x] **Step 1: Run API/product contract tests**

```powershell
pytest -q tests/api/test_workspace_agentic_product_contract.py -p no:cacheprovider
```

- [x] **Step 2: Run repo/document guardrails**

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

- [x] **Step 3: Run frontend typecheck**

```powershell
npm --prefix apps/web run lint
```

If this fails because dependencies are missing, record the exact failure and do not claim frontend typecheck passed.

Result: command executed, but local frontend typecheck was blocked because `node_modules/vue-tsc/bin/vue-tsc.js` is missing from the repository root.
