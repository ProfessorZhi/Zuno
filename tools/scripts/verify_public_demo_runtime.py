from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = REPO_ROOT / "src" / "backend"
BACKEND_ROOT = REPO_ROOT / "src/backend"
for runtime_root in (str(BACKEND_ROOT),):
    if runtime_root not in sys.path:
        sys.path.insert(0, runtime_root)

from zuno.evals.contract_review_eval.run_contract_eval import run


def _validate_result(payload: dict, report_root: Path) -> list[str]:
    errors: list[str] = []

    if payload.get("status") != "ok":
        errors.append(f"unexpected status: {payload.get('status')}")
    if payload.get("profile") != "dev_offline":
        errors.append(f"unexpected profile: {payload.get('profile')}")

    sample_count = int(payload.get("sample_count") or 0)
    report_count = int(payload.get("report_count") or 0)
    results = list(payload.get("results") or [])

    if sample_count <= 0:
        errors.append("sample_count must be positive")
    if report_count != sample_count:
        errors.append(f"report_count should equal sample_count, got {report_count} vs {sample_count}")
    if len(results) != sample_count:
        errors.append(f"results length should equal sample_count, got {len(results)} vs {sample_count}")

    for result in results:
        report_path = Path(str(result.get("report_path") or ""))
        if not report_path:
            errors.append(f"{result.get('id')} missing report_path")
            continue
        if not report_path.exists():
            errors.append(f"{result.get('id')} report missing: {report_path}")
            continue
        if report_root not in report_path.parents:
            errors.append(f"{result.get('id')} report_path outside temp output: {report_path}")

        report_text = report_path.read_text(encoding="utf-8")
        if "Contract Review Report Template" not in report_text:
            errors.append(f"{result.get('id')} report missing report template marker")
        if "Clause -> CLAUSE_HAS_RISK" not in report_text:
            errors.append(f"{result.get('id')} report missing expected graph-path evidence")

        if int(result.get("citation_count") or 0) <= 0:
            errors.append(f"{result.get('id')} citation_count should be positive")
        if int(result.get("path_count") or 0) <= 0:
            errors.append(f"{result.get('id')} path_count should be positive")
        if int(result.get("trace_node_count") or 0) <= 0:
            errors.append(f"{result.get('id')} trace_node_count should be positive")
        if str(result.get("profile_extraction_mode") or "") != "fixture":
            errors.append(f"{result.get('id')} profile_extraction_mode should be fixture")

    return errors


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="zuno-public-demo-smoke-") as temp_dir:
        report_root = Path(temp_dir)
        payload = asyncio.run(run("dev_offline", output_dir=report_root))
        errors = _validate_result(payload, report_root)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("public demo runtime verification failed.")
        return 1

    print("public demo runtime verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

