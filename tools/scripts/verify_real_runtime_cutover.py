from __future__ import annotations

import argparse
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

SERVICE = REPO_ROOT / "src/backend/zuno/agent/runtime/service.py"
MODEL_STEP = REPO_ROOT / "src/backend/zuno/agent/runtime/execution/model_step.py"
REACT_STEP = REPO_ROOT / "src/backend/zuno/agent/runtime/execution/react_step.py"
KNOWLEDGE_STEP = REPO_ROOT / "src/backend/zuno/agent/runtime/execution/knowledge_step.py"
COMPLETION_SERVICE = REPO_ROOT / "src/backend/zuno/api/services/completion.py"
COMPLETION_ROUTE = REPO_ROOT / "src/backend/zuno/api/v1/completion.py"
CURRENT = REPO_ROOT / ".agent/programs/current.md"
PHASE01 = REPO_ROOT / ".agent/programs/PHASE01_real-runtime-baseline.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _contains(path: Path, phrase: str) -> bool:
    return phrase in _read(path)


def verify_phase01_baseline() -> list[str]:
    errors: list[str] = []
    current = _read(CURRENT)
    phase01 = _read(PHASE01)
    for phrase in [
        "state: active",
        "active_program: zuno-real-unified-runtime-cutover-v1",
        "current_phase: PHASE01_real-runtime-baseline",
    ]:
        if phrase not in current:
            errors.append(f"current.md missing active phrase: {phrase}")
    for phrase in [
        "runtime_code_modified: false",
        "measurement_status: baseline_frozen_not_measured",
        "_run_from()",
        "Unified runtime completed.",
        "synthetic `evidence:<run>:<step>`",
    ]:
        if phrase not in phase01:
            errors.append(f"PHASE01 baseline missing frozen fact: {phrase}")

    expected_current_gaps = {
        "manual service loop": (SERVICE, "while current_node != RuntimeNode.END"),
        "start uses _run_from": (SERVICE, "final_state = self._run_from(state, RuntimeNode.INPUT_GATE)"),
        "resume forces PASS": (SERVICE, "reflection_decision=ReflectionDecision.PASS"),
        "model step deterministic": (MODEL_STEP, "del deps"),
        "react step deterministic": (REACT_STEP, "single ReAct step completed"),
        "knowledge synthetic evidence": (KNOWLEDGE_STEP, 'evidence_ids=[f"evidence:{state.run_id}:{step.step_id}"]'),
        "completion canned answer": (COMPLETION_SERVICE, '"Unified runtime completed."'),
        "completion opt-in unified runtime": (COMPLETION_ROUTE, 'req.product_mode == "unified_runtime"'),
        "general agent default path": (COMPLETION_ROUTE, "chat_agent, agent_config = await _create_chat_agent"),
    }
    for label, (path, phrase) in expected_current_gaps.items():
        if not _contains(path, phrase):
            errors.append(f"PHASE01 expected current gap not detected: {label}")
    return errors


def verify_enforce_langgraph() -> list[str]:
    errors: list[str] = []
    service = _read(SERVICE)
    if "while current_node != RuntimeNode.END" in service:
        errors.append("UnifiedAgentRuntimeService still contains manual runtime while loop")
    if "final_state = self._run_from(state, RuntimeNode.INPUT_GATE)" in service:
        errors.append("UnifiedAgentRuntimeService.start still calls _run_from instead of compiled graph")
    if "reflection_decision=ReflectionDecision.PASS" in service:
        errors.append("UnifiedAgentRuntimeService.resume still forces ReflectionDecision.PASS")
    if not any(token in service for token in [".ainvoke(", ".invoke(", ".astream(", ".astream_events("]):
        errors.append("UnifiedAgentRuntimeService does not call compiled graph invoke/stream")
    return errors


def verify_enforce_dependencies() -> list[str]:
    errors: list[str] = []
    for relative_path in [
        "src/backend/zuno/agent/runtime/factory.py",
        "src/backend/zuno/agent/runtime/protocols.py",
    ]:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing runtime dependency factory file: {relative_path}")
    deps_path = REPO_ROOT / "src/backend/zuno/agent/runtime/dependencies.py"
    if deps_path.exists() and "Any | None" in _read(deps_path):
        errors.append("RuntimeDependencies still uses Any | None for core dependencies")
    return errors


def verify_enforce_real_execution() -> list[str]:
    errors: list[str] = []
    if "model_gateway" not in _read(MODEL_STEP):
        errors.append("ModelStepExecutor does not reference model_gateway")
    if "del deps" in _read(MODEL_STEP):
        errors.append("ModelStepExecutor still discards dependencies")
    react_text = _read(REACT_STEP)
    if "create_agent" not in react_text and "react_runner" not in react_text:
        errors.append("ReActStepExecutor does not call a real ReAct runner")
    if "single ReAct step completed" in react_text:
        errors.append("ReActStepExecutor still returns deterministic completed observation")
    grounded = REPO_ROOT / "src/backend/zuno/agent/runtime/synthesis/grounded_answer.py"
    grounded_text = _read(grounded) if grounded.exists() else ""
    for phrase in ["final_answer", "unsupported", "citation"]:
        if phrase not in grounded_text:
            errors.append(f"Grounded synthesis missing {phrase}")
    return errors


def verify_enforce_knowledge_tool_memory() -> list[str]:
    errors: list[str] = []
    knowledge_text = _read(KNOWLEDGE_STEP)
    if 'evidence_ids=[f"evidence:{state.run_id}:{step.step_id}"]' in knowledge_text:
        errors.append("KnowledgeStepExecutor still fabricates synthetic evidence when runtime is missing")
    if 'citation_ids=[f"citation:{state.run_id}:{step.step_id}"]' in knowledge_text:
        errors.append("KnowledgeStepExecutor still fabricates synthetic citations when runtime is missing")
    for tool_name in ["filesystem.read", "filesystem.write"]:
        if tool_name not in "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in (REPO_ROOT / "src/backend/zuno/capability").rglob("*.py")):
            errors.append(f"missing real tool registration: {tool_name}")
    return errors


def verify_enforce_product_cutover() -> list[str]:
    errors: list[str] = []
    completion_route = _read(COMPLETION_ROUTE)
    completion_service = _read(COMPLETION_SERVICE)
    if 'req.product_mode == "unified_runtime"' in completion_route:
        errors.append("Completion still requires product_mode unified_runtime opt-in")
    if '"Unified runtime completed."' in completion_service:
        errors.append("Completion still emits canned unified runtime completion text")
    if "legacy_general_agent" not in completion_route + completion_service:
        errors.append("Completion cutover missing explicit legacy_general_agent rollback flag")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--enforce-langgraph", action="store_true")
    parser.add_argument("--enforce-dependencies", action="store_true")
    parser.add_argument("--enforce-real-execution", action="store_true")
    parser.add_argument("--enforce-knowledge-tool-memory", action="store_true")
    parser.add_argument("--enforce-product-cutover", action="store_true")
    args = parser.parse_args()

    errors = verify_phase01_baseline()
    if args.enforce_langgraph:
        errors.extend(verify_enforce_langgraph())
    if args.enforce_dependencies:
        errors.extend(verify_enforce_dependencies())
    if args.enforce_real_execution:
        errors.extend(verify_enforce_real_execution())
    if args.enforce_knowledge_tool_memory:
        errors.extend(verify_enforce_knowledge_tool_memory())
    if args.enforce_product_cutover:
        errors.extend(verify_enforce_product_cutover())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Real runtime cutover verification failed.")
        return 1
    print("Real runtime cutover verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
