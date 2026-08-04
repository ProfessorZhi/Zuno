# Contract fixture 25: history document describing retired legacy code.

> Status: RESOLVED_RETIRED
> Date: 2026-07-31

This history document records the retirement of the legacy runtime. It
mentions every retired token (``GeneralAgent``, ``legacy_runner``,
``_fallback_to_legacy``, ``rollback``, ``shadow``, ``canary``) and
therefore MUST NOT be treated as a production finding.

The verifier excludes ``docs/history`` (and any other path with the
``HISTORY_EXCLUDED_ROOTS`` marker) from the production scan.