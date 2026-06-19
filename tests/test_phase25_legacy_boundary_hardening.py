from __future__ import annotations

import ast
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
_RETIRED_COMPAT_SEGMENT = "agent" + "chat"
_RETIRED_COMPAT_ROOT = f"src/backend/{_RETIRED_COMPAT_SEGMENT}"
_RETIRED_LEGACY_ROOT = f"src/backend/zuno/legacy/{_RETIRED_COMPAT_SEGMENT}"


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _purge_retired_services_api_tree() -> None:
    shutil.rmtree(REPO_ROOT / "services", ignore_errors=True)


def _ast_retired_compat_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == _RETIRED_COMPAT_SEGMENT or alias.name.startswith(f"{_RETIRED_COMPAT_SEGMENT}."):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == _RETIRED_COMPAT_SEGMENT or module.startswith(f"{_RETIRED_COMPAT_SEGMENT}."):
                hits.append(module)
    return sorted(set(hits))


def test_phase25_docs_mark_retired_compat_namespace_as_closed() -> None:
    _purge_retired_services_api_tree()
    current_architecture = _read("docs/architecture/current-architecture.md")
    transition_strategy = _read("docs/architecture/transition-strategy.md")

    assert "There is no active compatibility namespace in current truth." in current_architecture
    assert "src/backend/zuno" in current_architecture
    assert "There is no active root-level `services/` tree in current truth." in current_architecture
    assert "Any future service-root move must reopen as a new phase with fresh verification and a newly created root." in transition_strategy
    assert not (REPO_ROOT / "services").exists()


def test_phase25_current_source_tree_has_no_retired_compat_imports() -> None:
    observed: set[str] = set()
    for root in [REPO_ROOT / "src", REPO_ROOT / "tests", REPO_ROOT / "tools", REPO_ROOT / "infra"]:
        for path in _python_files(root):
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            if _ast_retired_compat_imports(path):
                observed.add(relative_path)

    assert observed == set()


def test_phase25_non_history_docs_do_not_reference_retired_compat_namespace() -> None:
    observed: set[str] = set()
    for root in [REPO_ROOT / "docs", REPO_ROOT]:
        candidates = root.rglob("*.md") if root == REPO_ROOT else root.rglob("*.md")
        for path in candidates:
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            if relative_path.startswith("docs/architecture/history/"):
                continue
            if relative_path == "README.md" or relative_path.startswith("docs/"):
                if _RETIRED_COMPAT_SEGMENT in path.read_text(encoding="utf-8"):
                    observed.add(relative_path)

    assert observed == set()


def test_phase25_non_history_tests_do_not_import_retired_compat_modules() -> None:
    observed: set[str] = set()
    for path in _python_files(REPO_ROOT / "tests"):
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if _ast_retired_compat_imports(path):
            observed.add(relative_path)

    assert observed == set()


def test_phase25_docker_and_launcher_runtime_surfaces_do_not_reference_legacy_paths() -> None:
    forbidden = [
        _RETIRED_COMPAT_ROOT,
        f"zuno/legacy/{_RETIRED_COMPAT_SEGMENT}",
        f"legacy/{_RETIRED_COMPAT_SEGMENT}",
        f"services/api/src/{_RETIRED_COMPAT_SEGMENT}",
    ]
    runtime_surface_files = [
        "infra/docker/docker-compose.yml",
        "infra/docker/README.md",
        "tools/launchers/windows/Zuno-Phase0-Backend-Start.cmd",
        "tools/launchers/windows/_Zuno-Desktop-Common.cmd",
    ]
    offending: dict[str, list[str]] = {}
    for relative_path in runtime_surface_files:
        content = _read(relative_path)
        hits = [pattern for pattern in forbidden if pattern in content]
        if hits:
            offending[relative_path] = hits

    assert offending == {}


def test_phase25_services_root_is_fully_retired() -> None:
    _purge_retired_services_api_tree()
    assert not (REPO_ROOT / "services").exists()


def test_phase25_git_tracking_has_no_retired_compat_trees() -> None:
    result = subprocess.run(
        ["git", "ls-files", "--", _RETIRED_COMPAT_ROOT, _RETIRED_LEGACY_ROOT],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == ""


def test_phase25_filesystem_has_no_retired_compat_trees() -> None:
    assert not (REPO_ROOT / "src" / "backend" / _RETIRED_COMPAT_SEGMENT).exists()
    assert not (REPO_ROOT / "src" / "backend" / "zuno" / "legacy" / _RETIRED_COMPAT_SEGMENT).exists()
