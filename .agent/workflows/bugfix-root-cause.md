# Bugfix Root Cause Workflow

## Trigger

Use when a test, script, runtime flow, or document gate fails.

## Steps

1. Capture the failing command and exact output.
2. Identify whether the failure is code, docs, verification drift, environment,
   or stale expectation.
3. Trace the root cause before patching.
4. Add or update the smallest test that protects the corrected behavior.
5. Rerun the original failing command.

## Stop Conditions

- Fixing requires forbidden runtime scope.
- Evidence is insufficient to know whether docs or code are wrong.
