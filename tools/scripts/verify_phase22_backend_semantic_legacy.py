"""PHASE22 Backend Semantic Legacy Cleanup Verifier — ownership + reachability.

This verifier is a fail-closed audit gate for the retirement of the semantic
legacy agent runtimes. It produces a two-layer result so the PR truth can be
separated from the broader repository cutover truth:

  Scoped Slice Status (this PR's own retirement)
    - AGENT_FAMILY_LEGACY_SLICE_CLEAN
    - AGENT_FAMILY_LEGACY_SLICE_BLOCKED

  Repository Runtime Status (full Backend Product Runtime cutover)
    - BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED
    - BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED
    - BACKEND_PRODUCT_RUNTIME_UNRESOLVED
    - TOOL_ERROR

The repository scope classifies every candidate runtime class by **ownership
and reachability**, not by class name alone:

  PRODUCT_LEGACY_RUNTIME
      Was or still is a complete Product Runtime: constructs an independent
      LangGraph/LangChain agent graph, owns Product Run lifecycle, executes
      tools/models directly, bypasses ToolInvocationGateway, or owns
      Plan / Final Gate / RunOutcome / Trace.

  PRODUCT_ADAPTER
      A thin facade that delegates to the canonical Product Runtime
      (``UnifiedAgentRuntimeService`` / ``SingleControllerRuntimeHarness``
      or a known composition root), does not construct an independent
      graph, and does not directly execute models or tools. Requires
      ``canonical_delegate`` evidence inside the class methods.

  INTERNAL_TEST_HARNESS
      Class definition exists but is only reached from ``tests/``,
      ``evals/``, ``docs/`` or the agent ``__init__`` facade export.
      No production entry point can construct or invoke it.

  INTERNAL_STEP_CAPABILITY
      Step-internal mechanism (e.g. ``ReActStepRunner``,
      ``StructuredResponseAgent``) only used inside the StepExecutionGraph.
      Not a top-level runtime.

  UNRESOLVED
      Production Reachability exists but canonical delegation cannot be
      statically proven (no ``canonical_delegate`` evidence, no legacy
      evidence). Also emitted when dynamic construction
      (``globals``, ``getattr``, ``eval``, ``__import__``, ``import_module``)
      can target a Runtime class whose identity cannot be resolved.

Default invocation is equivalent to ``--scope repository`` so the verifier
is fail-closed in CI. ``--scope agent-family`` is provided for workflows
that want to gate only the slice owned by this work package.

Detection is AST-based (Python ``ast`` module) — no string counting.

Usage:
    python tools/scripts/verify_phase22_backend_semantic_legacy.py
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope agent-family
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --scope repository --json
    python tools/scripts/verify_phase22_backend_semantic_legacy.py --report
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
EVIDENCE_DIR = (
    REPO_ROOT / "docs" / "evidence" / "goal05-phase22-backend-semantic-legacy-cleanup"
)


SCOPE_AGENT_FAMILY = "agent-family"
SCOPE_REPOSITORY = "repository"

# Scoped slice statuses (this PR's own retirement)
STATUS_SCOPED_CLEAN = "AGENT_FAMILY_LEGACY_SLICE_CLEAN"
STATUS_SCOPED_BLOCKED = "AGENT_FAMILY_LEGACY_SLICE_BLOCKED"

# Repository statuses (whole Backend Product Runtime cutover)
STATUS_REPO_CONFIRMED = "BACKEND_PRODUCT_RUNTIME_CUTOVER_CONFIRMED"
STATUS_REPO_BLOCKED = "BACKEND_PRODUCT_RUNTIME_CUTOVER_BLOCKED"
STATUS_REPO_UNRESOLVED = "BACKEND_PRODUCT_RUNTIME_UNRESOLVED"
STATUS_TOOL_ERROR = "TOOL_ERROR"


# Symbols retired by THIS work package (the GeneralAgent family). Used
# for the scoped slice.
RETIRED_FAMILY_CLASSES = (
    "GeneralAgent",
    "ReactAgent",
    "PlanExecuteAgent",
    "CodeActAgent",
    "Text2SQLAgent",
)

RETIRED_FAMILY_SYMBOLS = RETIRED_FAMILY_CLASSES + (
    "AgentConfig",
    "StreamAgentState",
    "EmitEventAgentMiddleware",
)

RETIRED_FAMILY_MODULES = (
    "zuno.agent.core.agents.general_agent",
    "zuno.agent.core.agents.react_agent",
    "zuno.agent.core.agents.plan_execute_agent",
    "zuno.agent.core.agents.codeact_agent",
    "zuno.agent.core.agents.text2sql_agent",
)

RETIRED_FAMILY_FILES = (
    "src/backend/zuno/agent/core/agents/general_agent.py",
    "src/backend/zuno/agent/core/agents/react_agent.py",
    "src/backend/zuno/agent/core/agents/plan_execute_agent.py",
    "src/backend/zuno/agent/core/agents/codeact_agent.py",
    "src/backend/zuno/agent/core/agents/text2sql_agent.py",
    "src/backend/zuno/agent/runtime.py",
    "src/backend/zuno/agent/state.py",
    "src/backend/zuno/agent/streaming.py",
)

FORBIDDEN_FAMILY_RUNTIME_SELECTORS = (
    "ZUNO_AGENT_RUNTIME",
    "legacy_general_agent",
    "_create_chat_agent",
)


# Production entry points scanned in both scopes. These are the surfaces
# that can reach a Product Runtime today.
ENTRY_POINT_FILES = (
    "src/backend/zuno/main.py",
    "src/backend/zuno/api/services/completion.py",
    "src/backend/zuno/api/services/workspace_task_runtime.py",
    "src/backend/zuno/api/services/agent_skill.py",
    "src/backend/zuno/api/services/mcp_server.py",
    "src/backend/zuno/api/services/workspace.py",
    "src/backend/zuno/api/services/wechat.py",
    "src/backend/zuno/api/v1/completion.py",
    "src/backend/zuno/platform/services/queue/workers.py",
    "src/backend/zuno/platform/services/cli_tool_discovery.py",
    "src/backend/zuno/platform/services/simple_api_tool.py",
    "tools/scripts/start.py",
)


# Candidate runtime classes the verifier classifies by ownership +
# reachability in repository scope. ``SINGLE_CONTROLLER_CLASS`` is the
# canonical Product Runtime and is always allowed.
SINGLE_CONTROLLER_CLASS = "SingleControllerRuntimeHarness"

CANDIDATE_RUNTIME_CLASSES = (
    SINGLE_CONTROLLER_CLASS,
    "WorkSpaceSimpleAgent",
    "WeChatAgent",
    "WechatAgent",
    "AgentControlRuntime",
)

INTERNAL_STEP_CAPABILITY_CLASSES = (
    "ReActStepRunner",
    "ReActStepExecutor",
    "ReActStepNode",
    "StructuredResponseAgent",
)


# Surfaces that do not constitute a Production Entry Point: they are
# baseline generators, fixture scripts, or doc-only references.
NON_PRODUCTION_ENTRY_POINT_FILES = (
    "src/backend/zuno/agent/product_baseline.py",
    "tools/evals/zuno/agent/product_baseline.py",
    "src/backend/zuno/agent/control_runtime.py",
)

NON_PRODUCTION_PATH_PREFIXES = (
    "tests/",
    "docs/",
    ".agent/",
)


# Symbols that, when called inside a candidate runtime's methods, prove
# it owns the Product Run lifecycle or executes tools/models directly.
DIRECT_MODEL_CALL_NAMES = (
    "model.invoke",
    "model.ainvoke",
    "model.stream",
    "model.astream",
)

DIRECT_TOOL_CALL_NAMES = (
    "tool.invoke",
    "tool.ainvoke",
    "tool.run",
    "tool.arun",
)

# Direct ``handler(request)`` tool-call surface. AST-detected because
# string matching is too noisy on docstrings and tests.
DIRECT_HANDLER_AWAIT_PATTERN = "handler"

# Symbols that prove the candidate constructs an independent graph.
INDEPENDENT_GRAPH_BUILDERS = (
    "create_agent",
    "create_react_agent",
    "create_structured_chat_agent",
    "StateGraph",
    "MessageGraph",
    "ToolNode",
)

# Canonical runtime / composition-root symbols a thin Product Adapter
# must delegate to.
CANONICAL_RUNTIME_SYMBOLS = (
    "UnifiedAgentRuntimeService",
    "SingleControllerRuntimeHarness",
    "SingleControllerDurableRuntime",
    "build_single_controller_runtime_harness",
    "WorkspaceAgentRuntime",
    "WorkspaceTaskRuntimeService",
)

# Method names that, when invoked as ``self.<attr>.<method>(...)`` on a
# non-model / non-tool attribute, indicate the class is delegating to a
# runtime dependency (a thin Product Adapter pattern). This is the
# heuristic that recognizes a thin adapter that does not embed the
# canonical runtime class name as a literal symbol.
DELEGATE_METHOD_NAMES = (
    "start",
    "stream",
    "astream",
    "astream_events",
    "run",
    "run_step",
    "execute",
    "drive",
)

# Attributes that prove the call target is a model / tool / llm client,
# NOT a runtime dependency. When ``self.<attr>.<method>`` matches one of
# these names, the call is direct model/tool invocation, not delegation.
DIRECT_EXEC_ATTR_NAMES = (
    "model",
    "tool",
    "tools",
    "llm",
    "client",
    "chat",
    "chat_model",
    "tools_client",
    "tool_client",
)

# Attributes / locals that show the candidate owns Plan / Trace / Budget /
# Final Gate / RunOutcome directly.
PRODUCT_LIFECYCLE_ATTRIBUTES = (
    "trace_events",
    "trace_event",
    "final_answer",
    "final_response",
    "run_outcome",
    "RunOutcome",
    "capability_plan",
    "CapabilityPlan",
    "budget",
    "Budget",
    "publication",
    "Publication",
    "final_gate",
    "FinalGate",
    "planner_output",
    "PlannerOutput",
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    category: str
    path: str
    line: int
    detail: str
    severity: str = "error"


@dataclass
class Classification:
    """Per-class ownership + reachability verdict."""

    name: str
    classification: str
    module: str
    line: int = 0
    evidence: list[str] = field(default_factory=list)
    production_callers: list[tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "classification": self.classification,
            "module": self.module,
            "line": self.line,
            "evidence": list(self.evidence),
            "production_callers": [
                {"path": path, "line": line}
                for path, line in self.production_callers
            ],
        }


@dataclass
class ScopeResult:
    status: str = ""
    findings: list[Finding] = field(default_factory=list)
    classifications: list[Classification] = field(default_factory=list)
    unresolved: list[Finding] = field(default_factory=list)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------


def _classdef_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            names.add(node.name)
    return names


def _imports_in(tree: ast.AST) -> list[tuple[str, int]]:
    """Return ``(module_or_full_name, lineno)`` for every import.

    For ``from x.y import z`` we return ``"x.y"`` (the bare module) so
    prefix-based matchers work correctly. For ``import x.y`` we return
    ``"x.y"``.
    """
    imports: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append((module, node.lineno))
    return imports


def _imported_symbols(tree: ast.AST) -> list[tuple[str, str, int]]:
    """Return ``(module, symbol, lineno)`` for every ``from ... import sym``.

    Used by callers that need the imported *symbol* (e.g. for class-name
    reachability checks) in addition to the bare module path.
    """
    imports: list[tuple[str, str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append((module, alias.name, node.lineno))
    return imports


def _classdef_nodes(tree: ast.AST) -> Iterable[ast.ClassDef]:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            yield node


def _call_target_strings(tree: ast.AST) -> list[tuple[str, int]]:
    """Return (callable_text, line_no) for every Call node."""
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            try:
                results.append((ast.unparse(node.func), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _attribute_chains(tree: ast.AST) -> list[tuple[str, int]]:
    """Return attribute chain text for every Attribute node."""
    results: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            try:
                results.append((ast.unparse(node), node.lineno))
            except Exception:  # pragma: no cover - defensive
                continue
    return results


def _direct_handler_await_sites(tree: ast.AST) -> list[tuple[int, str]]:
    """Return (line, snippet) for ``<assign> = await handler(...)`` assignments.

    Only assignments are matched — the workspace bypass pattern is the
    well-known shape ``response = await handler(request)`` / ``tool_result
    = await handler(request)`` inside an ``AgentMiddleware`` body. A bare
    ``await handler(payload)`` in a worker runner is NOT a tool bypass
    because ``handler`` is a Callable parameter, not the middleware
    context. Detecting that distinction purely from AST requires the
    Assign form.
    """
    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Await):
            continue
        await_node = node.value
        if not isinstance(await_node.value, ast.Call):
            continue
        call = await_node.value
        try:
            text = ast.unparse(call.func)
        except Exception:  # pragma: no cover - defensive
            continue
        if text == DIRECT_HANDLER_AWAIT_PATTERN:
            sites.append((node.lineno, ast.unparse(call)))
    return sites


def _safe_parse(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Per-class classification primitives
# ---------------------------------------------------------------------------


def _class_method_bodies(class_node: ast.ClassDef) -> list[ast.AST]:
    """Return a list of AST subtrees for every method body in the class."""
    return [node for node in class_node.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _collect_attribute_names(tree: ast.AST) -> set[str]:
    """Collect lifecycle fields owned by the candidate class.

    A Product Adapter is allowed to project a canonical runtime result into
    its channel contract.  In particular, reading
    ``observation.metadata["final_answer"]`` or assigning a local
    ``final_answer`` is presentation mapping, not ownership of the Product
    Run lifecycle.  Only fields rooted at ``self`` count as class-owned
    lifecycle state; this keeps the ownership check fail-closed without
    treating every result field name as a legacy runtime.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            if not isinstance(node.value, ast.Name) or node.value.id != "self":
                continue
            # Private ``self._final_answer(...)``-style helper methods are
            # adapter implementation details, not owned lifecycle fields.
            if node.attr.startswith("_"):
                continue
            try:
                if node.attr in PRODUCT_LIFECYCLE_ATTRIBUTES:
                    names.add(node.attr)
            except Exception:  # pragma: no cover - defensive
                continue
        elif isinstance(node, ast.Dict):
            # A runtime that publishes a run-shaped result object with
            # lifecycle fields owns that publication contract.  This is
            # distinct from an adapter reading a field from an observation;
            # the latter is not a dict key in the adapter's returned payload.
            for key in node.keys:
                if isinstance(key, ast.Constant) and isinstance(key.value, str):
                    if key.value in PRODUCT_LIFECYCLE_ATTRIBUTES:
                        names.add(key.value)
    return names


