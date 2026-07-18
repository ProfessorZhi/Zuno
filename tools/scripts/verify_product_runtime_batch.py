from __future__ import annotations

from pathlib import Path

from zuno.product.runtime_batch import (
    ProductRuntimeBatchError,
    validate_product_runtime_batch_from_repo,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        report = validate_product_runtime_batch_from_repo(REPO_ROOT)
    except ProductRuntimeBatchError as exc:
        print("Product runtime batch verification failed.")
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Product runtime batch verification passed: "
        f"{len(report.requirement_ids)} requirements, "
        f"{report.receipt_count} receipts, "
        f"{report.stream_event_count} stream events, "
        f"{report.outcome_count} run outcomes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
