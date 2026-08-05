"""Fixture tree builder for the PHASE22 two-layer feature flag truth gate.

Builds a minimal, self-contained repository-shaped tree under a tmp dir:

    .agent/programs/work-products/feature-flag-registry.yaml
    .agent/programs/work-products/temporary-allowlist.yaml   (optional)
    src/backend/zuno/api/v1/product.py
    src/backend/zuno/api/v1/workspace.py
    src/backend/zuno/api/router.py
    src/backend/zuno/__init__.py
    src/backend/zuno/platform/__init__.py
    + caller-supplied production modules and tests/

The registry template mirrors the real registry shape: five rollout flags,
full PHASE02 lifecycle, RETIRED defaults with non-executable fail-closed
rollback_commands. ``build_registry`` supports surgical overrides so tests
can corrupt exactly one dimension (open rollback transition, non-RETIRED
default, missing mandatory field).
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
FIXTURE_DIR = Path(__file__).resolve().parent

RETIRED_FLAGS = [
    "product_api_v1_adapter",
    "workspace_projection_stream_v1",
    "tool_runtime_readonly_gateway",
    "postgres_domain_uow_shadow",
]

LIFECYCLE_HEADER = """\
phase_id: PHASE02
task_id: P02-T02
start_commit: 000928c7fc46224264e43677a5877d76731cd04c
status_boundary: "Flag 只允许路由和观测，不允许复制领域事实或成为永久双路径。"
lifecycle:
  allowed_states: [DECLARED, SHADOW, CANARY, DEFAULT_NEW, ROLLBACK_WINDOW, RETIRED]
  allowed_transitions:
    DECLARED: [SHADOW]
    SHADOW: [CANARY, RETIRED]
    CANARY: [DEFAULT_NEW, ROLLBACK_WINDOW]
    DEFAULT_NEW: [ROLLBACK_WINDOW, RETIRED]
    ROLLBACK_WINDOW: [DEFAULT_NEW, RETIRED]
    RETIRED: []
"""

FLAG_BLOCKS = """\
flags:
  - flag: "product_api_v1_adapter"
    owner: "01 Product Surface"
    scope: "server route"
    default: "RETIRED"
    metric: ["command_acceptance_rate"]
    rollback_command: "retired and fail-closed; no runtime adapter switch exists"
    expires_at_phase: "PHASE10"
    retire_task: "P22-T03"
    domain_fact_owner: "unchanged"
  - flag: "workspace_projection_stream_v1"
    owner: "01 Product Surface"
    scope: "SSE stream"
    default: "RETIRED"
    metric: ["sse_resume_success_rate"]
    rollback_command: "retired and fail-closed; dual stream switch removed"
    expires_at_phase: "PHASE10"
    retire_task: "P22-T03"
    domain_fact_owner: "unchanged"
  - flag: "legacy_general_agent_completion_rollback"
    owner: "06 Agent Core"
    scope: "completion route rollback"
    default: "RETIRED"
    metric: ["legacy_completion_invocation_count"]
    rollback_command: "retired and fail-closed; ZUNO_COMPLETION_CUTOVER_MODE=rollback is rejected"
    expires_at_phase: "PHASE08"
    retire_task: "P22-T03"
    domain_fact_owner: "unchanged"
  - flag: "tool_runtime_readonly_gateway"
    owner: "08 Tool Runtime"
    scope: "tool invocation"
    default: "RETIRED"
    metric: ["tool_bypass_count"]
    rollback_command: "retired and fail-closed; no read-only direct execution path exists"
    expires_at_phase: "PHASE15"
    retire_task: "P22-T03"
    domain_fact_owner: "unchanged"
  - flag: "postgres_domain_uow_shadow"
    owner: "11 Infrastructure"
    scope: "persistence"
    default: "RETIRED"
    metric: ["uow_conflict_count"]
    rollback_command: "retired and fail-closed; shadow write removed"
    expires_at_phase: "PHASE04"
    retire_task: "P22-T03"
    domain_fact_owner: "canonical owner tables after cutover"
"""

REGISTRY_TAIL = """\
validation_rules:
  - "owner, scope, default, metric, rollback_command, expires_at_phase and retire_task are mandatory."
  - "retire_task must be P22-T03 or a stricter module-specific removal task that still feeds P22-T03."
  - "domain_fact_owner cannot be a feature flag."
  - "expired flags fail the guard."
"""


def build_registry(
    *,
    retired_transition: str | None = None,
    non_retired_default: str | None = None,
    drop_mandatory_field: str | None = None,
) -> str:
    """Surgical registry variants for the fail-closed fixture tests.

    - ``retired_transition``: an extra target allowed from RETIRED, e.g.
      ``RETIRED: [DEFAULT_NEW]`` (rollback must be rejected).
    - ``non_retired_default``: flag default to swap to an open rollout state.
    - ``drop_mandatory_field``: remove one mandatory field line (slice does
      not integrate with the PHASE02 boundary).
    """
    lifecycle = LIFECYCLE_HEADER
    if retired_transition:
        lifecycle = lifecycle.replace("    RETIRED: []", f"    RETIRED: [{retired_transition}]")
    blocks = FLAG_BLOCKS
    if non_retired_default:
        blocks = blocks.replace('    default: "RETIRED"', f'    default: "{non_retired_default}"', 1)
    if drop_mandatory_field:
        lines = [line for line in blocks.splitlines() if not line.strip().startswith(drop_mandatory_field + " ")]
        blocks = "\n".join(lines) + "\n"
    return lifecycle + "\n" + blocks + "\n" + REGISTRY_TAIL


DEFAULT_REGISTRY = build_registry()

PRODUCT_V1 = '''"""Public v1 product contract fixture."""
'''

WORKSPACE_V1 = '''"""Public v1 workspace SSE contract fixture."""
EVENTS_STREAM_ROUTE = "/api/v1/workspace/task/{task_id}/events/stream"
EVENT_STREAM_MEDIA_TYPE = "text/event-stream"
'''


def _write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def build_fixture_tree(
    tmp_path: Path,
    *,
    registry: str = DEFAULT_REGISTRY,
    modules: dict[str, str] | None = None,
    tests: dict[str, str] | None = None,
    allowlist: str | None = None,
    with_v1: bool = True,
) -> Path:
    """Build a repository-shaped fixture tree. ``modules`` maps repo-relative
    production paths to source text; ``tests`` maps ``tests/...`` paths."""
    root = tmp_path / "fixture"
    _write(root / ".agent/programs/work-products/feature-flag-registry.yaml", registry)
    if allowlist is not None:
        _write(root / ".agent/programs/work-products/temporary-allowlist.yaml", allowlist)
    if with_v1:
        _write(root / "src/backend/zuno/api/v1/product.py", PRODUCT_V1)
        _write(root / "src/backend/zuno/api/v1/workspace.py", WORKSPACE_V1)
        _write(root / "src/backend/zuno/api/router.py", "# router\n")
    _write(root / "src/backend/zuno/__init__.py", "# fixture package\n")
    _write(root / "src/backend/zuno/platform/__init__.py", "# fixture package\n")
    for rel, body in (modules or {}).items():
        _write(root / rel, body)
    for rel, body in (tests or {}).items():
        _write(root / rel, body)
    return root
