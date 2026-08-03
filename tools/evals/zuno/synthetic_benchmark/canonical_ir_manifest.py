from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json
from tools.evals.zuno.synthetic_benchmark.source_upload_manifest import (
    build_source_upload_manifest,
)


@dataclass
class CanonicalIrManifestValidation:
    passed: bool
    errors: list[str] = field(default_factory=list)
    document_count: int = 0
    chunk_count: int = 0
    entity_count: int = 0
    relation_count: int = 0
    canonical_ir_hash: str | None = None


ENTITY_ALIASES = {
    "Axis-9 Industrial Controller v9.4.0": "product:Axis-9 Industrial Controller v9.4.0",
    "Haruto Soma": "person:Haruto Soma",
    "Auroralis": "org:Auroralis",
    "Kjartan Eliasson": "person:Kjartan Eliasson",
    "Automation Systems": "org:Automation Systems",
    "Iris Vange": "person:Iris Vange",
    "Lukas Wenger": "person:Lukas Wenger",
    "Solveig Hagen": "person:Solveig Hagen",
    "Information Security Policy v4.2": "policy:Information Security Policy v4.2",
    "Information Security Policy v4.1": "policy:Information Security Policy v4.1",
    "Project Northwind": "project:Northwind",
    "Northwind SDK v3.0.0": "product:Northwind SDK v3.0.0",
    "Amani Bello": "person:Amani Bello",
    "Forge-X1": "product:Forge-X1",
    "Nadya Soroka": "person:Nadya Soroka",
}

RELATION_RULES = (
    ("Project Northwind", "Northwind SDK v3.0.0", "project_delivers_product"),
    ("Kjartan Eliasson", "Project Northwind", "person_sponsors_project"),
    ("Haruto Soma", "Axis-9 Industrial Controller v9.4.0", "person_released_product"),
    ("Haruto Soma", "Northwind SDK v3.0.0", "person_released_product"),
    ("Information Security Policy v4.2", "Information Security Policy v4.1", "policy_supersedes_policy"),
    ("Nadya Soroka", "Forge-X1", "person_issued_corrective_action"),
)


def _paragraph_chunks(body: str) -> list[str]:
    return [chunk.strip() for chunk in body.split("\n\n") if chunk.strip()]


def _entities_for_text(text: str, *, document_id: str, chunk_id: str) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    for label, entity_ref in ENTITY_ALIASES.items():
        if label in text:
            entities.append(
                {
                    "entity_id": f"entity::{entity_ref}",
                    "entity_ref": entity_ref,
                    "label": label,
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                }
            )
    return entities


def _relations_for_document(document_id: str, chunk_ids_by_label: dict[str, str]) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    for from_label, to_label, kind in RELATION_RULES:
        if from_label not in chunk_ids_by_label or to_label not in chunk_ids_by_label:
            continue
        relations.append(
            {
                "relation_id": f"relation::{kind}::{ENTITY_ALIASES[from_label]}::{ENTITY_ALIASES[to_label]}",
                "kind": kind,
                "from": ENTITY_ALIASES[from_label],
                "to": ENTITY_ALIASES[to_label],
                "direction": "outbound",
                "document_id": document_id,
                "evidence_chunk_ids": sorted(
                    {chunk_ids_by_label[from_label], chunk_ids_by_label[to_label]}
                ),
            }
        )
    return relations


def build_canonical_ir_manifest(corpus_root: Path) -> dict[str, Any]:
    source_manifest = build_source_upload_manifest(corpus_root)
    documents: list[dict[str, Any]] = []
    chunks: list[dict[str, Any]] = []
    entities_by_id: dict[str, dict[str, Any]] = {}
    relations_by_id: dict[str, dict[str, Any]] = {}

    sources_by_doc = {source["document_id"]: source for source in source_manifest["sources"]}
    for path in sorted(corpus_root.glob("*.md")):
        document_id = path.stem
        source = sources_by_doc[document_id]
        body = path.read_text(encoding="utf-8")
        document_version_id = f"document-version::{document_id}::{source['source_hash'][:16]}"
        documents.append(
            {
                "document_id": document_id,
                "document_version_id": document_version_id,
                "source_id": source["source_id"],
                "tenant_id": source["tenant_id"],
                "workspace_id": source["workspace_id"],
                "security_scope": source["security_scope"],
                "source_hash": source["source_hash"],
            }
        )
        chunk_ids_by_label: dict[str, str] = {}
        for index, text in enumerate(_paragraph_chunks(body), start=1):
            chunk_id = f"chunk::{document_id}::{index:03d}"
            chunk = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_version_id": document_version_id,
                "tenant_id": source["tenant_id"],
                "workspace_id": source["workspace_id"],
                "security_scope": source["security_scope"],
                "ordinal": index,
                "text_hash": sha256_json({"text": text}),
            }
            chunks.append(chunk)
            for entity in _entities_for_text(text, document_id=document_id, chunk_id=chunk_id):
                entities_by_id.setdefault(entity["entity_id"], entity)
                chunk_ids_by_label[entity["label"]] = chunk_id
        for relation in _relations_for_document(document_id, chunk_ids_by_label):
            relations_by_id.setdefault(relation["relation_id"], relation)

    manifest = {
        "schema_version": "1.0.0",
        "track_id": "machine_attested_synthetic_regression",
        "status": "CANONICAL_IR_INPUTS_PREPARED",
        "parser_runtime_executed": False,
        "postgres_facts_verified": False,
        "knowledge_version_created": False,
        "source_manifest_hash": source_manifest["source_manifest_hash"],
        "document_count": len(documents),
        "chunk_count": len(chunks),
        "entity_count": len(entities_by_id),
        "relation_count": len(relations_by_id),
        "documents": documents,
        "chunks": chunks,
        "entities": sorted(entities_by_id.values(), key=lambda item: item["entity_id"]),
        "relations": sorted(relations_by_id.values(), key=lambda item: item["relation_id"]),
    }
    manifest["canonical_ir_hash"] = sha256_json(
        {key: value for key, value in manifest.items() if key != "canonical_ir_hash"}
    )
    return manifest


