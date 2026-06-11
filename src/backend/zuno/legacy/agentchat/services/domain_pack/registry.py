from __future__ import annotations

from pathlib import Path

from agentchat.services.domain_pack.loader import DomainPackLoader


class DomainPackRegistry:
    def __init__(self, packs_root: Path | None = None):
        self.loader = DomainPackLoader(packs_root=packs_root)

    def list_pack_ids(self) -> list[str]:
        root = self.loader.packs_root
        if not root.exists():
            return []
        return sorted(path.name for path in root.iterdir() if path.is_dir() and (path / "pack.yaml").exists())

    def load_all(self) -> list[dict]:
        results: list[dict] = []
        for pack_id in self.list_pack_ids():
            pack = self.loader.load(pack_id)
            if pack:
                results.append(pack.to_dict())
        return results
