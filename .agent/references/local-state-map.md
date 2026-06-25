# Local State Map

## Purpose

Define the only local Agent state layout.

## Current Paths

- `.agent/local/README.md`
- `.agent/local/notes/`
- `.agent/local/tmp/`
- `.agent/local/logs/`
- `.agent/local/secrets/`

## Rule

Local state stays under `.agent/local/`. Do not create sibling `.agent/notes/`,
`.agent/tmp/`, `.agent/logs/`, or `.agent/secrets/` directories.

Tracked durable Agent knowledge belongs in `.agent/references/`,
`.agent/workflows/`, `.agent/skills/`, `.agent/lessons/`, `.agent/templates/`,
or `.agent/programs/`.
