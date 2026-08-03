# PHASE22 Object Store Owner Binding Fixtures

This directory hosts test doubles used by the PHASE22-OBJECT-STORE-OWNER-GATE.
Each fixture is a non-production helper and is **not** counted toward the
production owner by the Fail-closed Object Store Owner Binding Gate.

| File | Role | Production? |
|------|------|-------------|
| `fake_object_store.py` | Test Double | No |

The fixture exists so the gate has a stable file path to anchor its
Test-Double role classification without depending on transient test code.