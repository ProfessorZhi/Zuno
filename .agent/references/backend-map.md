# Backend Map

## Purpose

Orient Agents working in `src/backend/zuno`.

## Current Paths

- App entry: `src/backend/zuno/main.py`
- API layer: `src/backend/zuno/api/`
- Core/runtime: `src/backend/zuno/core/`
- Services: `src/backend/zuno/services/`
- Schemas: `src/backend/zuno/schema/`
- Database: `src/backend/zuno/database/`
- Settings: `src/backend/zuno/settings.py`

## Main Responsibilities

Routes expose HTTP boundaries. Services own use cases. Core/runtime owns
orchestration and graph behavior. Persistence belongs under database and
storage modules.

## Update Triggers

Update this map when backend package layout, route ownership, runtime call
chain, or validation commands change.

For backend architecture replacement, GraphRAG boundary, Context/Memory, or
package layout work, first read
`.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`.
