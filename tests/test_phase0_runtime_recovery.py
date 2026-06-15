from __future__ import annotations

import subprocess
import sys
import asyncio
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _run_backend_python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, r'{BACKEND_ROOT}'); "
                + code
            ),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_phase0_backend_entry_file_is_restored_under_src_backend() -> None:
    result = _run_backend_python("import zuno.main; print(zuno.main.__file__)")

    assert result.returncode == 0, result.stderr
    assert "src\\backend\\zuno\\main.py" in result.stdout


def test_phase0_local_start_script_uses_src_backend_startup_path() -> None:
    content = (REPO_ROOT / "tools" / "scripts" / "start.py").read_text(encoding="utf-8")

    assert 'BACKEND_DIR = PROJECT_ROOT / "services" / "api"' not in content
    assert 'BACKEND_DIR = PROJECT_ROOT' in content
    assert '"--app-dir", "src/backend", "zuno.main:app"' in content


def test_phase0_backend_root_keeps_high_value_runtime_imports_working() -> None:
    result = _run_backend_python(
        (
            "from zuno.core.graphs.domain_qa_graph import DomainQAGraph; "
            "from zuno.services.retrieval.orchestrator import RetrievalOrchestrator; "
            "from zuno.services.graphrag.retriever import GraphRetriever; "
            "from zuno.services.domain_pack.loader import load_domain_pack; "
            "print(DomainQAGraph.__name__, RetrievalOrchestrator.__name__, GraphRetriever.__name__, callable(load_domain_pack))"
        )
    )

    assert result.returncode == 0, result.stderr
    assert "DomainQAGraph RetrievalOrchestrator GraphRetriever True" in result.stdout


def test_phase0_readme_exposes_backend_recovery_start_and_verification() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860" in content
    assert "pytest tests/test_phase0_runtime_recovery.py" in content


def test_phase0_runtime_recovery_verifier_script_passes() -> None:
    result = subprocess.run(
        [sys.executable, "tools/scripts/verify_phase0_runtime_recovery.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Phase 0 runtime recovery verification passed." in result.stdout


def test_phase0_zuno_bootstrap_can_find_service_surface_in_container_like_layout(tmp_path) -> None:
    sys.path.insert(0, str(BACKEND_ROOT))
    import zuno

    package_root = tmp_path / "app" / "legacy_backend" / "zuno"
    service_root = tmp_path / "app" / "src" / "zuno"
    package_root.mkdir(parents=True)
    service_root.mkdir(parents=True)
    (service_root / "main.py").write_text("app = object()\n", encoding="utf-8")

    resolved = zuno._find_service_api_root(package_root)

    assert resolved == tmp_path / "app" / "src"


def test_phase0_dockerfile_uses_src_backend_startup_path() -> None:
    content = (REPO_ROOT / "infra" / "docker" / "Dockerfile").read_text(encoding="utf-8")

    assert "ENV PYTHONPATH=/app/legacy_backend:/app/src:/app" in content
    assert 'CMD ["uvicorn", "--app-dir", "legacy_backend", "zuno.main:app"' in content


def test_phase0_compose_exposes_postgres_to_local_backend_startup() -> None:
    content = (REPO_ROOT / "infra" / "docker" / "docker-compose.yml").read_text(encoding="utf-8")

    assert '- "5432:5432"' in content


def test_phase0_init_config_fails_fast_when_database_bootstrap_fails(monkeypatch) -> None:
    sys.path.insert(0, str(BACKEND_ROOT))
    import zuno.main as zuno_main
    import zuno.database.init_data as init_data

    calls: list[str] = []

    async def fake_initialize_app_settings():
        calls.append("settings")

    def fake_configure_langsmith():
        calls.append("langsmith")

    async def fake_init_database():
        calls.append("init_database")
        return False

    async def fake_init_default_agent():
        calls.append("init_default_agent")

    monkeypatch.setattr(zuno_main, "initialize_app_settings", fake_initialize_app_settings)
    monkeypatch.setattr(zuno_main, "configure_langsmith", fake_configure_langsmith)
    monkeypatch.setattr(init_data, "init_database", fake_init_database)
    monkeypatch.setattr(init_data, "init_default_agent", fake_init_default_agent)

    async def run():
        await zuno_main.init_config()

    try:
        asyncio.run(run())
        raised = None
    except RuntimeError as exc:
        raised = exc

    assert raised is not None
    assert "Database bootstrap failed" in str(raised)
    assert calls == ["settings", "langsmith", "init_database"]


def test_phase0_avatar_optional_startup_skips_when_storage_endpoint_unreachable(monkeypatch) -> None:
    sys.path.insert(0, str(BACKEND_ROOT))
    import zuno.database.init_data as init_data

    calls: list[str] = []

    monkeypatch.setattr(init_data, "_is_storage_endpoint_reachable", lambda: False)

    class DummyStorageClient:
        def list_files_in_folder(self, folder_path):
            calls.append(f"list:{folder_path}")
            return []

    monkeypatch.setattr(init_data, "storage_client", DummyStorageClient())

    asyncio.run(init_data.upload_user_avatars_storage())

    assert calls == []
