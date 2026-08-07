"""PHASE22 (Slice B) — positive fixture: file rename that the verifier
CANNOT statically prove must surface AUDIT_UNRESOLVED.

A file rename is not detectable from the AST alone: the verifier
cannot distinguish a renamed file from an originally-named file. The
hardened detector therefore treats any "ambiguous-shape" file — one
whose name does not match the canonical executor adapter naming
contract but whose body shows a direct tool / model invocation chain
WITHOUT a specific bypass pattern — as AUDIT_UNRESOLVED. The verifier
must fail-closed: it cannot prove the file is a renamed legacy /
bypass surface, so the audit must report AUDIT_UNRESOLVED rather than
CLEAN.

The class name deliberately does NOT include ``Adapter`` /
``RuntimeAdapter`` / ``Engine`` so the existing name-coupled
exemption does not apply. The call site uses a dynamic ``getattr``
dispatch so the existing name-coupled detectors do not produce a
specific ``tool_bypass_*`` finding — only the unresolved_file_rename
shape concern remains.
"""


class FileRenamedWorker:
    """Worker whose original file name is unknown. The verifier cannot
    statically prove this file is not a renamed legacy / bypass
    surface; the audit must surface AUDIT_UNRESOLVED."""

    def __init__(self, *, tool, name):
        self._tool = tool
        self._name = name

    async def run(self, payload):
        # Dynamic dispatch via ``getattr`` cannot be statically proven
        # to resolve to a canonical executor adapter. Combined with a
        # non-canonical file name, the verifier surfaces AUDIT_UNRESOLVED.
        method = getattr(self._tool, self._name)
        return await method(payload)