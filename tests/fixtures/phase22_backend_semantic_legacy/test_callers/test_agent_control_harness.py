"""Test-only caller fixture for AgentControlRuntime.

The verifier must treat this file as non-production: a path under
``tests/`` is excluded from the production reachability scan. The
verifier must classify
``runtime_definitions/agent_control_runtime_no_prod_caller.py`` as
``INTERNAL_TEST_HARNESS`` because the only callers live here.
"""

from ..runtime_definitions.agent_control_runtime_no_prod_caller import AgentControlRuntime  # noqa: E402


def drive_in_test(planner_output):
    return AgentControlRuntime().run(planner_output)