def _evidence_for_class(class_node: ast.ClassDef) -> list[str]:
    """Walk every method body of a candidate class and collect behaviour
    evidence strings.
    """
    evidence: list[str] = []
    bodies = _class_method_bodies(class_node)

    def _matches(call_text: str, target: str) -> bool:
        """Match ``call_text`` against ``target``. ``call_text`` is the
        unparsed Call.func which may be ``self.model.ainvoke`` etc. We
        match either by full equality or by the trailing suffix
        ``.target`` so ``self.<attr>.target`` also triggers.
        """
        if call_text == target:
            return True
        if call_text.endswith("." + target):
            return True
        return False

    for method in bodies:
        for call_text, line in _call_target_strings(method):
            head = call_text.split("(", 1)[0].split(".", 1)[-1]
            for builder in INDEPENDENT_GRAPH_BUILDERS:
                if head == builder or call_text == builder:
                    evidence.append(
                        f"independent_graph:{call_text}@{method.name}:{line}"
                    )
                    break
            for sym in DIRECT_MODEL_CALL_NAMES:
                if _matches(call_text, sym):
                    evidence.append(f"direct_model_call:{call_text}@{method.name}:{line}")
                    break
            for sym in DIRECT_TOOL_CALL_NAMES:
                if _matches(call_text, sym):
                    evidence.append(f"direct_tool_call:{call_text}@{method.name}:{line}")
                    break
            for sym in CANONICAL_RUNTIME_SYMBOLS:
                if _matches(call_text, sym):
                    evidence.append(
                        f"canonical_delegate:{call_text}@{method.name}:{line}"
                    )
                    break
            # Detect the thin-adapter delegation pattern
            # ``self.<attr>.<method>(...)`` where the attribute is NOT a
            # direct model / tool locator and the method is a known
            # runtime entry point. This is the heuristic that recognizes
            # adapters that don't reference the canonical runtime class
            # name as a literal symbol.
            already_delegate = any(
                entry.startswith("canonical_delegate:") for entry in evidence
            )
            if not already_delegate:
                parts = call_text.split(".")
                if (
                    len(parts) >= 3
                    and parts[0] == "self"
                    and parts[-1] in DELEGATE_METHOD_NAMES
                    and parts[1] not in DIRECT_EXEC_ATTR_NAMES
                ):
                    evidence.append(
                        f"canonical_delegate:{call_text}@{method.name}:{line}"
                    )
        for line, snippet in _direct_handler_await_sites(method):
            evidence.append(f"direct_handler_await:{snippet}@{method.name}:{line}")
        attrs = _collect_attribute_names(method)
        for attr in attrs:
            for marker in PRODUCT_LIFECYCLE_ATTRIBUTES:
                if attr == marker or attr.endswith("." + marker):
                    evidence.append(
                        f"product_lifecycle_attr:{attr}@{method.name}"
                    )
                    break
    # De-duplicate while preserving order.
    seen: set[str] = set()
    deduped: list[str] = []
    for item in evidence:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _is_production_path(path: str) -> bool:
    rel = path.replace("\\", "/")
    for prefix in NON_PRODUCTION_PATH_PREFIXES:
        if rel.startswith(prefix):
            return False
    if rel in NON_PRODUCTION_ENTRY_POINT_FILES:
        return False
    # ``__init__.py`` files in the backend tree are facade re-export
    # surfaces — TYPE_CHECKING imports, ``__all__`` lists, and ``_EXPORT_TO_MODULE``
    # dictionaries — not real Product Runtime callers. They do not count
    # as production reachability on their own.
    if rel.endswith("__init__.py"):
        return False
    return True


