from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_public_backend_entrypoints_use_src_backend_truth() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    dockerfile = (REPO_ROOT / "infra/docker/Dockerfile").read_text(encoding="utf-8")
    start_script = (REPO_ROOT / "tools/scripts/start.py").read_text(encoding="utf-8")

    assert "uvicorn --app-dir src/backend zuno.main:app" in readme
    assert "cd services\\api" not in readme
    assert 'ENV PYTHONPATH=/app/src/backend:/app' in dockerfile
    assert 'CMD ["uvicorn", "--app-dir", "src/backend", "zuno.main:app"' in dockerfile
    assert '"--app-dir", "src/backend", "zuno.main:app"' in start_script


def test_top_level_zuno_package_does_not_bridge_to_service_api() -> None:
    zuno_root_init = (REPO_ROOT / "src/backend/zuno/__init__.py").read_text(encoding="utf-8")
    zuno_main = (REPO_ROOT / "src/backend/zuno/main.py").read_text(encoding="utf-8")

    assert "services/api/src" not in zuno_root_init
    assert "_find_service_api_root" not in zuno_root_init
    assert "from zuno.api.router import router" in zuno_main
    assert "from agentchat.main import app" not in zuno_main


def test_compat_and_eval_entrypoints_insert_backend_root_only() -> None:
    files_to_check = [
        "tests/compat/conftest.py",
        "tools/evals/zuno/rag_eval/ingest_prepared_corpus.py",
        "tools/evals/zuno/rag_eval/run_eval.py",
        "tools/evals/zuno/rag_eval/run_local_embedding_eval.py",
        "tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py",
        "tools/evals/zuno/rag_eval/run_stackless_local_eval.py",
        "tools/evals/zuno/contract_review_eval/run_contract_eval.py",
    ]

    for relative_path in files_to_check:
        content = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
        assert 'src" / "backend' in content or "src/backend" in content
        assert "services/api/src" not in content
        assert "legacy_backend" not in content
