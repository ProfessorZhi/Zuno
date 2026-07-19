from __future__ import annotations

import argparse
import ast
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY = REPO_ROOT / ".agent" / "programs" / "work-products" / "phase07-provider-bypass-inventory.yaml"
SOURCE_ROOT = REPO_ROOT / "src" / "backend" / "zuno"

PROVIDER_MODULES = {
    "anthropic",
    "langchain_openai",
    "openai",
}
PROVIDER_SYMBOLS = {
    "Anthropic",
    "AsyncAnthropic",
    "AsyncOpenAI",
    "ChatOpenAI",
    "OpenAI",
}
ALLOWED_PREFIXES = {
    "src/backend/zuno/platform/model_gateway",
    "src/backend/zuno/platform/compatibility/vendor",
}
TYPE_ONLY_ALLOWED_MODULES = {
    "openai.types",
}


def _relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _is_allowed(relative: str) -> bool:
    return any(relative.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def _is_type_only_module(module: str) -> bool:
    return any(module == allowed or module.startswith(f"{allowed}.") for allowed in TYPE_ONLY_ALLOWED_MODULES)


def _provider_hits(path: Path) -> set[str]:
    relative = _relative(path)
    if _is_allowed(relative):
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return {f"syntax-error:{exc.lineno}"}
    hits: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in PROVIDER_MODULES and not _is_type_only_module(alias.name):
                    hits.add(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            root = module.split(".", 1)[0]
            if root in PROVIDER_MODULES and not _is_type_only_module(module):
                names = ", ".join(alias.name for alias in node.names)
                hits.add(f"from {module} import {names}")
        elif isinstance(node, ast.Call):
            function = node.func
            name = ""
            if isinstance(function, ast.Name):
                name = function.id
            elif isinstance(function, ast.Attribute):
                name = function.attr
            if name in PROVIDER_SYMBOLS:
                hits.add(f"call {name}")
    return hits


def current_bypass_inventory() -> dict[str, list[str]]:
    inventory: dict[str, list[str]] = {}
    for path in SOURCE_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        hits = sorted(_provider_hits(path))
        if hits:
            inventory[_relative(path)] = hits
    return inventory


def _load_expected_paths() -> set[str]:
    if not INVENTORY.exists():
        return set()
    data = yaml.safe_load(INVENTORY.read_text(encoding="utf-8")) or {}
    return set(data.get("known_bypass_paths") or [])


def verify_model_gateway_bypass(*, strict: bool = False) -> list[str]:
    errors: list[str] = []
    current = current_bypass_inventory()
    current_paths = set(current)
    if strict:
        for path, hits in sorted(current.items()):
            errors.append(f"provider SDK bypass remains: {path}: {', '.join(hits)}")
        return errors
    expected_paths = _load_expected_paths()
    missing_from_inventory = sorted(current_paths - expected_paths)
    stale_inventory = sorted(expected_paths - current_paths)
    if missing_from_inventory:
        errors.append(f"new untracked provider bypass paths: {missing_from_inventory!r}")
    if stale_inventory:
        errors.append(f"stale provider bypass inventory paths: {stale_inventory!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="require zero provider SDK bypasses")
    parser.add_argument("--list", action="store_true", help="print current bypass inventory")
    args = parser.parse_args()
    current = current_bypass_inventory()
    if args.list:
        for path, hits in sorted(current.items()):
            print(f"{path}: {', '.join(hits)}")
    errors = verify_model_gateway_bypass(strict=args.strict)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Model Gateway bypass verification failed.")
        return 1
    mode = "strict" if args.strict else "inventory"
    print(f"Model Gateway bypass {mode} verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
