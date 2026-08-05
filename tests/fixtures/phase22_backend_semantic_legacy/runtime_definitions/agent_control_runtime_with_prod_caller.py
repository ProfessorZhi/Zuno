"""AgentControlRuntime fixture WITH a production caller.

The production caller file
``tests/fixtures/phase22_backend_semantic_legacy/production_callers/caller_of_agent_control.py``
constructs this class. The verifier must classify it as
``PRODUCT_LEGACY_RUNTIME`` (BLOCKED) because a Production Entry Point
can reach it.
"""


class AgentControlRuntime:
    def __init__(self, *, memory_engine=None):
        self._memory_engine = memory_engine

    def run(self, planner_output, *, observations=()):
        return {
            "task_id": planner_output.task_id,
            "trace_events": list(planner_output.trace_events),
            "final_answer": planner_output.final_answer or "",
        }