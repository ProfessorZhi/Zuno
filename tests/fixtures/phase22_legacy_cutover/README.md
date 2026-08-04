# Phase22 Legacy Cutover Audit (V2) — Contract Fixtures

The V2 verifier under ``tools/scripts/verify_phase22_final_legacy_cutover.py``
keeps the contract fixtures inline in
``tests/repo/test_phase22_final_legacy_cutover.py`` so that each test
constructs its own minimal repository tree under ``tmp_path``. This
directory is the fixture scratch space; it carries shared templating
notes only.

## Covered scenarios (one per test)

1.  Clean canonical fixture
2.  Phase08 ``_fallback_to_legacy``
3.  ``legacy_runner`` injection via composition root
4.  rollback mode
5.  shadow legacy-primary
6.  canary legacy-shadow
7.  Automatic fallback to legacy on new-runtime exception
8.  Public Adapter direct DAO/Repository write
9.  Public Adapter routing through Application Service
10. Old ``zuno.<legacy>`` import
11. Dynamic ``importlib.import_module`` legacy import
12. ``sys.meta_path`` hook
13. ``sys.modules`` wholesale alias
14. ``try canonical / except ImportError`` legacy fallback
15. TypeScript legacy API path
16. Shell legacy runtime env selector
17. Workflow legacy command
18. ``dual_read=`` marker in production source
19. ``dual_write=`` marker in production source
20. Expired but not retired feature flag
21. Retired feature flag with no runtime reader
22. Dynamic callout that cannot be statically resolved
23. History document with legacy narrative (allowed)
24. Evidence false ``CLEAN`` claim (noted, never gating)
25. Product API still reaching ``GeneralAgent`` (runtime blocker)
26. ``tests/legacy_guards`` re-introduction
27. CLI status table
28. Re-introduction of ``legacy_aliases.py``
