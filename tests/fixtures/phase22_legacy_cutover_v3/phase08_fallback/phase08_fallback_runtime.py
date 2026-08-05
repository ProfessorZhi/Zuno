"""Phase08 legacy fallback fixture — ``legacy_phase08_agent`` symbol
reachable. The verifier must report this as a legacy_runtime blocker.
"""


class Phase08LegacyRuntime:
    """The legacy phase08 runtime that must be retired."""

    def run(self, state):
        return {"legacy": True, "state": state}


def legacy_phase08_agent(state):
    """Public entry point to the legacy phase08 runtime."""
    return Phase08LegacyRuntime().run(state)
