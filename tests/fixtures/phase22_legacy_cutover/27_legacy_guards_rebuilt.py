"""Contract fixture 27: rebuilt ``tests/legacy_guards`` placeholder.

The historical ``tests/legacy_guards/`` directory was retired in
PHASE22. This fixture file is intentionally placed in the
``tests/fixtures/phase22_legacy_cutover/`` tree (not the production
``tests/legacy_guards/`` location) so the audit does not surface a
finding for the rebuilt suite.

The audit forbids any reintroduction of the ``tests/legacy_guards``
directory itself.
"""