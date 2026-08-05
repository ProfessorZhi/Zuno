"""Production caller with module-qualified constructor.

``import module`` then ``module.WorkSpaceSimpleAgent(...)``. The verifier
must resolve the qualified construction to ``WorkSpaceSimpleAgent`` and
classify the candidate as ``PRODUCT_ADAPTER`` (canonical-delegate
shape) or ``UNRESOLVED`` (no-delegate shape) depending on the candidate
fixture's evidence.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions import (  # noqa: E402
    candidate_constructor,
)


def build_with_qualified_constructor(unified_runtime, model_config, user_id, session_id):
    return candidate_constructor.WorkSpaceSimpleAgent(
        unified_runtime=unified_runtime,
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
