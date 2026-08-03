"""PHASE22 CC-D environment probe.

This script enumerates Docker services (or local equivalents) declared in
infra/docker/docker-compose.yml and records their actual state. It writes a
structured JSON report that downstream tools and tests consume.

Hard rules (CC-D task card):

* Port reachable != write/read verified. We record reachability and
  health, but the report must clearly distinguish
  ``SERVICE_REACHABLE`` from ``SERVICE_WRITE_READ_VERIFIED``. Reaching a
  port does not flip any matrix row to PASSED.

* The probe must NEVER claim credentials or secrets; credentials are
  loaded from environment variables and redacted on output.

* Missing services do not produce fake receipts. Missing service
  snapshots appear in the report so the evidence manifest can declare
  ``NOT_RUN_DEPENDENCY_BLOCKED``.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SERVICES: tuple[dict[str, Any], ...] = (
    {
        "id": "postgres",
        "container": "zuno-postgres",
        "host": "localhost",
        "port": 5432,
        "protocol": "tcp",
        "expected_kind": "postgres_domain",
    },
    {
        "id": "redis",
        "container": "zuno-redis",
        "host": "localhost",
        "port": 6379,
        "protocol": "tcp",
        "expected_kind": "redis_optional",
    },
    {
        "id": "rabbitmq",
        "container": "zuno-rabbitmq",
        "host": "localhost",
        "port": 5672,
        "protocol": "tcp",
        "expected_kind": "queue",
    },
    {
        "id": "neo4j",
        "container": "zuno-neo4j",
        "host": "localhost",
        "port": 7687,
        "protocol": "tcp",
        "expected_kind": "knowledge_index",
    },
    {
        "id": "minio",
        "container": "zuno-minio",
        "host": "localhost",
        "port": 9000,
        "protocol": "http",
        "expected_kind": "object_store",
    },
    {
        "id": "milvus",
        "container": "zuno-milvus",
        "host": "localhost",
        "port": 19530,
        "protocol": "tcp",
        "expected_kind": "knowledge_index",
    },
    {
        "id": "elasticsearch",
        "container": "zuno-elasticsearch",
        "host": "localhost",
        "port": 9200,
        "protocol": "http",
        "expected_kind": "knowledge_index",
    },
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _tcp_reachable(host: str, port: int, timeout: float) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _http_head(url: str, timeout: float) -> dict[str, Any]:
    import urllib.request

    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "reachable": True,
                "status": response.status,
                "server": response.headers.get("Server", ""),
            }
    except Exception as exc:  # noqa: BLE001 - probe only, surface the error
        return {"reachable": False, "error": str(exc)}


def _docker_inspect(container: str) -> dict[str, Any]:
    if shutil.which("docker") is None:
        return {"docker_available": False}
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{.State.Health.Status}}|{{.Config.Image}}", container],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return {
            "docker_available": True,
            "container_reachable": False,
            "stderr": result.stderr.strip(),
        }
    payload = result.stdout.strip()
    if "|" not in payload:
        return {"docker_available": True, "container_reachable": True, "raw": payload}
    health, image = payload.split("|", 1)
    return {
        "docker_available": True,
        "container_reachable": True,
        "health": health,
        "image": image,
    }


def _redact(value: str) -> str:
    if not value:
        return value
    lowered = value.lower()
    for keyword in ("password", "secret", "token", "key"):
        if keyword in lowered:
            return "***REDACTED***"
    return value


def probe_service(service: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    record: dict[str, Any] = {
        "id": service["id"],
        "expected_kind": service["expected_kind"],
        "host": service["host"],
        "port": service["port"],
        "protocol": service["protocol"],
    }
    container_meta = _docker_inspect(service["container"])
    record["docker"] = container_meta
    reachable = _tcp_reachable(service["host"], service["port"], timeout)
    record["service_reachable"] = reachable
    record["service_write_read_verified"] = False  # always false from probe
    if service["protocol"] == "http":
        http = _http_head(f"http://{service['host']}:{service['port']}/", timeout)
        record["http"] = http
        if http.get("reachable"):
            record["service_write_read_verified"] = False  # http reach != write/read
    record["probe_state"] = (
        "SERVICE_REACHABLE" if reachable else "SERVICE_UNREACHABLE"
    )
    return record


def probe_all(timeout: float) -> dict[str, Any]:
    services = [probe_service(svc, timeout=timeout) for svc in DEFAULT_SERVICES]
    return {
        "probe_kind": "phase22_cc_d_environment",
        "probe_version": "1.0.0",
        "captured_at": _utc_now_iso(),
        "host": os.environ.get("HOSTNAME", socket.gethostname()),
        "python_version": sys.version.split()[0],
        "docker_compose_file": "infra/docker/docker-compose.yml",
        "services": services,
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PHASE22 CC-D environment probe")
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / "docs"
        / "evidence"
        / "goal05-phase22-machine-attested-synthetic-regression"
        / "minimax2-cc-d"
        / "environment_probe.json",
    )
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument(
        "--service",
        choices=tuple(s["id"] for s in DEFAULT_SERVICES),
        help="Restrict probe to a single service id (used by matrix rows).",
    )
    parser.add_argument(
        "--expect",
        choices=("reachable", "unreachable"),
        default="unreachable",
        help="Expected state for --service; mismatch is a hard failure.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.expect not in {"reachable", "unreachable"}:
        print(f"ERROR: invalid --expect value {args.expect!r}", file=sys.stderr)
        return 2
    if args.service is not None and not any(
        s["id"] == args.service for s in DEFAULT_SERVICES
    ):
        print(f"ERROR: unknown service {args.service}", file=sys.stderr)
        return 2
    report = probe_all(args.timeout)
    if args.service is not None:
        keep = [s for s in report["services"] if s["id"] == args.service]
        report["services"] = keep
        if not keep:
            print(f"ERROR: unknown service {args.service}", file=sys.stderr)
            return 2
        only = keep[0]
        write_report(report, args.output)
        actual_reachable = bool(only["service_reachable"])
        expectation_matched = (
            (args.expect == "reachable" and actual_reachable)
            or (args.expect == "unreachable" and not actual_reachable)
        )
        if expectation_matched:
            print(f"wrote environment probe report: {args.output.as_posix()}")
            return 0
        # Expectation mismatch is a hard failure (exit 1). Port reachable
        # != write/read verified, so we still always set
        # ``service_write_read_verified = false`` in the probe record; the
        # mismatch exit only signals that the expected fault was not (or
        # was) induced.
        print(
            f"ERROR: expectation mismatch for {args.service} "
            f"(expect={args.expect}, actual={'reachable' if actual_reachable else 'unreachable'}); "
            "port reachable != write/read verified; matrix row stays "
            "NOT_RUN_DEPENDENCY_BLOCKED until DeepSeek CC-B receipts land.",
            file=sys.stderr,
        )
        return 1
    write_report(report, args.output)
    print(f"wrote environment probe report: {args.output.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())