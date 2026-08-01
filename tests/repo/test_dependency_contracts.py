import tomllib
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _requirements_packages() -> set[str]:
    packages: set[str] = set()
    for raw_line in (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split("==", 1)[0].split("[", 1)[0].strip().lower()
        packages.add(name)
    return packages


def test_docker_runtime_requirements_include_pyproject_runtime_plugins():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pyproject_deps = {
        name.lower()
        for name in pyproject["tool"]["poetry"]["dependencies"]
        if name.lower() != "python"
    }
    requirements = _requirements_packages()

    assert "langgraph-checkpoint-postgres" in pyproject_deps
    assert "langgraph-checkpoint-postgres" in requirements
