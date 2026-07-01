import json
from pathlib import Path


class PolicyParser:
    def parse_policy(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))


def helper(value: int) -> int:
    return value + 1
