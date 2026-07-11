# PHASE01 Baseline Manifest

本文件是 `zuno-unified-agent-runtime-closure-v1` 的 PHASE01 事实源。它冻结的是 program 启动时的 runtime baseline，不表示 unified runtime 已完成。

```json
{
  "schema_version": 1,
  "program": "zuno-unified-agent-runtime-closure-v1",
  "phase": "PHASE01_truth-source-baseline-and-program-activation",
  "phase_status": "completed",
  "phase_start_commit": "04bf52ed554d8391d7b76203b364beacdecea064",
  "phase_start_branch": "codex/zuno-truth-source-production-readiness-baseline",
  "runtime_modification_scope": "none",
  "measurement_status": "baseline_frozen_not_measured",
  "blocked_reason": "fixed_enterprise_rag_agentic_profile_not_measured_in_phase01",
  "truth_semantics": {
    "measured": "Only a complete fixed paired benchmark profile can be measured.",
    "runtime_observed": "A real run produced trace, but not benchmark quality evidence.",
    "prepared": "Data, config, or contract exists without a complete runtime run.",
    "blocked": "A required runtime, provider, dataset, or trace field is unavailable."
  },
  "product_entrypoints": [
    {
      "name": "completion_http_route",
      "path": "src/backend/zuno/api/v1/completion.py",
      "symbol": "completion",
      "status": "current_product_entrypoint",
      "notes": "Creates GeneralAgent through the completion path and streams SSE chunks."
    },
    {
      "name": "completion_service_agent_factory",
      "path": "src/backend/zuno/api/services/completion.py",
      "symbol": "CompletionService.create_chat_agent",
      "status": "current_product_entrypoint",
      "notes": "Creates and initializes GeneralAgent from dialog config."
    },
    {
      "name": "workspace_task_runtime",
      "path": "src/backend/zuno/api/services/workspace_task_runtime.py",
      "symbol": "WorkspaceTaskRuntimeService",
      "status": "current_product_surface_partial",
      "notes": "Owns workspace task, planner output, durable runtime facade, tool runtime, retrieval runtime, trace and artifacts."
    }
  ],
  "agent_runtimes": [
    {
      "name": "general_agent_react",
      "path": "src/backend/zuno/agent/core/agents/general_agent.py",
      "symbols": ["GeneralAgent", "GeneralAgent.init_agent", "GeneralAgent.astream"],
      "status": "current_real_react_entrypoint",
      "notes": "Uses LangChain create_agent, ModelManager, KnowledgeQueryService, MemoryEngine, tools, MCP and skills."
    },
    {
      "name": "strategy_selector",
      "path": "src/backend/zuno/agent/planning.py",
      "symbols": ["StrategySelector", "PlanningRequest"],
      "status": "current_rule_baseline",
      "notes": "Builds StrategySelectorOutput, RetrievalPlan, CapabilityPlan, PlanState, ReflectionVerdict, ReplanDecision and ReflexionLesson."
    },
    {
      "name": "agent_control_runtime",
      "path": "src/backend/zuno/agent/control_runtime.py",
      "symbols": ["AgentControlRuntime", "RuntimeObservation"],
      "status": "current_rule_baseline",
      "notes": "Runs handcrafted observation/reflection/replan/reflexion baseline; not the unified product loop."
    },
    {
      "name": "single_controller_durable_runtime",
      "path": "src/backend/zuno/agent/durable_runtime.py",
      "symbols": ["SingleControllerDurableRuntime", "InMemoryDurableRuntimeStore"],
      "status": "current_deterministic_baseline",
      "notes": "In-memory checkpoint, interrupt, resume and cancel state machine. act_react_loop still records simulated marker, so it is not a completed unified runtime."
    }
  ],
  "subsystem_baselines": [
    {
      "name": "memory_engine",
      "path": "src/backend/zuno/memory/engine.py",
      "status": "current_partial",
      "notes": "MemoryEngine and ContextPack surfaces exist; full AgentChat lifecycle reuse remains a closure gap."
    },
    {
      "name": "tool_control_plane",
      "path": "src/backend/zuno/capability/control_plane.py",
      "status": "current_partial",
      "notes": "Tool policy, approval, credential-ref and normalized result surfaces exist; unified runtime integration remains later phase work."
    },
    {
      "name": "agentic_graphrag",
      "path": "src/backend/zuno/knowledge/agentic_graphrag.py",
      "status": "implementation_available_measurement_blocked",
      "notes": "Retrieval, evidence and citation baseline exists; fixed paired agentic measured pass is not complete."
    },
    {
      "name": "model_gateway",
      "path": "src/backend/zuno/platform/model_gateway.py",
      "status": "target_gateway_surface_exists",
      "notes": "Gateway contract exists, but legacy direct ModelManager and SDK surfaces remain."
    }
  ],
  "model_call_inventory": [
    {
      "path": "src/backend/zuno/agent/core/agents/general_agent.py",
      "symbols": ["ModelManager.get_user_model", "ModelManager.get_conversation_model"],
      "owner": "legacy_model_manager",
      "status": "legacy_direct_model_path_to_close_in_PHASE03"
    },
    {
      "path": "src/backend/zuno/agent/core/models/manager.py",
      "symbols": ["ModelManager", "ChatOpenAI"],
      "owner": "legacy_model_manager",
      "status": "legacy_direct_model_path_to_close_in_PHASE03"
    },
    {
      "path": "src/backend/zuno/agent/core/models/usage_model.py",
      "symbols": ["OpenAI", "AsyncOpenAI"],
      "owner": "legacy_openai_compatible_usage_model",
      "status": "legacy_direct_sdk_surface"
    },
    {
      "path": "src/backend/zuno/agent/core/models/reason_model.py",
      "symbols": ["AsyncOpenAI"],
      "owner": "legacy_openai_compatible_reason_model",
      "status": "legacy_direct_sdk_surface"
    },
    {
      "path": "src/backend/zuno/agent/core/models/tool_call.py",
      "symbols": ["AsyncOpenAI"],
      "owner": "legacy_openai_compatible_tool_call_model",
      "status": "legacy_direct_sdk_surface"
    },
    {
      "path": "src/backend/zuno/agent/core/models/embedding.py",
      "symbols": ["OpenAI"],
      "owner": "legacy_embedding_model",
      "status": "legacy_direct_sdk_surface"
    },
    {
      "path": "src/backend/zuno/agent/core/models/anthropic.py",
      "symbols": ["Anthropic", "AsyncAnthropic"],
      "owner": "legacy_anthropic_model",
      "status": "legacy_direct_sdk_surface"
    },
    {
      "path": "src/backend/zuno/api/services/mcp_chat.py",
      "symbols": ["DeepAsyncAnthropic"],
      "owner": "legacy_mcp_chat_model",
      "status": "legacy_direct_model_path"
    },
    {
      "path": "tools/evals/zuno/rag_eval/run_eval.py",
      "symbols": ["ModelManager.get_conversation_model"],
      "owner": "eval_legacy_model_manager",
      "status": "eval_runner_legacy_model_path"
    }
  ],
  "benchmark_truth_source": {
    "enterprise_rag_runner": "tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py",
    "enterprise_rag_dataset_adapter": "tools/evals/zuno/rag_eval/public_enterprise_datasets.py",
    "enterprise_rag_readme": "tools/evals/zuno/rag_eval/README.md",
    "enterprise_rag_required_raw_questions": ".local/evals/raw/enterprise_rag_bench/hf/data/questions/test.parquet",
    "enterprise_rag_required_raw_documents": ".local/evals/raw/enterprise_rag_bench/hf/data/documents/test.parquet",
    "release_gate_owner": "tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py::_build_release_gate",
    "failure_cases_owner": "tools/evals/zuno/rag_eval/run_enterprise_rag_paired_benchmark.py::_write_failure_cases",
    "status": "truth_source_identified_measurement_not_run_in_PHASE01"
  },
  "sample_case_sets": {
    "sample_8": {
      "dataset_path": "tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl",
      "case_ids": [
        "mrv1_keyword_trace_header",
        "mrv1_keyword_response_trace_header",
        "mrv1_semantic_runtime_split",
        "mrv1_semantic_graph_entry_policy",
        "mrv1_crossdoc_deploy_components",
        "mrv1_crossdoc_standard_vs_graph",
        "mrv1_graph_atlas_team",
        "mrv1_graph_clientnova_sre"
      ],
      "coverage": ["exact_lookup", "semantic_fact", "cross_doc_summary", "graph_relation", "citation_required"],
      "status": "tracked_regression_sample_ready"
    },
    "sample_80": {
      "dataset_path": null,
      "case_ids": [],
      "status": "blocked",
      "blocked_reason": "no_tracked_fixed_80_case_enterprise_rag_set_available_in_repo; local .local runs are not committed truth source"
    }
  },
  "fixed_dataset_candidates": [
    {
      "path": "tools/evals/zuno/rag_eval/datasets/mixed_realistic_v1_eval.jsonl",
      "case_count": 16,
      "status": "tracked_small_regression"
    },
    {
      "path": "tools/evals/zuno/rag_eval/datasets/graphrag_focus_eval.jsonl",
      "case_count": 4,
      "status": "tracked_graph_focus_regression"
    },
    {
      "path": "tools/evals/zuno/rag_eval/datasets/contract_review_graph_relation_small.jsonl",
      "case_count": 12,
      "status": "tracked_contract_graph_regression"
    }
  ],
  "phase01_regression_commands": [
    "python .agent/scripts/verify_agent_system.py",
    "powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1",
    "python tools/scripts/verify_docs_entrypoints.py",
    "python -m pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider",
    "python -m pytest -q tests/repo/test_current_program_contract.py -p no:cacheprovider",
    "git diff --check"
  ],
  "next_phase": "PHASE02_unified-runtime-contracts-and-state",
  "phase01_closure": {
    "status": "completed",
    "runtime_code_modified": false,
    "benchmark_measured": false,
    "quality_gate_changed": false
  }
}
```
