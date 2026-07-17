from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_phase04_rabbitmq_out_of_order_verifier() -> None:
    result = subprocess.run(
        ["python", "tools/scripts/verify_phase04_rabbitmq_out_of_order.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
