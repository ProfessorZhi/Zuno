# Contract fixture 26: evidence file that lies about being CLEAN.

> Status: LEGACY_CUTOVER_AUDIT_CLEAN
> Head SHA: 0000000000000000000000000000000000000000

This evidence file falsely claims the audit status is CLEAN while the
real verifier returns DUAL_PATH_BLOCKERS_FOUND. The verifier MUST NOT
trust the file's status declaration; it MUST walk the repository
independently.