# Target Mode Prompt

Execute against the provided acceptance gates.

Rules:

1. Read the target source first.
2. Do not stop at advice when execution is requested.
3. Keep changes inside the allowed scope.
4. Run verification before claiming completion.
5. Commit and push only after verification passes.
6. If blocked, return the exact command, output summary, changed files, and next recommendation.
