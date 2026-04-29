import argparse
import os
import platform
import signal
import subprocess
import sys
import time
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
BACKEND_DIR = PROJECT_ROOT / "src" / "backend"
FRONTEND_DIR = PROJECT_ROOT / "src" / "frontend"
IS_WINDOWS = platform.system() == "Windows"

processes: list[subprocess.Popen] = []


def install_dependencies() -> None:
    requirements = PROJECT_ROOT / "requirements.txt"
    if not requirements.exists():
        print(f"[warn] Missing requirements file: {requirements}")
        return

    print(f"[deps] Installing Python dependencies from {requirements}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements)], check=True)


def start_process(command: list[str], cwd: Path, *, shell: bool = False) -> subprocess.Popen:
    print(f"[start] {' '.join(command)} (cwd: {cwd})")
    process = subprocess.Popen(command, cwd=str(cwd), shell=shell)
    processes.append(process)
    return process


def start_services() -> None:
    if not BACKEND_DIR.exists():
        raise FileNotFoundError(f"Backend directory not found: {BACKEND_DIR}")
    if not FRONTEND_DIR.exists():
        raise FileNotFoundError(f"Frontend directory not found: {FRONTEND_DIR}")

    backend = start_process(
        ["uvicorn", "agentchat.main:app", "--host", "0.0.0.0", "--port", "7860"],
        BACKEND_DIR,
    )

    time.sleep(2)

    frontend = start_process(
        ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "8090"],
        FRONTEND_DIR,
        shell=IS_WINDOWS,
    )

    print("[ready] Backend:  http://127.0.0.1:7860")
    print("[ready] Frontend: http://127.0.0.1:8090")
    print("[hint] Press Ctrl+C to stop both processes.")

    while True:
        time.sleep(1)
        if backend.poll() is not None:
            raise RuntimeError(f"Backend exited with code {backend.returncode}")
        if frontend.poll() is not None:
            raise RuntimeError(f"Frontend exited with code {frontend.returncode}")


def cleanup() -> None:
    print("[stop] Shutting down local services...")
    for process in processes:
        if process.poll() is not None:
            continue
        if IS_WINDOWS:
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            process.send_signal(signal.SIGTERM)


def main() -> int:
    parser = argparse.ArgumentParser(description="Start Zuno backend and frontend locally.")
    parser.add_argument("--install-deps", action="store_true", help="Install Python dependencies first.")
    args = parser.parse_args()

    if args.install_deps:
        install_dependencies()
    else:
        print("[deps] Skipped dependency installation. Use --install-deps when needed.")

    try:
        start_services()
    except KeyboardInterrupt:
        return 0
    finally:
        cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
