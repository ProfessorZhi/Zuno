import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_web_start_launcher_does_not_rebuild_on_plain_start():
    content = (REPO_ROOT / "launchers" / "_Zuno-Web-Common.cmd").read_text(encoding="utf-8")
    start_block = re.search(r"^:start\s*(.*?)^:stop\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert start_block is not None
    assert "docker compose up -d --remove-orphans" in start_block.group(1)
    assert "docker compose up --build -d" not in start_block.group(1)
    assert 'call :wait_http "http://127.0.0.1:7860/health" "Backend API" 90' in start_block.group(1)
    assert 'call :wait_http "http://127.0.0.1:8090" "Web frontend" 90' in start_block.group(1)


def test_scripts_start_does_not_install_dependencies_by_default():
    content = (REPO_ROOT / "tools" / "scripts" / "start.py").read_text(encoding="utf-8")

    assert "args.install_deps" in content
    assert "if args.install_deps:" in content


def test_desktop_stop_stops_backend_services_too():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    stop_block = re.search(r"^:launcher_stop\s*(.*?)^:launcher_rebuild\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert stop_block is not None
    assert "call :stopBackend" in stop_block.group(1)
    assert "DESKTOP_ELECTRON_EXE" in content
    assert "call :cleanup_processes" in stop_block.group(1)
    assert "_Zuno-Desktop-Cleanup.ps1" in content
    assert "docker compose down --remove-orphans" in content


def test_desktop_start_uses_direct_vite_and_electron_runtime():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    helper = (REPO_ROOT / "launchers" / "_Zuno-Desktop-StartElectron.ps1").read_text(encoding="utf-8")

    assert "node_modules\\.bin\\vite.cmd" in content
    assert "call :recordListeningPid \"%DESKTOP_FRONTEND_PORT%\" \"%FRONTEND_PID_FILE%\"" in content
    assert "_Zuno-Desktop-StartElectron.ps1" in content
    assert "node_modules\\electron\\dist\\electron.exe" in helper
    assert "Remove-Item Env:ELECTRON_RUN_AS_NODE" in helper
    assert "CreateDirectory" in helper
    assert "call :startSequence" in content
    assert "-WindowStyle Normal" in helper


def test_desktop_launcher_uses_external_electron_helper_not_batch_label():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")

    assert "call :startElectron" not in content
    assert "_Zuno-Desktop-StartElectron.ps1" in content


def test_desktop_cleanup_uses_external_helper_and_targets_launcher_processes():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    helper = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Cleanup.ps1").read_text(encoding="utf-8")

    assert "_Zuno-Desktop-Cleanup.ps1" in content
    assert 'powershell -NoProfile -ExecutionPolicy Bypass -File "%CLEANUP_HELPER%"' in content
    assert "Zuno-Desktop-Start.cmd" in helper
    assert "Zuno-Desktop-Stop.cmd" in helper
    assert "Stop-Process -Id" in helper
    assert "[int]$TargetPid" in helper
    assert "Stop-ProcessTree -TargetPid" in helper


def test_legacy_desktop_forwarders_target_current_launcher_names():
    start_bat = (REPO_ROOT / "tools" / "scripts" / "zuno-start.bat").read_text(encoding="utf-8")
    stop_bat = (REPO_ROOT / "tools" / "scripts" / "zuno-stop.bat").read_text(encoding="utf-8")
    rebuild_bat = (REPO_ROOT / "tools" / "scripts" / "zuno-rebuild-start.bat").read_text(encoding="utf-8")
    full_rebuild_bat = (REPO_ROOT / "tools" / "scripts" / "zuno-clean-rebuild-start.bat").read_text(encoding="utf-8")

    assert "Zuno-Desktop-Start.cmd" in start_bat
    assert "Zuno-Desktop-Stop.cmd" in stop_bat
    assert "Zuno-Desktop-Rebuild.cmd" in rebuild_bat
    assert "Zuno-Desktop-Full-Rebuild.cmd" in full_rebuild_bat
    assert "Zuno-Start.cmd" not in start_bat
    assert "Zuno-Stop.cmd" not in stop_bat
    assert "Zuno-Rebuild" not in rebuild_bat


def test_desktop_shortcuts_only_pause_on_failure():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    start_block = re.search(r"^:launcher_start\s*(.*?)^:launcher_stop\s*$", content, flags=re.MULTILINE | re.DOTALL)
    stop_block = re.search(r"^:launcher_stop\s*(.*?)^:launcher_rebuild\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert start_block is not None
    assert stop_block is not None
    assert re.search(r"if errorlevel 1\s*\([\s\S]*pause[\s\S]*exit /b 1[\s\S]*\)\s*exit /b 0", start_block.group(1))
    assert "pause\nexit /b 0" not in stop_block.group(1).replace("\r\n", "\n")


def test_web_shortcuts_only_pause_on_failure():
    content = (REPO_ROOT / "launchers" / "_Zuno-Web-Common.cmd").read_text(encoding="utf-8")
    start_block = re.search(r"^:start\s*(.*?)^:stop\s*$", content, flags=re.MULTILINE | re.DOTALL)
    stop_block = re.search(r"^:stop\s*(.*?)^:rebuild\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert start_block is not None
    assert stop_block is not None
    assert re.search(r"if errorlevel 1 goto :fail", start_block.group(1))
    assert "pause\nexit /b 0" not in stop_block.group(1).replace("\r\n", "\n")
    assert "pause" not in content.split(":fail", 1)[0]


def test_docker_stack_includes_neo4j_runtime():
    compose = (REPO_ROOT / "infra" / "docker" / "docker-compose.yml").read_text(encoding="utf-8")
    local_config = (REPO_ROOT / "infra" / "docker" / "docker_config.example.yaml").read_text(encoding="utf-8")

    assert "\n  neo4j:\n" in compose
    assert "image: neo4j:5-community" in compose
    assert "neo4j:\n        condition: service_healthy" in compose
    assert "neo4j:" in local_config
    assert "enabled: true" in local_config
    assert "bolt://neo4j:7687" in local_config


def test_compose_launchers_remove_orphans_on_lifecycle_commands():
    desktop = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    web = (REPO_ROOT / "launchers" / "_Zuno-Web-Common.cmd").read_text(encoding="utf-8")

    assert "docker compose up -d --remove-orphans postgres redis neo4j minio backend" in desktop
    assert "docker compose down --remove-orphans" in desktop
    assert "docker compose up -d --remove-orphans" in web
    assert "docker compose up --build -d --remove-orphans" in web
    assert web.count("docker compose down --remove-orphans") >= 2
