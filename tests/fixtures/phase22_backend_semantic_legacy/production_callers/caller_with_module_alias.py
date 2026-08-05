"""Production caller with module alias.

``import module as runtime_module`` then ``runtime_module.WorkSpaceSimpleAgent(...)``.
The verifier must resolve the qualified construction via the module
alias to ``WorkSpaceSimpleAgent`` and classify the candidate as
``PRODUCT_ADAPTER`` (canonical-delegate shape) or ``UNRESOLVED``
(no-delegate shape) depending on the candidate fixture's evidence.
"""

from tests.fixtures.phase22_backend_semantic_legacy.runtime_definitions import (  # noqa: E402
    candidate_constructor as runtime_module,
)


def build_with_module_alias(unified_runtime, model_config, user_id, session_id):
    return runtime_module.WorkSpaceSimpleAgent(
        unified_runtime=unified_runtime,
        model_config=model_config,
        user_id=user_id,
        session_id=session_id,
    )