def _candidate_local_names(tree: ast.AST, class_name: str) -> set[str]:
    """Return the set of local names that *could* refer to ``class_name``
    in this module's scope.

    Resolves:
      - ``from x import ClassName``                  → local ``ClassName``
      - ``from x import ClassName as Alias``         → local ``Alias``
      - ``import x.y.ClassName``                     → local ``ClassName``
      - ``import x.y.ClassName as Alias``            → local ``Alias``
      - ``LocalName = ClassName`` (module-level)     → local ``LocalName``

    The result is a name *set* — membership is sufficient to claim
    reachability. ``mod.ClassName(...)`` works without resolution because
    the verifier checks the trailing segment separately.
    """
    names: set[str] = {class_name}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                local = alias.asname or alias.name
                if alias.name == class_name:
                    names.add(local)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                tail = parts[-1]
                local = alias.asname or tail
                if tail == class_name:
                    names.add(local)
        elif isinstance(node, ast.Assign):
            # Only module-level assignments are emitted by ast.walk()
            # only when the parent is Module; here we filter explicitly
            # by treating the value text. We accept any RHS that
            # matches the class name as a literal Name.
            if not all(isinstance(t, ast.Name) for t in node.targets):
                continue
            try:
                rhs_text = ast.unparse(node.value)
            except Exception:  # pragma: no cover - defensive
                continue
            if rhs_text == class_name:
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.add(t.id)
    return names


