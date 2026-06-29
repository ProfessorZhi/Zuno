from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

LAZY_FACADES = [
    "src/backend/zuno/agent/__init__.py",
    "src/backend/zuno/agent/core/__init__.py",
    "src/backend/zuno/agent/core/agents/__init__.py",
    "src/backend/zuno/agent/context.py",
    "src/backend/zuno/agent/runtime.py",
    "src/backend/zuno/agent/state.py",
    "src/backend/zuno/agent/streaming.py",
    "src/backend/zuno/capability/__init__.py",
    "src/backend/zuno/knowledge/__init__.py",
    "src/backend/zuno/knowledge/citation.py",
    "src/backend/zuno/knowledge/evidence.py",
    "src/backend/zuno/knowledge/fusion/__init__.py",
    "src/backend/zuno/knowledge/graphrag/__init__.py",
    "src/backend/zuno/knowledge/query_service.py",
    "src/backend/zuno/knowledge/retrieval/__init__.py",
    "src/backend/zuno/knowledge/trace.py",
    "src/backend/zuno/memory/__init__.py",
    "src/backend/zuno/platform/__init__.py",
    "src/backend/zuno/platform/storage/__init__.py",
]


def _literal_str_set(node: ast.AST, relative_path: str) -> set[str]:
    assert isinstance(node, (ast.List, ast.Tuple)), f"{relative_path}: __all__ must be literal"
    values: set[str] = set()
    for element in node.elts:
        assert isinstance(element, ast.Constant) and isinstance(element.value, str), (
            f"{relative_path}: __all__ must contain only string literals"
        )
        values.add(element.value)
    return values


def _exported_names(tree: ast.Module, relative_path: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    return _literal_str_set(node.value, relative_path)
    raise AssertionError(f"{relative_path}: missing literal __all__")


def _lazy_export_map_names(tree: ast.Module, relative_path: str) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name)
            and target.id in {"_EXPORT_TO_MODULE", "_LAZY_EXPORT_TO_MODULE"}
            for target in node.targets
        ):
            continue
        assert isinstance(node.value, ast.Dict), f"{relative_path}: lazy export map must be literal"
        for key in node.value.keys:
            assert isinstance(key, ast.Constant) and isinstance(key.value, str), (
                f"{relative_path}: lazy export map keys must be string literals"
            )
            names.add(key.value)
    return names


def _type_checking_imported_names(tree: ast.Module) -> set[str]:
    imported: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not isinstance(test, ast.Name) or test.id != "TYPE_CHECKING":
            continue
        for statement in ast.walk(node):
            if isinstance(statement, ast.ImportFrom):
                imported.update(alias.asname or alias.name for alias in statement.names)
    return imported


def test_lazy_facade_all_names_are_visible_to_static_analysis() -> None:
    for relative_path in LAZY_FACADES:
        path = REPO_ROOT / relative_path
        tree = ast.parse(path.read_text(encoding="utf-8"))
        exported = _exported_names(tree, relative_path)
        lazy_exports = _lazy_export_map_names(tree, relative_path)
        imported = _type_checking_imported_names(tree)
        assert exported == lazy_exports, f"{relative_path}: __all__ must match lazy export map"
        missing = sorted(exported - imported)
        assert not missing, f"{relative_path} missing TYPE_CHECKING imports: {missing}"
