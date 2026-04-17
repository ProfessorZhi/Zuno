import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_web_start_launcher_does_not_rebuild_on_plain_start():
    content = (REPO_ROOT / "launchers" / "_Zuno-Web-Common.cmd").read_text(encoding="utf-8")
    start_block = re.search(r"^:start\s*(.*?)^:stop\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert start_block is not None
    assert "docker compose up -d" in start_block.group(1)
    assert "docker compose up --build -d" not in start_block.group(1)


def test_scripts_start_does_not_install_dependencies_by_default():
    content = (REPO_ROOT / "scripts" / "start.py").read_text(encoding="utf-8")

    assert "args.install_deps" in content
    assert "if args.install_deps:" in content


def test_desktop_stop_stops_backend_services_too():
    content = (REPO_ROOT / "launchers" / "_Zuno-Desktop-Common.cmd").read_text(encoding="utf-8")
    stop_block = re.search(r"^:stop\s*(.*?)^:rebuild\s*$", content, flags=re.MULTILINE | re.DOTALL)

    assert stop_block is not None
    assert "call :stop_backend" in stop_block.group(1)