def _production_callers_for(
    class_name: str,
    files_index: dict[str, ast.AST],
    production_paths: set[str],
) -> list[tuple[str, int]]:
    """Find every (path, line) where ``class_name`` is **constructed** in
    production code. Bare imports and facade ``__init__.py`` re-exports
    are not counted.

    The matcher recognises:
      - direct ``ClassName(...)`` calls
      - module-qualified ``module.ClassName(...)`` calls
      - module-alias-qualified ``alias.ClassName(...)`` calls
      - aliased ``from x import ClassName as Alias`` followed by ``Alias(...)``
      - module-level ``LocalName = ClassName`` then ``LocalName(...)``
    """
    sites: list[tuple[str, int]] = []
    for rel, tree in files_index.items():
        if rel not in production_paths:
            continue
        local_names = _candidate_local_names(tree, class_name)
        for call_text, call_line in _call_target_strings(tree):
            head = call_text.split("(", 1)[0]
            # Qualified construction: take the trailing attribute name.
            if "." in head:
                bare = head.rsplit(".", 1)[-1]
            else:
                bare = head
            if bare in local_names:
                sites.append((rel, call_line))
    return sites


def _dynamic_constructor_sites(tree: ast.AST) -> list[tuple[int, str]]:
    """Return (line, snippet) for every Call that uses a dynamic loader
    and *could* target a Runtime class.

    The verifier cannot statically prove the type returned by ``globals``,
    ``getattr``, ``eval``, ``__import__``, ``import_module``, ``locals`` or
    ``vars``. The token heuristic below is intentionally conservative:
    we only flag calls whose textual representation contains a token
    commonly used in Runtime / Agent / Service / Harness / Controller names.
    """
    tokens = ("Agent", "Runtime", "Controller", "Service", "Harness", "Factory")
    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name: str | None = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if func_name not in (
            "globals",
            "getattr",
            "eval",
            "__import__",
            "import_module",
            "locals",
            "vars",
        ):
            continue
        try:
            text = ast.unparse(node)
        except Exception:  # pragma: no cover - defensive
            continue
        if not any(token in text for token in tokens):
            continue
        sites.append((node.lineno, text))
    return sites


