# Session Transcript — rb-2026-09-13-red-calibration-015

This transcript records observable role I/O, GitHub refs/commits, Controller transitions and user intervention. It does not record or fabricate private chain-of-thought.

## Event 001 — ROUND_INIT
actor: User / Controller
stage: ROUND_INIT
input_head_sha: 0ccc1ee336c42d8ecad0bd6535a97f8fc4e6aca3
input_files:
- .agent/red-blue/protocol.md
- .agent/red-blue/attack-model.md
- user instruction captured as UF-001 / UF-002
observable_input_summary: Start a Red calibration round, stop after the first Red output, and require user inspection before any Blue execution.
observable_output_summary: Initialized Round #015 with 100-question pressure-suite capacity, 30-question Primary Path target, 70 Reserve target, REQUIRED USER_RED_REVIEW gate, and Blue blocked until approval.
output_files:
- .agent/red-blue/current.md
- 00_manifest.yaml through 08_session_transcript.md
output_commit_sha: recover from Git history after commit
next_stage: ROUND_PR_BIND
