"""Expired flag reader fixture — yaml.safe_load + expires_at comparison.

The verifier must detect this as a dual-path blocker because it shows
a feature flag reader that loads from YAML and checks ``expires_at``.
"""

import yaml


def _now():
    import datetime
    return datetime.datetime.now()


def read_flag(path):
    """Read a feature flag and check whether it has expired."""
    with open(path, "r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp)
    if data["expires_at"] < _now():
        return False
    return data.get("enabled", False)
