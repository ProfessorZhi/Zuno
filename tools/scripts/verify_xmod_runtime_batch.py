from __future__ import annotations

from pathlib import Path

from zuno.platform.contracts import (
    CrossModuleRuntimeBatchError,
    validate_cross_module_runtime_batch_from_repo,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        report = validate_cross_module_runtime_batch_from_repo(REPO_ROOT)
    except CrossModuleRuntimeBatchError as exc:
        print("XMOD runtime batch verification failed.")
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "XMOD runtime batch verification passed: "
        f"{len(report.requirement_ids)} requirements, "
        f"{report.contract_count} contracts, "
        f"{report.failure_code_count} failure codes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
