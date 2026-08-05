"""Production caller with module-level assignment alias.

``Runtime = WorkSpaceSimpleAgent`` at module level then ``Runtime(...)``.
The verifier must resolve ``Runtime`` to ``WorkSpaceSimpleAgent`` via the
module-level assignment and classify the candidate as ``PRODUCT_ADAPTER``
(canonical-delegate shape) or ``UNRESOLVED`` (no-delegate shape)
depending on the candidate fixture's evidence.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions.candidate_constructor import (  # noqa: E402
    WorkSpaceSimpleAgent,
)


Runtime = WorkSpaceSimpleAgent


def build_with_assignment_alias(unified_runtime, model_config, user_id, session_id):
    return Runtime(
        unified_runtime=unified_runtime,
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
