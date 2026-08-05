"""AgentControlRuntime fixture with NO production caller.

The verifier must classify it as ``INTERNAL_TEST_HARNESS``: the class
exists but no Production Entry Point can construct or invoke it. Its
methods still contain ``trace_events`` / ``final_answer`` style legacy
attributes, but those are dead code because there is no production
caller that drives them.

This file exists purely as a verifier fixture. It is NOT imported by
production code.
"""


class AgentControlRuntime:
    def __init__(self, *, memory_engine=None, required_citation_coverage=0.8):
        self._memory_engine = memory_engine
        self._required_citation_coverage = required_citation_coverage

    def run(self, planner_output, *, observations=()):
        trace_events = list(planner_output.trace_events)
        capability_plan = planner_output.capability_plan
        return {
            "task_id": planner_output.task_id,
            "trace_id": planner_output.trace_id,
            "trace_events": trace_events,
            "capability_plan": capability_plan,
            "final_answer": planner_output.final_answer or "",
        }