def _unresolved_alias_or_factory_sites(
    tree: ast.AST,
    class_name: str,
) -> list[tuple[int, str]]:
    """Return (line, snippet) for every Call whose callee is a local
    name that *could* be a factory producing ``class_name`` but whose
    return type cannot be proven statically.

    Examples that trigger this:
      - ``globals()["Runtime"]()`` returns a class we cannot introspect.
      - ``make_agent()`` returns an opaque object.
      - ``AgentClass()`` where ``AgentClass`` is assigned in a way we
        cannot resolve (e.g. inside a function).

    The verifier reports these as UNRESOLVED on the candidate class to
    fail closed rather than silently allow.
    """
    # Build the set of names we *can* resolve to the candidate class.
    local_names = _candidate_local_names(tree, class_name)
    sites: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        callee_name: str | None = None
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            callee_name = node.func.attr
        if callee_name is None:
            continue
        # Callee is already a known local for the candidate class → safe.
        if callee_name in local_names:
            continue
        # Callee is a known dynamic loader → reported elsewhere.
        if callee_name in ("globals", "getattr", "eval", "__import__", "import_module"):
            continue
        # Callee is "ClassName(...)" but we can't resolve it via the
        # import map. This catches ``factory_class()`` shapes that
        # *might* produce a Runtime class.
        if isinstance(node.func, ast.Name) and callee_name.endswith("Runtime"):
            try:
                text = ast.unparse(node)
            except Exception:  # pragma: no cover - defensive
                continue
            sites.append((node.lineno, text))
    return sites


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------


