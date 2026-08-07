"""Stub helper module for the import-alias positive fixture.

Used by ``positive_import_alias.py`` to verify the verifier handles
``from x import y as alias`` patterns correctly.
"""


class RenamedInvoker:
    """A minimal stand-in for a tool / model object that exposes ainvoke."""

    async def ainvoke(self, args):
        return args
