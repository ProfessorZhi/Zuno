# Local Model Default Cleanup Plan

Program: Model Registry & Eval Profile Hardening

Phase: M4 - Local DB Default Cleanup Plan

Scope: documentation only. This phase does not mutate the local database and
does not change runtime logic.

## Problem Statement

Current local PostgreSQL model registry state contains duplicate
`conversation_model` slot bindings:

- `MiniMax-M2.5`
- `qwen-plus`

This conflicts with the intended one-slot-one-default rule and makes default
conversation model resolution ambiguous for any runtime path that calls:

- `ModelManager.get_conversation_model()`
- `ModelManager.get_model_config("conversation_model", ...)`

## Why This Matters

Affected surfaces:

- Agent default chat model resolution
- shared answer-generation flows that fall back to default conversation model
- eval runners that do not pass explicit conversation-model settings
- any future rewrite / judge / answer flow that reuses the same slot

This is not just a UI inconsistency. It is a correctness and reproducibility
problem because the current DAO reads the first matching row without a stable
business rule.

## Cleanup Goal

Target steady state:

- exactly one active `conversation_model`
- keep all useful model rows
- do not delete `MiniMax-M2.5`
- do not commit any local database dump or ad-hoc SQL export

## Recommended Default Strategy

Recommended product/runtime defaults:

- default `conversation_model`: `qwen-plus`
- low-cost eval answer model: `deepseek-v4-flash`
- keep `MiniMax-M2.5` as optional selectable `LLM`, but not the active default
- text embedding: `text-embedding-v4`
- VL embedding: `qwen3-vl-embedding`
- rerank: `gte-rerank-v2`

Reasoning:

- `qwen-plus` already matches `config.example.yaml` default conversation config
- `deepseek-v4-flash` is a good explicit low-cost eval answer candidate
- text-only multihop eval does not need VL embedding
- embedding and rerank slots are already clean in current local state

## What To Change Locally

Recommended local cleanup action:

1. keep the `qwen-plus` row bound to `conversation_model`
2. remove `conversation_model` slot from `MiniMax-M2.5`
3. keep `deepseek-v4-flash` unbound unless a future explicit slot rule is added

This preserves all three `LLM` rows while restoring one clear default.

## Preferred Fix Path

Preferred order:

1. use existing admin/API slot activation flow where possible
2. if duplicate historical rows remain possible, add seed/reconcile hardening
3. only add a migration or dedicated cleanup action if API/seed flow cannot
   normalize old states safely

Why this order:

- repository truth should live in code paths and admin actions
- manual DB edits are easy to lose and hard to audit
- this repo already has `POST /api/v1/llm/activate` for slot changes

## Existing Entry Points

Current relevant code paths:

- activation API: `src/backend/zuno/api/v1/llm.py`
- activation service: `src/backend/zuno/api/services/llm.py`
- system seed/reconcile path: `src/backend/zuno/database/init_data.py`
- default slot reader: `src/backend/zuno/core/models/manager.py`

Current limitation:

- activation clears a slot before assigning a new model
- but historical duplicates can still exist already
- current seed/reconcile logic updates models by `(type, model)` identity, not by
  enforcing one unique row per slot

## Safe Follow-up Options

Option A: admin cleanup action without schema change

- list rows currently using `conversation_model`
- keep `qwen-plus` active
- clear slot from `MiniMax-M2.5`
- re-run checker:
  `python tools/scripts/check_model_registry_defaults.py`

Option B: seed/reconcile hardening

- extend system init reconcile logic to detect duplicate slot rows
- preserve the configured canonical slot model from `app_settings`
- clear the slot from non-canonical duplicates

Option C: schema-level hardening later

- add a stricter uniqueness rule or cleanup migration only after verifying it
  will not break user-owned custom model workflows

## What Not To Do

Do not:

- delete `MiniMax-M2.5`
- commit local PostgreSQL data files
- commit SQL dumps
- silently mutate the DB during docs-only or audit-only phases
- rely on "PostgreSQL usually returns rows in this order" as a default rule

## Eval Guidance

Until local default cleanup is completed, real multihop eval should prefer
explicit profile binding:

- retrieval baseline profile -> `qwen-plus`
- cheap answer-generation profile -> `deepseek-v4-flash`
- text embedding -> `text-embedding-v4`
- rerank -> `gte-rerank-v2`

Reference:

- `tools/evals/zuno/multihop_eval/eval_profiles.example.json`

## Verification

Use this checker before and after any future cleanup action:

```powershell
python tools/scripts/check_model_registry_defaults.py
```

Expected target result after cleanup:

- `conversation_model` count = 1
- `embedding` count >= 1
- `rerank` count >= 1
- script exit code = 0