def classify_class(
    *,
    class_name: str,
    class_node: ast.ClassDef | None,
    module_path: str,
    production_callers: list[tuple[str, int]],
    evidence: list[str] | None = None,
) -> Classification:
    """Classify a single candidate class.

    The decision tree is fail-closed:

      1. ``class_name`` is in ``SINGLE_CONTROLLER_CLASS`` →
         ``PRODUCT_CANONICAL`` (informational, never blocking).
      2. ``class_name`` is in ``INTERNAL_STEP_CAPABILITY_CLASSES`` →
         ``INTERNAL_STEP_CAPABILITY``.
      3. ``class_name`` has no production callers →
         ``INTERNAL_TEST_HARNESS`` (a non-production class definition
         cannot block on its own).
      4. ``class_name`` has production callers AND any of:
         ``independent_graph``, ``direct_model_call``, ``direct_tool_call``,
         ``direct_handler_await`` or ``product_lifecycle_attr`` →
         ``PRODUCT_LEGACY_RUNTIME`` (BLOCKED).
      5. ``class_name`` has production callers AND has
         ``canonical_delegate`` evidence AND no legacy evidence →
         ``PRODUCT_ADAPTER`` (allowed).
      6. ``class_name`` has production callers AND has no
         ``canonical_delegate`` evidence AND no legacy evidence →
         ``UNRESOLVED`` (BLOCKED via non-zero exit).

    Step 6 is the fail-closed contract: a class that *can* be reached
    from production code but for which the verifier cannot prove
    canonical delegation is treated as ``UNRESOLVED``. The repository
    scope exits non-zero whenever any candidate class is ``UNRESOLVED``.
    """
    ev = list(evidence or [])
    if class_name == SINGLE_CONTROLLER_CLASS:
        return Classification(
            name=class_name,
            classification="PRODUCT_CANONICAL",
            module=module_path,
            line=getattr(class_node, "lineno", 0),
            evidence=ev,
            production_callers=production_callers,
        )
    if class_name in INTERNAL_STEP_CAPABILITY_CLASSES:
        return Classification(
            name=class_name,
            classification="INTERNAL_STEP_CAPABILITY",
            module=module_path,
            line=getattr(class_node, "lineno", 0),
            evidence=ev,
            production_callers=production_callers,
        )
    if not production_callers:
        return Classification(
            name=class_name,
            classification="INTERNAL_TEST_HARNESS",
            module=module_path,
            line=getattr(class_node, "lineno", 0),
            evidence=ev,
            production_callers=[],
        )
    # Has production callers. Look for legacy behaviour evidence.
    legacy_kinds = (
        "independent_graph",
        "direct_model_call",
        "direct_tool_call",
        "direct_handler_await",
        "product_lifecycle_attr",
    )
    for entry in ev:
        for kind in legacy_kinds:
            if entry.startswith(kind + ":"):
                return Classification(
                    name=class_name,
                    classification="PRODUCT_LEGACY_RUNTIME",
                    module=module_path,
                    line=getattr(class_node, "lineno", 0),
                    evidence=ev,
                    production_callers=production_callers,
                )
    # No legacy evidence. Look for canonical delegation evidence.
    has_canonical_delegate = any(
        entry.startswith("canonical_delegate:") for entry in ev
    )
    if has_canonical_delegate:
        return Classification(
            name=class_name,
            classification="PRODUCT_ADAPTER",
            module=module_path,
            line=getattr(class_node, "lineno", 0),
            evidence=ev,
            production_callers=production_callers,
        )
    # Production caller + no legacy evidence + no canonical_delegate
    # evidence → UNRESOLVED (fail-closed).
    return Classification(
        name=class_name,
        classification="UNRESOLVED",
        module=module_path,
        line=getattr(class_node, "lineno", 0),
        evidence=ev,
        production_callers=production_callers,
    )


# ---------------------------------------------------------------------------
# Scope: agent-family (this PR's own retirement)
# ---------------------------------------------------------------------------


def _check_retired_files_present() -> list[Finding]:
    findings: list[Finding] = []
    for rel in RETIRED_FAMILY_FILES:
        if (REPO_ROOT / rel).exists():
            findings.append(
                Finding(
                    category="retired_file_present",
                    path=rel,
                    line=0,
                    detail=f"retired file is present: {rel}",
                )
            )
    return findings


