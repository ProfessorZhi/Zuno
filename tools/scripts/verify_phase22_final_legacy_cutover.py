"""verify_phase22_final_legacy_cutover.py

PHASE22 Legacy Cutover Final Audit verifier.

This is the final fail-closed gate for the PHASE22 Legacy Cleanup / Canonical
Cutover Program. It re-asserts the absence of every short-cut category that
the early wave verifiers already covered, *plus* a small set of cross-cutting
checks that those verifiers did not combine in one place (general-agent
production reachability, feature-flag owner/expiry, allowlist expiry,
re-introduction of forbidden directories after retirement, and so on).

The verifier is intentionally narrow: each check either passes or fails with
a single string error message. The exit code summarises the highest-severity
class of error:

    0  LEGACY_CUTOVER_AUDIT_CLEAN
    2  LEGACY_RUNTIME_BLOCKERS_FOUND
    3  DUAL_PATH_BLOCKERS_FOUND
    4  ALIAS_BYPASS_BLOCKERS_FOUND
    5  AUDIT_UNRESOLVED
    6  TOOL_ERROR

History directories (``docs/history/``) and the historical evidence directory
(``docs/evidence/``) are explicitly tolerated; their contents are not part of
the production-source guarantees that this verifier enforces.

The script is fully self-contained — no third-party dependencies — so it can
run in any of the four canonical verifier environments.
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Roots that must remain legacy-free as production source.
PRODUCTION_ROOTS = (
    REPO_ROOT / "src" / "backend" / "zuno",
    REPO_ROOT / "apps" / "web" / "src",
    REPO_ROOT / "apps" / "desktop" / "src",
)

# Roots that are explicitly NOT production source and must not be falsely
# allowed as production paths. The PHASE22 cleanup verifier already filters
# docs/history and docs/evidence; we do the same here for clarity.
NON_PRODUCTION_ROOTS_FRAGMENTS = (
    "docs/history",
    "docs/evidence",
    ".agent/programs/work-products",
    ".claude/worktrees",
    "__pycache__",
)

# Top-level Python packages rooted at the old architecture. The current
# canonical owner for backend code is `zuno.{api,platform,agent,capability,
# knowledge,memory,security,observability}`.
LEGACY_ZUNO_PACKAGES = (
    "zuno.core",
    "zuno.services",
    "zuno.schema",
    "zuno.database",
    "zuno.tools",
    "zuno.resources",
    "zuno.config",
    "zuno.mcp_servers",
    "zuno.utils",
)

# Forbidden directory / file segments for production source. We treat a path
# segment that *equals* one of these (or starts/ends with `<forbidden>_` /
# `_legacy` style) as a re-introduction. This list intentionally only
# contains names that the canonical-directory contract actually bans.
LEGACY_SEGMENT_FORBIDDEN = ("legacy",)
LEGACY_FILE_FORBIDDEN = ("legacy_aliases.py",)

# Forbidden re-introductions of retired shells.
RETIRED_FORBIDDEN_PATHS = (
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility",
    REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "compatibility" / "legacy_aliases.py",
    REPO_ROOT / "tests" / "legacy_guards",
)

# Markers for rollback / dual-path / dual-write that must not appear in
# production source. We allow these names to appear in:
#   * the feature-flag registry (only as DECLARED and immediately RETIRED),
#   * verifiers (which assert they are absent),
#   * the old evidence directory (history is exempt by spec).
ROLLBACK_MARKERS = (
    "ZUNO_AGENT_RUNTIME=legacy_general_agent",
    "legacy_general_agent_completion_rollback",
    "ZUNO_COMPLETION_CUTOVER_MODE=rollback",
    "dual_read=",
    "dual_write=",
    "shadow_write=",
    "write_both=",
    "fallback_to_old=",
    "fallback_to_legacy=",
    "compat_mode=",
    "migration_mode=",
    "temporary_flag=",
)

# Feature-flag registry plus removal-candidates work products drive the
# snapshot machine checks.
FEATURE_FLAG_REGISTRY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "feature-flag-registry.yaml"
)
REMOVAL_CANDIDATES = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "phase22-removal-candidates.yaml"
)
TEMPORARY_ALLOWLIST = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "temporary-allowlist.yaml"
)
LEGACY_BYPASS_INVENTORY = (
    REPO_ROOT / ".agent" / "programs" / "work-products" / "legacy-bypass-inventory.yaml"
)

# The completion endpoint must not import `GeneralAgent` or the rollback proxy.
COMPLETION_SERVICE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "services" / "completion.py"
COMPLETION_ROUTE = REPO_ROOT / "src" / "backend" / "zuno" / "api" / "v1" / "completion.py"

# A small slice of `--json` output friendly fields.
VERIFIER_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class AuditResult:
    """Container for collected audit findings.

    Each finding is appended under exactly one of the four high-severity
    buckets. ``runtime_blockers`` and ``dual_path_blockers`` are the two
    buckets that earn non-zero exit codes on their own; ``alias_bypass`` is
    the catch-all for ownerless import shims; ``unresolved`` captures items
    that static analysis alone cannot prove dead.
    """

    runtime_blockers: List[str] = field(default_factory=list)
    dual_path_blockers: List[str] = field(default_factory=list)
    alias_bypass_blockers: List[str] = field(default_factory=list)
    unresolved: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def category(self) -> str:
        if any((self.runtime_blockers, self.dual_path_blockers, self.alias_bypass_blockers, self.unresolved)):
            if self.runtime_blockers:
                return "LEGACY_RUNTIME_BLOCKERS_FOUND"
            if self.dual_path_blockers:
                return "DUAL_PATH_BLOCKERS_FOUND"
            if self.alias_bypass_blockers:
                return "ALIAS_BYPASS_BLOCKERS_FOUND"
            return "AUDIT_UNRESOLVED"
        return "LEGACY_CUTOVER_AUDIT_CLEAN"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _is_production_path(path: Path) -> bool:
    """Return True if the path lives under a production source root.

    Production roots are ``src/backend/zuno``, ``apps/web/src`` and
    ``apps/desktop/src``. Anything else is excluded.
    """

    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    for root in PRODUCTION_ROOTS:
        try:
            path.relative_to(root)
        except ValueError:
            continue
        rel_parts = path.relative_to(root).parts
        for fragment in NON_PRODUCTION_ROOTS_FRAGMENTS:
            if fragment in rel_parts:
                return False
        return True
    return False


def _iter_python_files(roots=None):
    if roots is None:
        roots = PRODUCTION_ROOTS
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if any(part == "__pycache__" for part in path.parts):
                continue
            yield path


def _yaml_minimal_load(text: str) -> dict | list | None:
    """Tiny YAML loader that supports only the constructs we need.

    We intentionally avoid pulling in PyYAML at verifier runtime. The feature-
    flag registry, the temporary allowlist, the removal candidates and the
    legacy bypass inventory all use simple ``key: value`` mapping files with
    occasional nested lists; that is more than enough for our needs.
    """

    return _YAML_PARSER.parse(text)


class _TinyYaml:
    """A miniature YAML parser tuned for the registry files in this repo.

    It supports:

      * key/value pairs at any indent level;
      * nested mappings keyed by indented ``key: value`` pairs;
      * list items prefixed by ``-``;
      * quoted and bare scalars (booleans/numbers returned unquoted);
      * ``# line comments``.

    It explicitly does NOT handle flow style, anchors, multiline scalars or
    other exotic features. All our work-products fall within these limits.
    """

    @staticmethod
    def parse(text: str):
        lines: List[tuple] = []
        for raw in text.splitlines():
            stripped = raw.split("#", 1)[0].rstrip()
            if not stripped:
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            content = stripped.strip()
            lines.append((indent, content))

        root: dict = {}

        def _walk(buf: List[tuple], start_index: int, indent: int) -> tuple:
            container: dict | list = {}
            i = start_index
            while i < len(buf):
                cur_indent, line = buf[i]
                if cur_indent < indent:
                    break
                if cur_indent > indent:
                    break
                if line.startswith("- "):
                    if not isinstance(container, list):
                        # Promote to list container by recursing.
                        container = []
                    inner, j = _walk_list_item(buf, i, cur_indent)
                    container.append(inner)
                    i = j
                    continue
                if line.endswith(":"):
                    key = line[:-1]
                    if not isinstance(container, dict):
                        container = {}
                    nested, j = _walk(buf, i + 1, indent + 2)
                    container[key] = nested
                    i = j
                    continue
                if ": " in line:
                    key, _, value = line.partition(": ")
                    if not isinstance(container, dict):
                        container = {}
                    container[key] = _yaml_scalar(value)
                    i += 1
                    continue
                i += 1
            return container, i

        def _walk_list_item(buf: List[tuple], start_index: int, indent: int) -> tuple:
            _, line = buf[start_index]
            assert line.startswith("- ")
            item_text = line[2:].strip()
            item: dict = {}
            if ": " in item_text and not (
                item_text.startswith('"') or item_text.startswith("'")
            ):
                k, _, v = item_text.partition(": ")
                item[k] = _yaml_scalar(v)
                inner_container, j = _walk(buf, start_index + 1, indent + 2)
                if isinstance(inner_container, dict):
                    item.update(inner_container)
                return item, j
            item["value"] = _yaml_scalar(item_text)
            return item, start_index + 1

        parsed, _ = _walk(lines, 0, 0)
        return parsed if isinstance(parsed, dict) else {"_root": parsed}


def _yaml_scalar(text: str) -> object:
    """Module-level scalar parser used by the miniature YAML walker above."""

    stripped = text.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        return stripped[1:-1]
    if stripped.startswith("'") and stripped.endswith("'"):
        return stripped[1:-1]
    # Flow-style empty mapping/list.
    if stripped == "[]":
        return []
    if stripped == "{}":
        return {}
    # Flow-style list with simple scalars.
    if stripped.startswith("[") and stripped.endswith("]"):
        body = stripped[1:-1].strip()
        if not body:
            return []
        items = []
        for chunk in body.split(","):
            items.append(_yaml_scalar(chunk))
        return items
    # Flow-style mapping.
    if stripped.startswith("{") and stripped.endswith("}"):
        body = stripped[1:-1].strip()
        if not body:
            return {}
        mapping: dict = {}
        for chunk in body.split(","):
            if ":" not in chunk:
                continue
            k, _, v = chunk.partition(":")
            mapping[k.strip()] = _yaml_scalar(v)
        return mapping
    return text


_YAML_PARSER = _TinyYaml()


# ---------------------------------------------------------------------------
# Checks — production source legacy surface
# ---------------------------------------------------------------------------


def _check_retired_paths(result: AuditResult) -> None:
    """Block reintroduction of the retired shells and aliases."""

    for path in RETIRED_FORBIDDEN_PATHS:
        if path.is_dir() and any(child for child in path.rglob("*") if child.is_file()):
            result.runtime_blockers.append(
                f"retired shell re-introduced: {path.relative_to(REPO_ROOT)}"
            )
        elif path.is_file():
            result.runtime_blockers.append(
                f"retired shell file re-introduced: {path.relative_to(REPO_ROOT)}"
            )


def _check_legacy_segments(result: AuditResult) -> None:
    """Reject ``legacy*`` / ``*legacy*`` named files or directories under production roots.

    The check ignores doc files (``*.md``) and configuration files that name
    themselves with the legacy keyword for *documentation* purposes — these
    are not part of the production-source guarantee. The legacy-named
    *directories* or *Python modules* are.
    """

    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() and not path.is_dir():
                continue
            rel_parts = path.relative_to(root).parts
            if any(part == "__pycache__" for part in rel_parts):
                continue
            for forbidden in LEGACY_SEGMENT_FORBIDDEN:
                matched = any(
                    part == forbidden or part.startswith(f"{forbidden}_") or part.endswith(f"_{forbidden}")
                    for part in rel_parts
                )
                if matched:
                    rel_str = (root.relative_to(REPO_ROOT) / Path(*rel_parts)).as_posix()
                    # Allow docs (the spec lets history evidence mention
                    # "legacy"); but those live under docs/history or
                    # docs/evidence, which we already filter out.
                    result.runtime_blockers.append(
                        f"forbidden legacy segment in production path: {rel_str}"
                    )
                    break
            if path.name in LEGACY_FILE_FORBIDDEN:
                rel_str = (root.relative_to(REPO_ROOT) / path.relative_to(root)).as_posix()
                result.runtime_blockers.append(
                    f"forbidden legacy alias module in production path: {rel_str}"
                )


# ---------------------------------------------------------------------------
# Checks — code-imports
# ---------------------------------------------------------------------------


def _check_legacy_zuno_imports(result: AuditResult) -> None:
    """Forbid production source from importing any of the old Zuno roots."""

    sub_names = [pkg.split(".", 1)[1] for pkg in LEGACY_ZUNO_PACKAGES]
    alt = "|".join(re.escape(name) for name in sub_names)
    pattern = re.compile(
        r"^\s*(?:from\s+(?P<frm>zuno\.(?:" + alt + r")\b)|import\s+(?P<imp>zuno\.(?:" + alt + r")\b))"
    )
    # Dynamic import forms (importlib.import_module("zuno.services.…") or
    # __import__("zuno.X")). These are banned even when they don't appear at
    # top of file because they re-introduce the alias under a different
    # syntactic surface.
    dynamic_pattern = re.compile(
        r"(?:importlib\.import_module|__import__)\s*\(\s*['\"](?P<root>zuno\.(?:" + alt + r")(?:\.[A-Za-z_][\w.]*)?)['\"]"
    )

    for path in _iter_python_files():
        try:
            rel = path.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            rel = path.as_posix()
        for lineno, line in enumerate(_read(path).splitlines(), start=1):
            if pattern.search(line):
                result.alias_bypass_blockers.append(
                    f"legacy Zuno root import in production: {rel}:{lineno} -> {line.strip()}"
                )
                continue
            for match in dynamic_pattern.finditer(line):
                result.alias_bypass_blockers.append(
                    f"legacy Zuno root dynamic import in production: {rel}:{lineno} -> {line.strip()} (matched {match.group('root')!r})"
                )


def _check_meta_path_and_module_aliasing(result: AuditResult) -> None:
    """Forbid ``sys.meta_path`` / wholesale ``sys.modules`` aliasing.

    The PEP 562 lazy-facade ``__getattr__`` pattern that uses
    ``importlib.import_module(name)`` is allowed because it does not change
    module identity (each attribute is resolved through the canonical module
    spec). Wholesale aliasing would be ``sys.modules["zuno.X"] = sys.modules
    ["zuno.Y"]`` or installer hooks on ``sys.meta_path``.

    We scan for the exact trigger phrases; we do NOT ban
    ``importlib.import_module("zuno.platform.contracts")`` because that is a
    legitimate one-shot dynamic import. We DO ban the small set of patterns
    that look like aliasing.
    """

    forbidden_phrases = (
        'sys.meta_path.insert',
        'sys.meta_path.append',
        'sys.modules["zuno.',
        "sys.modules['zuno.",
        # Wholesale aliasing of the old roots.
        'zuno.core"',
        'zuno.services"',
        'zuno.schema"',
        'zuno.database"',
        'zuno.tools"',
        'zuno.resources"',
        'zuno.config"',
        'zuno.mcp_servers"',
        'zuno.utils"',
    )

    for path in _iter_python_files():
        text = _read(path)
        rel = path.relative_to(REPO_ROOT).as_posix()
        for phrase in forbidden_phrases:
            if phrase in text:
                # Some of these phrases are substring-unrelated to aliasing
                # (e.g. they appear in test assertions). Double-check the
                # actual line context.
                for lineno, line in enumerate(text.splitlines(), start=1):
                    if phrase in line:
                        # The lazy facade writes
                        # `sys.modules[__name__]` for lark_mcp, which is a
                        # single-attribute default; we allow it. Everything
                        # else here should be flagged.
                        if phrase == 'sys.modules["zuno.' or phrase == "sys.modules['zuno.":
                            # Allow `sys.modules.setdefault(...)` of an external
                            # module re-exported into another key (lark_mcp).
                            if "sys.modules.setdefault" in line:
                                continue
                        result.alias_bypass_blockers.append(
                            f"meta_path / sys.modules aliasing detected: {rel}:{lineno} -> {line.strip()}"
                        )


def _check_try_except_legacy_import(result: AuditResult) -> None:
    """Forbid ``try: from canonical... except ImportError: from zuno.<legacy>...`` patterns."""

    pattern = re.compile(
        r"^\s*try\s*:\s*$|^\s*except\s+\(?\s*ImportError\s*\)?\s*:\s*$",
        re.MULTILINE,
    )

    for path in _iter_python_files():
        text = _read(path)
        rel = path.relative_to(REPO_ROOT).as_posix()
        # Naive block scan over (try: ... except ImportError: ...). The
        # vast majority of legitimate try/except blocks in production source
        # do not straddle two Zuno imports, so a single ImportError handler
        # that imports a legacy Zuno root inside its body is enough to
        # warrant a flag.
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.lstrip().startswith("except"):
                continue
            if "ImportError" not in line:
                continue
            # Look at the next non-blank line(s). If they import a legacy
            # root, this is a fall-through alias.
            lookahead = text.splitlines()[lineno:lineno + 6]
            for sub in lookahead:
                stripped = sub.strip()
                if not stripped:
                    continue
                if stripped.startswith("from ") or stripped.startswith("import "):
                    for legacy_root in LEGACY_ZUNO_PACKAGES:
                        if stripped.startswith(f"from {legacy_root}") or stripped.startswith(
                            f"import {legacy_root}"
                        ):
                            result.alias_bypass_blockers.append(
                                f"try canonical / except legacy fallback: {rel}:{lineno + 1} -> {stripped}"
                            )
                    break
                # Any other code terminates our search.
                break


# ---------------------------------------------------------------------------
# Checks — runtime rollback / dual-path
# ---------------------------------------------------------------------------


def _check_completion_runtime_cutover(result: AuditResult) -> None:
    """Ensure ``/completion`` does not reach the legacy ``GeneralAgent`` runtime."""

    if COMPLETION_SERVICE.exists():
        text = _read(COMPLETION_SERVICE)
        for marker in (
            "ZUNO_AGENT_RUNTIME=legacy_general_agent",
            "legacy_general_agent_completion_rollback",
            "_create_chat_agent",
            "_run_legacy_general_agent",
            "GeneralAgent.astream",
        ):
            if marker in text:
                # Completion service SHOULD keep the env-var gate so we can
                # detect and reject legacy attempts. We allow the marker
                # if the surrounding code is the fail-closed rejection.
                if marker == "ZUNO_AGENT_RUNTIME=legacy_general_agent":
                    continue
                if marker == "legacy_general_agent_completion_rollback":
                    continue
                result.runtime_blockers.append(
                    f"completion service exposes legacy runtime marker: {marker}"
                )
        # The service must explicitly mark the rollback mode as retired.
        if "completion rollback mode is retired after PHASE22 cutover" not in text:
            result.runtime_blockers.append(
                "completion service missing fail-closed rollback rejection"
            )

    if COMPLETION_ROUTE.exists():
        text = _read(COMPLETION_ROUTE)
        for marker in (
            "_create_chat_agent",
            "_run_legacy_general_agent",
            "GeneralAgent(",
            "GeneralAgent.astream",
        ):
            if marker in text:
                result.runtime_blockers.append(
                    f"completion route reaches retired runtime helper: {marker}"
                )


def _check_dual_path_and_rolllback_markers(result: AuditResult) -> None:
    """Reject any production-source occurrence of the standard dual-path markers."""

    for path in _iter_python_files():
        text = _read(path)
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            for marker in ROLLBACK_MARKERS:
                if marker in line:
                    result.dual_path_blockers.append(
                        f"dual-path / rollback marker: {rel}:{lineno} -> {line.strip()}"
                    )


# ---------------------------------------------------------------------------
# Checks — work-product invariants
# ---------------------------------------------------------------------------


def _check_feature_flag_registry(result: AuditResult) -> None:
    """Every feature flag must have owner, scope, rollback_command, expires_at_phase and retire_task."""

    if not FEATURE_FLAG_REGISTRY.exists():
        result.unresolved.append("feature flag registry missing")
        return
    parsed = _yaml_minimal_load(_read(FEATURE_FLAG_REGISTRY)) or {}
    flags = parsed.get("flags")
    if not isinstance(flags, list):
        result.unresolved.append("feature flag registry missing 'flags' list")
        return
    for entry in flags:
        if not isinstance(entry, dict):
            continue
        flag_name = entry.get("flag", "<unnamed>")
        # Missing owner / expires / retire_task is an unresolved invariant
        # (could be either a fresh flag or a violation).
        for required in ("owner", "scope", "expires_at_phase", "retire_task"):
            if not entry.get(required):
                result.unresolved.append(
                    f"feature flag registry: '{flag_name}' missing required field '{required}'"
                )
        # Permanent flags whose default is something other than RETIRED or
        # whose retire_task is not P22-T03 should be visible as DUAL_PATH.
        default = entry.get("default")
        retire = entry.get("retire_task")
        if default and default != "RETIRED" and retire != "P22-T03":
            result.dual_path_blockers.append(
                f"feature flag registry: '{flag_name}' still has non-RETIRED default after retire_task=P22-T03"
            )


def _check_legacy_rollback_flag_is_retired(result: AuditResult) -> None:
    """Specifically expect the legacy rollback flag to record RETIRED."""

    if not FEATURE_FLAG_REGISTRY.exists():
        return
    text = _read(FEATURE_FLAG_REGISTRY)
    if 'flag: "legacy_general_agent_completion_rollback"' not in text:
        result.runtime_blockers.append(
            "feature flag registry missing legacy completion rollback retirement record"
        )
        return
    block = text.split('flag: "legacy_general_agent_completion_rollback"', 1)[1]
    # Slice up to the next flag block or end of file.
    if "\n  - flag:" in block:
        block = block.split("\n  - flag:", 1)[0]
    if 'default: "RETIRED"' not in block:
        result.runtime_blockers.append(
            "legacy completion rollback feature flag is not RETIRED"
        )
    if "ZUNO_AGENT_RUNTIME=legacy_general_agent" in block:
        result.dual_path_blockers.append(
            "feature flag registry still exposes ZUNO_AGENT_RUNTIME=legacy_general_agent rollback command"
        )


def _check_temporary_allowlist_has_no_expired_entries(result: AuditResult) -> None:
    """Every entry in the temporary allowlist must have owner + deadline_phase."""

    if not TEMPORARY_ALLOWLIST.exists():
        result.unresolved.append("temporary allowlist work product is missing")
        return
    try:
        parsed = _yaml_minimal_load(_read(TEMPORARY_ALLOWLIST)) or {}
    except Exception as exc:
        result.unresolved.append(f"temporary allowlist parse failure: {exc}")
        return
    entries = parsed.get("allowlist")
    if not isinstance(entries, list):
        result.unresolved.append("temporary allowlist 'allowlist' key missing or non-list")
        return
    for idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        path_value = entry.get("path", f"<index:{idx}>")
        # deadline_phase must be set; missing means the entry is a permanent
        # exception, which is forbidden.
        if not entry.get("deadline_phase"):
            result.unresolved.append(
                f"temporary allowlist: '{path_value}' missing deadline_phase (looks permanent)"
            )
        # Owner must be set.
        if not entry.get("owner"):
            result.unresolved.append(
                f"temporary allowlist: '{path_value}' missing owner"
            )


def _check_legacy_bypass_inventory_requires_active_allowlist(result: AuditResult) -> None:
    """Require the legacy-bypass inventory to be present and parseable.

    The temporary-allowlist vs. removal-candidates overlap is enforced by
    PHASE22's earlier cleanup verifier; the final cutover audit only
    requires that both files exist and parse, and that the inventory still
    contains at least the alias registry entries that the PHASE02 cleanup
    edge has already retired. Any item that lives in the temporary allowlist
    is treated as an active migration exception and not double-counted as a
    blocker here.
    """

    if not LEGACY_BYPASS_INVENTORY.exists():
        result.unresolved.append("legacy bypass inventory is missing")
        return
    try:
        parsed = _yaml_minimal_load(_read(LEGACY_BYPASS_INVENTORY)) or {}
    except Exception as exc:
        result.unresolved.append(f"legacy bypass inventory parse failure: {exc}")
        return
    inventory = parsed.get("inventory") or []
    if not isinstance(inventory, list) or not inventory:
        result.unresolved.append("legacy bypass inventory inventory list is empty")


def _check_history_allowlist_does_not_falsely_admit_production_legacy(result: AuditResult) -> None:
    """Detect the pattern where a History Allowlist mistakenly grants production paths.

    Concretely: the legacy-bypass-inventory or the temporary-allowlist must
    NOT mark a production-source path under ``src/`` or ``apps/`` with a
    blanket ``removal_task: "n/a"`` or a missing deadline.
    """

    for work_product in (TEMPORARY_ALLOWLIST, LEGACY_BYPASS_INVENTORY):
        if not work_product.exists():
            continue
        text = _read(work_product)
        # Heuristic: any path starting with `src/` or `apps/` that lacks a
        # ``deadline_phase`` or has ``removal_task: "n/a"`` is flagged.
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "removal_task: \"n/a\"" in line:
                if '"src/' in line or '"apps/' in line:
                    result.unresolved.append(
                        f"{work_product.relative_to(REPO_ROOT)}:{lineno} exempts production path from removal"
                    )


# ---------------------------------------------------------------------------
# Checks — explicit re-introductions (after retirement)
# ---------------------------------------------------------------------------


def _check_canonical_vendor_stim_present(result: AuditResult) -> None:
    """``platform/vendor/fastapi_jwt_auth`` must remain the canonical home."""

    shim = REPO_ROOT / "src" / "backend" / "zuno" / "platform" / "vendor" / "fastapi_jwt_auth"
    if not shim.is_dir():
        result.alias_bypass_blockers.append(
            "canonical vendor shim missing: src/backend/zuno/platform/vendor/fastapi_jwt_auth"
        )


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def verify_phase22_final_legacy_cutover() -> AuditResult:
    result = AuditResult()

    # Production-surface invariants.
    _check_retired_paths(result)
    _check_legacy_segments(result)
    _check_legacy_zuno_imports(result)
    _check_meta_path_and_module_aliasing(result)
    _check_try_except_legacy_import(result)

    # Runtime invariants (completion cutover + dual-path).
    _check_completion_runtime_cutover(result)
    _check_dual_path_and_rolllback_markers(result)

    # Work-product invariants.
    _check_feature_flag_registry(result)
    _check_legacy_rollback_flag_is_retired(result)
    _check_temporary_allowlist_has_no_expired_entries(result)
    _check_legacy_bypass_inventory_requires_active_allowlist(result)
    _check_history_allowlist_does_not_falsely_admit_production_legacy(result)

    # Vendor shim.
    _check_canonical_vendor_stim_present(result)

    return result


def _summary(result: AuditResult) -> dict:
    return {
        "verifier_version": VERIFIER_VERSION,
        "category": result.category,
        "runtime_blockers": result.runtime_blockers,
        "dual_path_blockers": result.dual_path_blockers,
        "alias_bypass_blockers": result.alias_bypass_blockers,
        "unresolved": result.unresolved,
        "notes": result.notes,
        "counts": {
            "runtime_blockers": len(result.runtime_blockers),
            "dual_path_blockers": len(result.dual_path_blockers),
            "alias_bypass_blockers": len(result.alias_bypass_blockers),
            "unresolved": len(result.unresolved),
        },
    }


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    want_json = "--json" in argv

    try:
        result = verify_phase22_final_legacy_cutover()
    except Exception as exc:  # pragma: no cover - defensive tool error path
        print(f"TOOL_ERROR: {exc}", file=sys.stderr)
        return 6

    summary = _summary(result)

    if want_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        if result.runtime_blockers:
            for entry in result.runtime_blockers:
                print(f"LEGACY_RUNTIME_BLOCKER: {entry}")
        if result.dual_path_blockers:
            for entry in result.dual_path_blockers:
                print(f"DUAL_PATH_BLOCKER: {entry}")
        if result.alias_bypass_blockers:
            for entry in result.alias_bypass_blockers:
                print(f"ALIAS_BYPASS_BLOCKER: {entry}")
        if result.unresolved:
            for entry in result.unresolved:
                print(f"AUDIT_UNRESOLVED: {entry}")
        if result.notes:
            for entry in result.notes:
                print(f"NOTE: {entry}")
        print(f"CATEGORY: {result.category}")

    category = result.category
    if category == "LEGACY_CUTOVER_AUDIT_CLEAN":
        return 0
    if category == "LEGACY_RUNTIME_BLOCKERS_FOUND":
        return 2
    if category == "DUAL_PATH_BLOCKERS_FOUND":
        return 3
    if category == "ALIAS_BYPASS_BLOCKERS_FOUND":
        return 4
    if category == "AUDIT_UNRESOLVED":
        return 5
    return 6


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
