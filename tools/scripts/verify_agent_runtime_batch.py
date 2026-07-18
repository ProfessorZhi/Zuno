from __future__ import annotations

from zuno.agent.runtime_batch import (
    AgentRuntimeBatchError,
    validate_agent_runtime_batch,
)


def main() -> int:
    try:
        report = validate_agent_runtime_batch()
    except AgentRuntimeBatchError as exc:
        print("Agent runtime batch verification failed.")
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    print(
        "Agent runtime batch verification passed: "
        f"{len(report.requirement_ids)} requirements, "
        f"{report.node_count} runtime nodes, "
        f"{report.step_count} step runs, "
        f"{report.reconciler_count} reconcilers."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
