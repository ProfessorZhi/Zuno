from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from zuno.platform.contracts.canonical import canonical_sha256, schema_sha256


class ContractVersion(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    major: int = Field(ge=1)
    minor: int = Field(ge=0)

    @classmethod
    def parse(cls, value: str) -> "ContractVersion":
        parts = value.split(".")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            raise ValueError(f"unsupported contract version format: {value}")
        return cls(major=int(parts[0]), minor=int(parts[1]))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

    def supports(self, requested: "ContractVersion") -> bool:
        return self.major == requested.major and self.minor >= requested.minor


class ContractRegistryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    contract_name: str
    version: ContractVersion
    schema_hash: str
    owner_module: str
    producer_modules: tuple[str, ...] = ()
    consumer_modules: tuple[str, ...] = ()
    compatibility: Literal["CURRENT_MAJOR", "READ_MINOR", "ADAPTER_REQUIRED", "REJECT"] = "CURRENT_MAJOR"
    fixture_ref: str | None = None

    @field_validator("contract_name", "owner_module")
    @classmethod
    def _not_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("contract registry fields cannot be empty")
        return value


class ContractBundleManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    bundle_name: str = "zuno-wave1-cross-module-contracts"
    bundle_version: str = "2026.07.wave1"
    entries: tuple[ContractRegistryEntry, ...]
    bundle_hash: str


class ContractRegistry:
    def __init__(self, entries: list[ContractRegistryEntry] | tuple[ContractRegistryEntry, ...]) -> None:
        self._entries: dict[tuple[str, int, int], ContractRegistryEntry] = {}
        self._latest: dict[str, ContractRegistryEntry] = {}
        for entry in entries:
            key = (entry.contract_name, entry.version.major, entry.version.minor)
            if key in self._entries:
                raise ValueError(f"duplicate contract version: {entry.contract_name} {entry.version}")
            for existing in self._entries.values():
                if (
                    existing.contract_name == entry.contract_name
                    and existing.version == entry.version
                    and existing.schema_hash != entry.schema_hash
                ):
                    raise ValueError(f"same contract version has different schema hash: {entry.contract_name}")
            self._entries[key] = entry
            latest = self._latest.get(entry.contract_name)
            if latest is None or (entry.version.major, entry.version.minor) > (
                latest.version.major,
                latest.version.minor,
            ):
                self._latest[entry.contract_name] = entry

    def get(self, contract_name: str, version: str) -> ContractRegistryEntry:
        requested = ContractVersion.parse(version)
        latest = self._latest.get(contract_name)
        if latest is None:
            raise KeyError(f"unknown contract: {contract_name}")
        if latest.version.major != requested.major:
            raise ValueError(f"unsupported major version for {contract_name}: {requested.major}")
        direct = self._entries.get((contract_name, requested.major, requested.minor))
        if direct:
            return direct
        if latest.version.supports(requested):
            return latest
        raise ValueError(f"unsupported minor version for {contract_name}: {requested}")

    def manifest(self) -> ContractBundleManifest:
        entries = tuple(sorted(self._entries.values(), key=lambda item: (item.contract_name, item.version.major, item.version.minor)))
        payload = [entry.model_dump(mode="json") for entry in entries]
        return ContractBundleManifest(entries=entries, bundle_hash=canonical_sha256(payload))


def _entry(model: type[BaseModel], *, owner: str, producers: tuple[str, ...], consumers: tuple[str, ...]) -> ContractRegistryEntry:
    return ContractRegistryEntry(
        contract_name=model.__name__,
        version=ContractVersion(major=1, minor=0),
        schema_hash=schema_sha256(model),
        owner_module=owner,
        producer_modules=producers,
        consumer_modules=consumers,
        fixture_ref=f"tests/contracts/fixtures/{model.__name__}.json",
    )


def build_wave1_contract_registry() -> ContractRegistry:
    from zuno.platform.contracts.shared import (
        ActionExecutionBindingV1,
        ActionProposalV1,
        AuditPersistenceReceiptV1,
        CrossModuleEnvelopeV1,
        EffectiveSecurityEpochRefV1,
        EffectReceiptV1,
        EffectReconciliationV1,
        FailureCodeV1,
        IndexWriteBatchV1,
        IndexWriteReceiptV1,
        ModelUsageReceiptV1,
        PreparedToolActionV1,
        PrincipalContextRefV1,
        SecurityApprovalDecisionV1,
        SecurityContextRefV1,
        ToolObservationV1,
        WriteVisibilityReceiptV1,
    )

    return ContractRegistry(
        [
            _entry(CrossModuleEnvelopeV1, owner="Infrastructure", producers=("ALL",), consumers=("ALL",)),
            _entry(PrincipalContextRefV1, owner="Security", producers=("Security",), consumers=("ALL",)),
            _entry(SecurityContextRefV1, owner="Security", producers=("Security",), consumers=("ALL",)),
            _entry(EffectiveSecurityEpochRefV1, owner="Security", producers=("Security",), consumers=("ALL",)),
            _entry(SecurityApprovalDecisionV1, owner="Security", producers=("Security",), consumers=("Tool Runtime", "Agent Core", "Product Surface")),
            _entry(AuditPersistenceReceiptV1, owner="Infrastructure", producers=("Infrastructure",), consumers=("Security", "Observability", "Tool Runtime")),
            _entry(FailureCodeV1, owner="Shared Contract Governance", producers=("ALL",), consumers=("ALL",)),
            _entry(ModelUsageReceiptV1, owner="Model Gateway", producers=("Model Gateway",), consumers=("Agent Core", "Observability")),
            _entry(IndexWriteBatchV1, owner="Knowledge/Memory", producers=("Knowledge", "Memory"), consumers=("Infrastructure",)),
            _entry(IndexWriteReceiptV1, owner="Infrastructure", producers=("Infrastructure",), consumers=("Knowledge", "Memory")),
            _entry(WriteVisibilityReceiptV1, owner="Infrastructure", producers=("Infrastructure",), consumers=("Knowledge", "Memory")),
            _entry(ActionProposalV1, owner="Agent Core", producers=("Agent Core",), consumers=("Tool Runtime",)),
            _entry(ActionExecutionBindingV1, owner="Agent Core", producers=("Agent Core",), consumers=("Agent Core", "Tool Runtime")),
            _entry(PreparedToolActionV1, owner="Tool Runtime", producers=("Tool Runtime",), consumers=("Security", "Agent Core")),
            _entry(ToolObservationV1, owner="Tool Runtime", producers=("Tool Runtime",), consumers=("Agent Core", "Observability")),
            _entry(EffectReceiptV1, owner="Tool Runtime", producers=("Tool Runtime",), consumers=("Agent Core", "Observability")),
            _entry(EffectReconciliationV1, owner="Tool Runtime", producers=("Tool Runtime",), consumers=("Agent Core", "Observability")),
        ]
    )
