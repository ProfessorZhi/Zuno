# Model Registry And Defaults Audit

Program: Model Registry & Eval Profile Hardening

Phase: M1 - Model Registry Audit

Scope: audit only. No business logic, runtime routing, GraphRAG runtime, or
database state is modified in this phase.

## Evidence Sources

Audited files:

- `src/backend/zuno/api/services/llm.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/core/models/manager.py`
- `src/backend/zuno/database/dao/llm.py`
- `src/backend/zuno/database/init_data.py`
- `src/backend/zuno/database/models/llm.py`
- `src/backend/zuno/schema/knowledge.py`
- `src/backend/zuno/config.example.yaml`
- `apps/web/src/pages/model/model.vue`
- local PostgreSQL `llm` table state on 2026-06-20

## Short Verdict

The codebase formally supports three model types and four model slots:

- model types: `LLM`, `Embedding`, `Rerank`
- model slots: `conversation_model`, `embedding`, `vl_embedding`, `rerank`

Knowledge runtime model binding is explicit for knowledge-specific
`Embedding`/`VL Embedding`/`Rerank` through `knowledge_config.model_refs`.
General conversation model binding is still slot-based through
`ModelManager.get_model_config("conversation_model", ...)`.

The current local database state contains two `LLM` rows bound to
`conversation_model`. That breaks the intended one-slot-one-default rule and
makes default conversation model selection nondeterministic in practice because
the DAO reads `.first()` without an explicit order.

## 1. Current Supported Model Types

Formal model types in code:

- `LLM`
- `Embedding`
- `Rerank`

Evidence:

- `src/backend/zuno/api/services/llm.py` defines `LLM_Types = ["LLM", "Embedding", "Rerank"]`
- frontend model page only exposes those three types

There is no separate stored type for:

- answer LLM
- rewrite LLM
- extraction LLM
- community report LLM

Those remain runtime concepts or future config gaps, not first-class registry
types.

## 2. Current Supported Model Slots

Formal slot names in code:

- `conversation_model`
- `embedding`
- `vl_embedding`
- `rerank`

Evidence:

- `src/backend/zuno/api/services/llm.py` `MODEL_SLOTS`
- `src/backend/zuno/database/init_data.py` system seed model specs

Slot/type constraints:

- `conversation_model` -> `LLM`
- `embedding` -> `Embedding`
- `vl_embedding` -> `Embedding`
- `rerank` -> `Rerank`

The activation API enforces type compatibility, but database history can still
contain duplicate rows already using the same slot.

## 3. How Default Conversation Model Resolves

Default conversation model resolution path:

1. `ModelManager.get_conversation_model()`
2. `ModelManager.get_model_config("conversation_model", ...)`
3. `LLMDao.get_llm_by_slot("conversation_model")`
4. if a DB row exists, use that row
5. otherwise fall back to `app_settings.multi_models.conversation_model`

Important detail:

- `LLMDao.get_llm_by_slot()` calls `select(LLMTable).where(...).first()`
- there is no `ORDER BY`
- no uniqueness constraint is enforced at DAO level

So if multiple rows share `conversation_model`, the chosen row is effectively
"first row returned by the database", not a deterministic product rule.

## 4. How Default Embedding Resolves

There are two different paths:

Knowledge-specific embedding:

- knowledge runtime does not use the `embedding` slot directly
- it uses `KnowledgeService.resolve_model_config_by_id(text_embedding_model_id)`
- if `text_embedding_model_id` is missing, knowledge runtime returns `None`

General fallback embedding:

- `ModelManager.get_embedding_model()`
- `ModelManager.get_model_config("embedding", ...)`
- DB slot first, then `app_settings.multi_models.embedding`

Conclusion:

- Agent/global embedding default is slot-based
- Knowledge embedding default is explicit-id-based, not slot-based

## 5. How Default Rerank Resolves

Knowledge rerank resolution is explicit-id-based:

- `KnowledgeService.resolve_model_config_by_id(rerank_model_id)`

Global/system rerank seed exists through config and DB seeding, but current
knowledge runtime does not auto-resolve rerank by slot if id is absent.

Conclusion:

- current knowledge rerank is explicit-id-based
- slot `rerank` mainly acts as system default/registry metadata, not as a strong
  knowledge fallback rule

## 6. What Happens If Multiple Models Bind The Same Slot

Current behavior depends on the consumer:

For `conversation_model` and `embedding` slot readers through `ModelManager`:

- DAO returns `.first()`
- no explicit ordering
- selected model is not guaranteed by business rule

For knowledge-specific model refs:

- no ambiguity if the stored `llm_id` points to one row
- ambiguity only appears if the caller intentionally falls back to slot-based
  runtime code somewhere else

So duplicate slot rows are not blocked by runtime read logic. They are only
partially discouraged by the activation API, which clears a slot before setting
a new one. Historical duplicates can still remain.

## 7. Is There Nondeterministic Default Selection?

Yes.

Current local DB state shows:

- `MiniMax-M2.5` -> `conversation_model`
- `qwen-plus` -> `conversation_model`

Because `LLMDao.get_llm_by_slot("conversation_model")` has no `ORDER BY` and no
uniqueness guarantee, default conversation model selection is nondeterministic
at code-contract level.

Even if PostgreSQL often returns rows in a stable order on one machine, the code
does not define that behavior. So this should be treated as a real correctness
risk, not a cosmetic issue.

## 8. Which Models Are Used For Agent Runtime

Agent/default chat runtime uses `LLM`:

- default path: `ModelManager.get_conversation_model()`
- per-agent override path: user-selected `llm_id` on agent config, then
  `ModelManager.get_user_model(**model_config)`

Implication:

- agent runtime can avoid the ambiguous default slot if the agent binds an
  explicit `llm_id`
- agent runtime remains at risk when relying on default `conversation_model`

## 9. Which Models Are Used For Knowledge Runtime

Knowledge runtime currently binds:

- text embedding -> `knowledge_config.model_refs.text_embedding_model_id`
- VL embedding -> `knowledge_config.model_refs.vl_embedding_model_id`
- rerank -> `knowledge_config.model_refs.rerank_model_id`

Knowledge runtime does not currently expose or bind:

- explicit answer-generation model
- explicit rewrite model
- explicit extraction model
- explicit community report model

So knowledge retrieval quality for eval can still be influenced by implicit
conversation-model defaults outside the formal `KnowledgeConfig` surface.

## 10. Which Models Are Used For Multihop Eval

Current multihop-preparation eval assets rely on a mix of:

- explicit embedding/rerank ids when passed to local eval scripts
- profile-level retrieval settings in eval code
- default conversation model when answer-generation or rewrite flows use shared
  runtime defaults

That means multihop eval is not yet fully protected from ambiguous
`conversation_model` defaults unless the runner or profile passes explicit model
choices.

Recommendation:

- future real multihop eval should always use an explicit eval profile that names
  `conversation_model`, `text_embedding_model`, and `rerank_model`

## 11. Current Local Database State

Observed local registry rows on 2026-06-20:

- `MiniMax-M2.5` (`LLM`, `MiniMax`) -> `conversation_model`
- `qwen-plus` (`LLM`, `通义千问`) -> `conversation_model`
- `deepseek-v4-flash` (`LLM`, `DeepSeek`) -> no slot
- `text-embedding-v4` (`Embedding`, `通义千问`) -> `embedding`
- `qwen3-vl-embedding` (`Embedding`, `通义千问`) -> `vl_embedding`
- `gte-rerank-v2` (`Rerank`, `通义千问`) -> `rerank`

Local-state conclusion:

- duplicate `conversation_model` exists
- `embedding` slot is clean
- `vl_embedding` slot is clean
- `rerank` slot is clean

## 12. Does The Current DB State Need A Fix?

Yes, but not through direct manual DB edits committed into the repository.

Recommended fix target:

- keep all model rows
- reduce `conversation_model` active default to exactly one row
- prefer an admin/API/seed-driven cleanup path over raw SQL hand edits

## 13. Should This Be Fixed By Migration, Seed, Or Admin API?

Recommended order:

1. admin/API action if available
2. seed/reconcile logic improvement if duplicates can be created during init
3. migration or dedicated cleanup action if historical duplicates must be
   normalized automatically

Why:

- runtime truth should stay in code paths, not hidden local SQL operations
- this repository already has a formal activation API for slots
- `database.init_data.insert_llm_to_mysql()` is already a seed/reconcile path

What not to do:

- do not commit local database dumps
- do not "fix" this by deleting model rows from the repository

## 14. Recommended Next Steps

Immediate next actions for hardening:

1. add a read-only checker script for slot/default health
2. add explicit multihop eval profile examples using model names, not DB ids
3. document a safe local cleanup plan for `conversation_model`

Not part of this phase:

- no GraphRAG runtime changes
- no real multihop dataset download
- no live DB mutation
