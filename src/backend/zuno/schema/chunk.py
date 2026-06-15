import hashlib


class ChunkModel:
    def __init__(
        self,
        chunk_id,
        content,
        file_id,
        file_name,
        update_time,
        knowledge_id,
        summary="",
        modality="text",
        source_url="",
        document_hash=None,
        chunk_hash=None,
        source_chunk_id=None,
    ):
        self.chunk_id = chunk_id
        self.content = content
        self.file_id = file_id
        self.file_name = file_name
        self.update_time = update_time
        self.knowledge_id = knowledge_id
        self.summary = summary
        self.modality = modality
        self.source_url = source_url
        self.source_chunk_id = source_chunk_id or chunk_id
        self.document_hash = document_hash or self._build_document_hash(
            file_id=file_id,
            file_name=file_name,
            knowledge_id=knowledge_id,
            source_url=source_url,
        )
        self.chunk_hash = chunk_hash or self._build_chunk_hash(
            chunk_id=chunk_id,
            content=content,
            document_hash=self.document_hash,
        )

    @staticmethod
    def _build_document_hash(*, file_id, file_name, knowledge_id, source_url=""):
        payload = f"{knowledge_id}|{file_id}|{file_name}|{source_url}"
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _build_chunk_hash(*, chunk_id, content, document_hash):
        payload = f"{document_hash}|{chunk_id}|{content}"
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "file_id": self.file_id,
            "file_name": self.file_name,
            "knowledge_id": self.knowledge_id,
            "update_time": self.update_time,
            "summary": self.summary,
            "modality": self.modality,
            "source_url": self.source_url,
            "source_chunk_id": self.source_chunk_id,
            "document_hash": self.document_hash,
            "chunk_hash": self.chunk_hash,
        }


__all__ = ["ChunkModel"]
