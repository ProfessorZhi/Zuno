from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORK_PRODUCTS = REPO_ROOT / ".agent" / "programs" / "work-products"

ALLOWED_FLAG_STATES = [
    "DECLARED",
    "SHADOW",
    "CANARY",
    "DEFAULT_NEW",
    "ROLLBACK_WINDOW",
    "RETIRED",
]
ALLOWED_TRANSITIONS = {
    "DECLARED": {"SHADOW"},
    "SHADOW": {"CANARY", "RETIRED"},
    "CANARY": {"DEFAULT_NEW", "ROLLBACK_WINDOW"},
    "DEFAULT_NEW": {"ROLLBACK_WINDOW", "RETIRED"},
    "ROLLBACK_WINDOW": {"DEFAULT_NEW", "RETIRED"},
    "RETIRED": set(),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _blocks(text: str, marker: str) -> list[str]:
    result: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if line.startswith(marker):
            if current:
                result.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        result.append("\n".join(current))
    return result


def _field(block: str, name: str) -> str | None:
    match = re.search(rf'(?m)^\s+{re.escape(name)}:\s+"?([^"\n]+)"?\s*$', block)
    return match.group(1).strip() if match else None


def _path_values(text: str) -> set[str]:
    return set(re.findall(r'(?m)^\s+- path: "([^"]+)"', text))


class FlagDecision:
    def __init__(self, flag: str, current: str, desired: str, rollback_command: str) -> None:
        self.flag = flag
        self.current = current
        self.desired = desired
        self.rollback_command = rollback_command


class FeatureFlagStateMachine:
    def __init__(self, registry_text: str) -> None:
        self.registry_text = registry_text
        self.flags = self._parse_flags(registry_text)

    @staticmethod
    def _parse_flags(text: str) -> dict[str, dict[str, str]]:
        parsed: dict[str, dict[str, str]] = {}
        for block in _blocks(text, "  - flag: "):
            name_match = re.match(r'\s+- flag:\s+"([^"]+)"', block)
            if not name_match:
                continue
            name = name_match.group(1)
            parsed[name] = {
                "owner": _field(block, "owner") or "",
                "scope": _field(block, "scope") or "",
                "default": _field(block, "default") or "",
                "rollback_command": _field(block, "rollback_command") or "",
                "expires_at_phase": _field(block, "expires_at_phase") or "",
                "retire_task": _field(block, "retire_task") or "",
                "domain_fact_owner": _field(block, "domain_fact_owner") or "",
            }
        return parsed

    def validate(self) -> list[str]:
        errors: list[str] = []
        if "allowed_states: [DECLARED, SHADOW, CANARY, DEFAULT_NEW, ROLLBACK_WINDOW, RETIRED]" not in self.registry_text:
            errors.append("feature flag registry missing canonical lifecycle states")
        for name, flag in self.flags.items():
            if flag["default"] not in ALLOWED_FLAG_STATES:
                errors.append(f"{name} has invalid default state: {flag['default']}")
            if flag["domain_fact_owner"] == "feature_flag":
                errors.append(f"{name} illegally owns domain facts")
            for field in ["owner", "scope", "rollback_command", "expires_at_phase", "retire_task"]:
                if not flag[field]:
                    errors.append(f"{name} missing {field}")
            if flag["retire_task"] != "P22-T03":
                errors.append(f"{name} must retire through P22-T03")
        return errors

    def decide_transition(self, flag: str, desired: str) -> FlagDecision:
        if flag not in self.flags:
            raise KeyError(f"unknown feature flag: {flag}")
        current = self.flags[flag]["default"]
        if desired not in ALLOWED_TRANSITIONS[current]:
            raise ValueError(f"illegal transition for {flag}: {current} -> {desired}")
        return FlagDecision(
            flag=flag,
            current=current,
            desired=desired,
            rollback_command=self.flags[flag]["rollback_command"],
        )


class TemporaryAllowlistGuard:
    def __init__(self, allowlist_text: str, legacy_text: str) -> None:
        self.allowlist_text = allowlist_text
        self.legacy_text = legacy_text
        self.allowlist_paths = _path_values(allowlist_text)
        self.legacy_paths = _path_values(legacy_text)

    def validate(self) -> list[str]:
        errors: list[str] = []
        missing = sorted(self.legacy_paths - self.allowlist_paths)
        if missing:
            errors.append(f"temporary allowlist missing legacy paths: {missing[:10]}")
        if 'new_bypass_default: "fail"' not in self.allowlist_text:
            errors.append("temporary allowlist must fail closed for new bypasses")
        for block in _blocks(self.allowlist_text, "  - path: "):
            for field in ["owner", "test", "removal_task", "deadline_phase"]:
                if f"{field}:" not in block:
                    errors.append(f"allowlist entry missing {field}: {block.splitlines()[0]}")
        return errors

    def assert_allowed(self, path: str) -> None:
        if path not in self.allowlist_paths:
            raise PermissionError(f"new bypass path is not allowlisted: {path}")


class DataCutoverController:
    def __init__(self, matrix_text: str) -> None:
        self.matrix_text = matrix_text
        self.entries = _blocks(matrix_text, "  - data_owner: ")

    def validate(self) -> list[str]:
        errors: list[str] = []
        if 'default_dual_write: "forbidden_without_coordinator_decision"' not in self.matrix_text:
            errors.append("data cutover matrix must forbid dual write by default")
        for block in self.entries:
            for field in ["source", "target", "transform", "hash", "backfill_chunk", "verification", "rollback", "retention", "target_phase", "removal_task"]:
                if f"{field}:" not in block:
                    errors.append(f"data cutover entry missing {field}: {block.splitlines()[0]}")
        return errors

    def dry_run_hashes(self) -> dict[str, str]:
        result: dict[str, str] = {}
        for block in self.entries:
            owner = _field(block, "data_owner") or block.splitlines()[0].split(":", 1)[1].strip().strip('"')
            canonical = "\n".join(line.strip() for line in block.splitlines())
            result[owner] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return result


class RollbackDrillChecker:
    REQUIRED_PHRASES = [
        "Tool UNKNOWN",
        "forward-fix",
        "P22-T03",
        "HTTP 2xx, SSE close, Queue ACK, Object Commit and Audit Delivery",
    ]

    def __init__(self, playbook_text: str) -> None:
        self.playbook_text = playbook_text

    def validate(self) -> list[str]:
        errors = [f"rollback playbook missing phrase: {phrase}" for phrase in self.REQUIRED_PHRASES if phrase not in self.playbook_text]
        if "Security" not in self.playbook_text or "Budget" not in self.playbook_text:
            errors.append("rollback playbook must preserve Security and Budget boundaries")
        return errors


def verify_phase02_runtime_controls() -> list[str]:
    errors: list[str] = []
    flags = FeatureFlagStateMachine(_read(WORK_PRODUCTS / "feature-flag-registry.yaml"))
    allowlist = TemporaryAllowlistGuard(
        _read(WORK_PRODUCTS / "temporary-allowlist.yaml"),
        _read(WORK_PRODUCTS / "legacy-bypass-inventory.yaml"),
    )
    cutover = DataCutoverController(_read(WORK_PRODUCTS / "data-cutover-matrix.yaml"))
    rollback = RollbackDrillChecker(_read(WORK_PRODUCTS / "rollback-recovery-playbook.md"))

    errors.extend(flags.validate())
    errors.extend(allowlist.validate())
    errors.extend(cutover.validate())
    errors.extend(rollback.validate())

    for flag, desired in [
        ("product_api_v1_adapter", "SHADOW"),
        ("workspace_projection_stream_v1", "SHADOW"),
        ("legacy_general_agent_completion_rollback", "RETIRED"),
        ("tool_runtime_readonly_gateway", "SHADOW"),
        ("postgres_domain_uow_shadow", "SHADOW"),
    ]:
        try:
            decision = flags.decide_transition(flag, desired)
        except (KeyError, ValueError) as exc:
            errors.append(str(exc))
        else:
            if not decision.rollback_command:
                errors.append(f"{flag} transition lacks rollback command")

    try:
        allowlist.assert_allowed("src/backend/zuno/platform/compatibility/legacy_aliases.py")
        allowlist.assert_allowed("src/backend/zuno/platform/compatibility/legacy/__init__.py")
    except PermissionError as exc:
        errors.append(str(exc))

    if len(cutover.dry_run_hashes()) < 6:
        errors.append("data cutover dry run must cover at least six owners")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PHASE02 executable compatibility controls.")
    parser.add_argument("--check", action="store_true", help="run all PHASE02 executable control checks")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")
    errors = verify_phase02_runtime_controls()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE02 executable compatibility controls failed.")
        return 1
    print("PHASE02 executable compatibility controls passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