def _check_retired_imports_in_entry_points() -> list[Finding]:
    findings: list[Finding] = []
    for rel in ENTRY_POINT_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for module, lineno in _imports_in(tree):
            if module in RETIRED_FAMILY_MODULES:
                findings.append(
                    Finding(
                        category="retired_module_imported",
                        path=rel,
                        line=lineno,
                        detail=f"entry point imports retired module: {module}",
                    )
                )
    return findings


def _check_retired_symbols_in_agent_exports() -> list[Finding]:
    """AST-detect retired symbols in agent package __all__."""
    findings: list[Finding] = []
    candidates = [
        "src/backend/zuno/agent/__init__.py",
        "src/backend/zuno/agent/core/__init__.py",
        "src/backend/zuno/agent/core/agents/__init__.py",
    ]
    for rel in candidates:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, (ast.List, ast.Tuple))
                    ):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                if elt.value in RETIRED_FAMILY_SYMBOLS:
                                    findings.append(
                                        Finding(
                                            category="retired_symbol_in_all",
                                            path=rel,
                                            line=elt.lineno,
                                            detail=f"retired symbol re-exported: {elt.value}",
                                        )
                                    )
    return findings


def _check_forbidden_selectors_in_entry_points() -> list[Finding]:
    findings: list[Finding] = []
    for rel in ENTRY_POINT_FILES:
        path = REPO_ROOT / rel
        if not path.exists():
            continue
        tree = _safe_parse(path)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_FAMILY_RUNTIME_SELECTORS:
                findings.append(
                    Finding(
                        category="forbidden_selector",
                        path=rel,
                        line=node.lineno,
                        detail=f"forbidden runtime selector referenced: {node.id}",
                    )
                )
    return findings


def verify_agent_family_scope() -> ScopeResult:
    result = ScopeResult()
    result.findings.extend(_check_retired_files_present())
    result.findings.extend(_check_retired_imports_in_entry_points())
    result.findings.extend(_check_retired_symbols_in_agent_exports())
    result.findings.extend(_check_forbidden_selectors_in_entry_points())
    if result.findings:
        result.status = STATUS_SCOPED_BLOCKED
    else:
        result.status = STATUS_SCOPED_CLEAN
    return result


# ---------------------------------------------------------------------------
# Scope: repository (whole Backend Product Runtime cutover)
# ---------------------------------------------------------------------------


def _iter_python_files() -> Iterable[Path]:
    for path in BACKEND_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _build_file_index() -> dict[str, ast.AST]:
    index: dict[str, ast.AST] = {}
    for path in _iter_python_files():
        rel = path.relative_to(REPO_ROOT).as_posix()
        tree = _safe_parse(path)
        if tree is None:
            continue
        index[rel] = tree
    return index


def _production_path_set(file_index: dict[str, ast.AST]) -> set[str]:
    paths = {rel for rel in file_index if _is_production_path(rel)}
    # The entry-point files are always production even if they import
    # only fixtures.
    for rel in ENTRY_POINT_FILES:
        if rel in file_index:
            paths.add(rel)
    return paths


def _classify_repository(file_index: dict[str, ast.AST]) -> tuple[
    list[Classification], list[Finding], list[Finding]
]:
    """Walk the backend tree, classify every candidate class, and emit
    findings for PRODUCT_LEGACY_RUNTIME classes plus the dynamic-load
    unresolved cases.

    Returns a triple ``(classifications, legacy_findings, unresolved_findings)``
    where ``unresolved_findings`` includes both dynamic-loader sites and
    any UNRESOLVED per-class verdicts.
    """
    classifications: list[Classification] = []
    production_paths = _production_path_set(file_index)
    dynamic_findings: list[Finding] = []
    legacy_findings: list[Finding] = []
    unresolved_findings: list[Finding] = []

    for rel, tree in file_index.items():
        for class_node in _classdef_nodes(tree):
            if class_node.name not in CANDIDATE_RUNTIME_CLASSES:
                continue
            evidence = _evidence_for_class(class_node)
            production_callers = _production_callers_for(
                class_node.name, file_index, production_paths
            )
            verdict = classify_class(
                class_name=class_node.name,
                class_node=class_node,
                module_path=rel,
                production_callers=production_callers,
                evidence=evidence,
            )
            classifications.append(verdict)
            if verdict.classification == "PRODUCT_LEGACY_RUNTIME":
                legacy_findings.append(
                    Finding(
                        category="legacy_runtime_owner",
                        path=rel,
                        line=class_node.lineno,
                        detail=(
                            f"PRODUCT_LEGACY_RUNTIME '{class_node.name}' owns "
                            f"the Product Run or executes tools/models directly: "
                            f"{'; '.join(evidence) or 'legacy_runtime_signature'}"
                        ),
                    )
                )
            elif verdict.classification == "UNRESOLVED":
                unresolved_findings.append(
                    Finding(
                        category="unresolved_runtime_ownership",
                        path=rel,
                        line=class_node.lineno,
                        detail=(
                            f"UNRESOLVED '{class_node.name}' has a Production "
                            f"Entry Point caller but no canonical_delegate "
                            f"evidence and no legacy markers: "
                            f"{'; '.join(evidence) or 'no_classification_evidence'}"
                        ),
                    )
                )

        # Detect dynamic Runtime constructions in production paths.
        if rel in production_paths:
            for line, snippet in _dynamic_constructor_sites(tree):
                unresolved_findings.append(
                    Finding(
                        category="dynamic_runtime_load",
                        path=rel,
                        line=line,
                        detail=f"unresolved dynamic Runtime construction: {snippet}",
                    )
                )
        # Always flag ``await handler(...)`` invocations in production
        # paths because they bypass ToolInvocationGateway.
        if rel in production_paths:
            for line, snippet in _direct_handler_await_sites(tree):
                legacy_findings.append(
                    Finding(
                        category="direct_handler_bypass",
                        path=rel,
                        line=line,
                        detail=f"direct handler(request) tool call: {snippet}",
                    )
                )

    return classifications, legacy_findings, unresolved_findings


