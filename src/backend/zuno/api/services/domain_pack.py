from __future__ import annotations

from pathlib import Path
from typing import Any

from zuno.services.domain_pack.loader import DomainPackLoader


class DomainPackService:
    @staticmethod
    def _pack_status(pack_dir: Path) -> str:
        return "published" if (pack_dir / "pack.yaml").exists() else "draft"

    @classmethod
    async def list_domain_packs(cls) -> list[dict[str, Any]]:
        loader = DomainPackLoader()
        results: list[dict[str, Any]] = []
        for pack_dir in sorted(loader.packs_root.iterdir() if loader.packs_root.exists() else []):
            if not pack_dir.is_dir():
                continue
            try:
                pack = loader.load(pack_dir.name)
            except Exception:
                results.append(
                    {
                        "pack_id": pack_dir.name,
                        "name": pack_dir.name,
                        "status": "draft",
                    }
                )
                continue

            results.append(
                {
                    "pack_id": pack.id,
                    "name": pack.name,
                    "version": pack.version,
                    "description": pack.description,
                    "status": cls._pack_status(pack_dir),
                }
            )
        return results

    @classmethod
    async def publish_domain_pack(cls, pack_id: str) -> dict[str, Any]:
        pack = DomainPackLoader().load(pack_id)
        if pack is None:
            raise ValueError(f"domain pack not found: {pack_id}")
        return {
            "pack_id": pack.id,
            "status": "published",
            "version": pack.version,
            "name": pack.name,
        }


__all__ = ["DomainPackService"]