def validate_canonical_ir_manifest(manifest: dict[str, Any]) -> CanonicalIrManifestValidation:
    errors: list[str] = []
    if manifest.get("track_id") != "machine_attested_synthetic_regression":
        errors.append("canonical IR manifest track_id mismatch")
    if manifest.get("status") != "CANONICAL_IR_INPUTS_PREPARED":
        errors.append("canonical IR manifest status mismatch")
    for field_name in ["parser_runtime_executed", "postgres_facts_verified", "knowledge_version_created"]:
        if manifest.get(field_name) is not False:
            errors.append(f"{field_name} must remain false before real canonical ingestion")
    documents = manifest.get("documents", [])
    chunks = manifest.get("chunks", [])
    entities = manifest.get("entities", [])
    relations = manifest.get("relations", [])
    if manifest.get("document_count") != len(documents):
        errors.append("document_count must match documents length")
    if manifest.get("chunk_count") != len(chunks):
        errors.append("chunk_count must match chunks length")
    if manifest.get("entity_count") != len(entities):
        errors.append("entity_count must match entities length")
    if manifest.get("relation_count") != len(relations):
        errors.append("relation_count must match relations length")
    if len(documents) != 8:
        errors.append("canonical IR manifest document_count must be 8")
    if not chunks:
        errors.append("canonical IR manifest must contain chunks")
    if not entities:
        errors.append("canonical IR manifest must contain entities")
    if not relations:
        errors.append("canonical IR manifest must contain relations")
    document_ids = {item.get("document_id") for item in documents if isinstance(item, dict)}
    chunk_ids = {item.get("chunk_id") for item in chunks if isinstance(item, dict)}
    entity_refs = {item.get("entity_ref") for item in entities if isinstance(item, dict)}
    for chunk in chunks:
        if chunk.get("document_id") not in document_ids:
            errors.append(f"{chunk.get('chunk_id')}: chunk document_id missing")
    for relation in relations:
        if relation.get("from") not in entity_refs:
            errors.append(f"{relation.get('relation_id')}: relation from missing entity")
        if relation.get("to") not in entity_refs:
            errors.append(f"{relation.get('relation_id')}: relation to missing entity")
        if relation.get("direction") != "outbound":
            errors.append(f"{relation.get('relation_id')}: relation direction must be outbound")
        evidence = relation.get("evidence_chunk_ids")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{relation.get('relation_id')}: relation evidence chunks missing")
        elif not set(evidence).issubset(chunk_ids):
            errors.append(f"{relation.get('relation_id')}: relation evidence chunks missing from chunks")
    expected_hash = sha256_json(
        {key: value for key, value in manifest.items() if key != "canonical_ir_hash"}
    )
    if manifest.get("canonical_ir_hash") != expected_hash:
        errors.append("canonical_ir_hash mismatch")
    return CanonicalIrManifestValidation(
        passed=not errors,
        errors=errors,
        document_count=len(documents),
        chunk_count=len(chunks),
        entity_count=len(entities),
        relation_count=len(relations),
        canonical_ir_hash=manifest.get("canonical_ir_hash"),
    )


def write_canonical_ir_manifest(out_root: Path, *, corpus_root: Path) -> dict[str, Any]:
    out_root.mkdir(parents=True, exist_ok=True)
    manifest = build_canonical_ir_manifest(corpus_root)
    validation = validate_canonical_ir_manifest(manifest)
    (out_root / "canonical_ir_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    (out_root / "canonical_ir_manifest_report.json").write_text(
        json.dumps(validation.__dict__, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return validation.__dict__


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    parser.add_argument("--corpus-root", required=True, type=Path)
    args = parser.parse_args()
    result = write_canonical_ir_manifest(args.out_root, corpus_root=args.corpus_root)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
