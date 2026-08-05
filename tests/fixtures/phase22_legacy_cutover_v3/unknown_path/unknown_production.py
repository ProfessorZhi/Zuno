"""Unknown path fixture — files that are not in the SCANNED_ROOTS list
must be excluded from the audit, but nothing in here should silence
findings in the actual scanned roots.

The verifier's SCANNED_ROOTS explicitly enumerates the production
surfaces. Anything outside is not scanned. This fixture exists to
document the contract.
"""


class UntrackedRuntime:
    """Reference implementation not in the scanned roots."""

    def run(self, state):
        return state