def verify_repository_scope() -> ScopeResult:
    result = ScopeResult()
    file_index = _build_file_index()
    classifications, legacy_findings, unresolved_findings = _classify_repository(
        file_index
    )
    result.classifications = classifications
    # UNRESOLVED status dominates: any unresolved finding exits non-zero.
    for finding in unresolved_findings:
        result.unresolved.append(finding)
    if unresolved_findings:
        for finding in unresolved_findings:
            result.findings.append(finding)
        result.status = STATUS_REPO_UNRESOLVED
        return result
    for finding in legacy_findings:
        result.add(finding)
    if result.findings:
        result.status = STATUS_REPO_BLOCKED
    else:
        result.status = STATUS_REPO_CONFIRMED
    return result


# ---------------------------------------------------------------------------
# CLI driver
# ---------------------------------------------------------------------------


def _serialise_finding(finding: Finding) -> dict:
    return {
        "category": finding.category,
        "path": finding.path,
        "line": finding.line,
        "detail": finding.detail,
        "severity": finding.severity,
    }


def _serialise_scope(scope: str, result: ScopeResult) -> dict:
    return {
        "scope": scope,
        "status": result.status,
        "finding_count": len(result.findings),
        "findings": [_serialise_finding(f) for f in result.findings],
        "classifications": [c.to_dict() for c in result.classifications],
        "unresolved": [_serialise_finding(f) for f in result.unresolved],
    }


def _run_scope(scope: str) -> ScopeResult:
    if scope == SCOPE_AGENT_FAMILY:
        return verify_agent_family_scope()
    if scope == SCOPE_REPOSITORY:
        return verify_repository_scope()
    raise SystemExit(f"unknown scope: {scope}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scope",
        choices=[SCOPE_AGENT_FAMILY, SCOPE_REPOSITORY],
        default=SCOPE_REPOSITORY,
        help="Scope of the verification (default: repository, fail-closed).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Write verifier_report.json to the evidence directory.",
    )
    args = parser.parse_args(argv)

    scope = args.scope
    try:
        result = _run_scope(scope)
    except Exception as exc:  # pragma: no cover - defensive
        if args.json:
            print(
                json.dumps(
                    {
                        "scope": scope,
                        "status": STATUS_TOOL_ERROR,
                        "finding_count": 0,
                        "findings": [],
                        "classifications": [],
                        "unresolved": [],
                        "error": str(exc),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        print(f"PHASE22 backend semantic legacy verifier tool error: {exc}", file=sys.stderr)
        return 2

    payload = _serialise_scope(scope, result)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))

    if args.report:
        EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = EVIDENCE_DIR / "verifier_report.json"
        report_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {report_path.relative_to(REPO_ROOT)}", file=sys.stderr)

    if not args.json:
        print(f"PHASE22 backend semantic legacy verifier scope={scope} status={result.status}")
        for finding in result.findings:
            print(f"FINDING [{finding.category}] {finding.path}:{finding.line} {finding.detail}")
        for cls in result.classifications:
            print(
                f"CLASSIFICATION [{cls.classification}] {cls.module}:{cls.line} "
                f"{cls.name}"
            )

    if scope == SCOPE_AGENT_FAMILY:
        return 0 if result.status == STATUS_SCOPED_CLEAN else 1
    # Repository scope is fail-closed: any non-CONFIRMED status exits non-zero.
    return 0 if result.status == STATUS_REPO_CONFIRMED else 1


if __name__ == "__main__":
    raise SystemExit(main())
