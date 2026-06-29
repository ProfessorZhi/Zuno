import hashlib
import os


def build_source_chunk_id(*, file_id: str, file_name: str, index: int, prefix: str | None = None) -> str:
    base_prefix = prefix or os.path.basename(file_name).split("_")[0] or "chunk"
    return f"{base_prefix}_{file_id}_{index}"[:128]


def build_chunk_id(*, file_id: str, file_name: str, content: str, index: int, prefix: str | None = None) -> str:
    base_prefix = prefix or os.path.basename(file_name).split("_")[0] or "chunk"
    fingerprint = hashlib.sha1(
        f"{file_id}|{file_name}|{index}|{content}".encode("utf-8")
    ).hexdigest()[:32]
    return f"{base_prefix}_{fingerprint}"[:128]


__all__ = ["build_chunk_id", "build_source_chunk_id"]
