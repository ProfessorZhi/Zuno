from __future__ import annotations

from copy import deepcopy


def snapshot_state(state: dict) -> dict:
    return deepcopy(state)
