from __future__ import annotations

from zuno.knowledge.ingestion.runtime_batch import (
    InputRuntimeBatchError,
    validate_input_runtime_batch,
)


def main() -> int:
    try:
        report = validate_input_runtime_batch()
    except InputRuntimeBatchError as exc:
        print("Input runtime batch verification failed.")
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Input runtime batch verification passed: "
        f"{len(report.requirement_ids)} requirements, "
        f"source_verified={report.source_verified}, "
        f"parse={report.parse_status}, "
        f"blocked={report.blocked_status}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
