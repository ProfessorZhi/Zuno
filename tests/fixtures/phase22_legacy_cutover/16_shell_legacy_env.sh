#!/usr/bin/env bash
# Contract fixture 16: shell script referencing a legacy runtime env.
export ZUNO_AGENT_RUNTIME=legacy_general_agent
exec python -m zuno.legacy_runtime --mode=rollback