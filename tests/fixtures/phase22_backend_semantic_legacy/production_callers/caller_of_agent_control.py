"""Production caller fixture for AgentControlRuntime.

This fixture represents a Production Entry Point that constructs the
``AgentControlRuntime`` defined in
``runtime_definitions/agent_control_runtime_with_prod_caller.py``. The
verifier must use this construction site to classify the runtime as
``PRODUCT_LEGACY_RUNTIME`` (BLOCKED).

This file exists purely as a verifier fixture. It is NOT imported by
production code.
"""


from .runtime_definitions.agent_control_runtime_with_prod_caller import AgentControlRuntime  # noqa: E402


def drive_runtime(planner_output):
    return AgentControlRuntime().run(planner_output)