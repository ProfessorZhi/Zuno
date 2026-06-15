from zuno.services.capability_registry import CapabilityRegistryService


class CapabilityService:
    @staticmethod
    async def search_capabilities(
        query: str,
        *,
        user_id: str,
        kind: str = "",
        limit: int = 8,
    ) -> list[dict]:
        return await CapabilityRegistryService.search(
            query,
            user_id=user_id,
            kind=kind,
            limit=limit,
        )


__all__ = ["CapabilityService"]
