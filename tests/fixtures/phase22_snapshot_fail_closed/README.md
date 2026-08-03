# PHASE22 Snapshot Fail-Closed Gate Fixtures

This directory hosts fixture-style helpers used by the
PHASE22-SNAPSHOT-FAIL-CLOSED-GATE verifier.  The contract fixtures live
inline inside ``tools/scripts/verify_phase22_snapshot_fail_closed.py`` so
that the verifier can be exercised without touching the real repository.

Future fixtures (e.g. extra ``SnapshotPersistencePort`` test doubles, more
index-client scope scenarios) should be added here.