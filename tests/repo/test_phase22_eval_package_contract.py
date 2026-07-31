from __future__ import annotations

import importlib
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[2]
EVALS_DIR = REPO_ROOT / "tools" / "evals" / "zuno" / "rag_eval"
SRC_BACKEND_DIR = REPO_ROOT / "src" / "backend"


def test_eval_files_do_not_contain_repetitive_sys_path_injection() -> None:
    violations: list[str] = []
    for path in EVALS_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if 'curr.name != "Zuno"' in text:
            violations.append(f"{path.name} contains curr.name != 'Zuno'")
        if "zuno.evals" in text and "test" not in path.name:
            if "sys.modules" in text or "__path__" in text:
                violations.append(f"{path.name} contains zuno.evals alias injection")

    assert violations == []


def test_library_modules_do_not_call_sys_path_insert() -> None:
    library_modules = [
        "__init__.py",
        "analyze_profile_deltas.py",
        "build_mixed_tuning_manifest.py",
        "generate_contract_review_scale_corpus.py",
        "metrics.py",
        "paths.py",
        "prepare_python_notes_corpus.py",
        "public_enterprise_datasets.py",
        "summarize_eval_profiles.py",
    ]
    violations: list[str] = []
    for name in library_modules:
        path = EVALS_DIR / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            if "sys.path.insert" in text:
                violations.append(f"{name} calls sys.path.insert")

    assert violations == []


def test_src_backend_does_not_import_tools_evals() -> None:
    violations: list[str] = []
    for path in SRC_BACKEND_DIR.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "tools.evals" in text:
            violations.append(str(path.relative_to(REPO_ROOT)))

    assert violations == []


def test_src_backend_zuno_evals_does_not_exist() -> None:
    legacy_evals_dir = SRC_BACKEND_DIR / "zuno" / "evals"
    assert not legacy_evals_dir.exists()


def test_benchmark_runner_can_be_imported_cleanly() -> None:
    mod = importlib.import_module("tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark")
    assert hasattr(mod, "run_enterprise_rag_paired_benchmark")


def test_benchmark_runner_help_command_succeeds() -> None:
    proc = subprocess.run(
        ["python", "-m", "tools.evals.zuno.rag_eval.run_enterprise_rag_paired_benchmark", "--help"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "EnterpriseRAG Paired Benchmark" in proc.stdout or "--questions-file" in proc.stdout


def test_no_global_pth_dependence_in_repo() -> None:
    pth_files = list(REPO_ROOT.glob("*.pth"))
    assert pth_files == []
